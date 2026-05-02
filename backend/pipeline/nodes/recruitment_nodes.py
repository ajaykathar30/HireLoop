import uuid
import operator
import asyncio
from typing import List, Annotated, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_, not_
from datetime import datetime, timezone, timedelta
from langchain_core.runnables import RunnableConfig

from models.job import Job
from models.application import Application
from models.candidate import Candidate
from models.interview import InterviewSession
from models.notification import Notification

from pipeline.agents.resume_parser import parse_resume
from pipeline.agents.fit_scorer import score_fit
from pipeline.agents.mcp_bridge import get_mcp_scores
from pipeline.ranking import rank_candidates_by_similarity

# State Definition
class PipelineState(TypedDict):
    job_id: uuid.UUID
    application_ids: List[uuid.UUID]
    top_candidate_ids: List[uuid.UUID]
    logs: Annotated[List[str], operator.add]

async def fetch_applications_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: fetch_applications_node ---")
    db = config["configurable"].get("db")
    job_id = state["job_id"]
    
    # Atomically check and set pipeline_triggered to prevent race conditions
    job = await db.get(Job, job_id)
    if job.pipeline_triggered:
        return {"application_ids": [], "logs": ["Pipeline already triggered for this job. Skipping."]}
    job.pipeline_triggered = True
    db.add(job)
    await db.commit()
    
    stmt = select(Application).where(and_(Application.job_id == job_id, Application.status == "applied"))
    result = await db.execute(stmt)
    apps = result.scalars().all()
    app_ids = [app.id for app in apps]
    return {"application_ids": app_ids, "logs": [f"Fetched {len(app_ids)} applications"]}

async def parse_resumes_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: parse_resumes_node ---")
    db = config["configurable"].get("db")
    for app_id in state["application_ids"]:
        app = await db.get(Application, app_id)
        if app:
            await parse_resume(str(app.candidate_id), db)
            app.status = "screening"
            db.add(app)
    await db.commit()
    return {"logs": ["Resumes parsed"]}

async def rank_candidates_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: rank_candidates_node ---")
    db = config["configurable"].get("db")
    top_20_ids = await rank_candidates_by_similarity(state["job_id"], db)
    reject_stmt = select(Application).where(and_(Application.job_id == state["job_id"], Application.status == "screening", not_(Application.id.in_(top_20_ids))))
    result = await db.execute(reject_stmt)
    for app in result.scalars().all():
        app.status = "rejected"
        db.add(app)
    await db.commit()
    return {"top_candidate_ids": top_20_ids, "logs": [f"Ranked top {len(top_20_ids)}"]}

async def score_fit_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: score_fit_node ---")
    db = config["configurable"].get("db")
    job = await db.get(Job, state["job_id"])
    
    stmt = select(Application, Candidate).join(Candidate).where(Application.id.in_(state["top_candidate_ids"]))
    result = await db.execute(stmt)
    apps_candidates = result.all()
    
    if not apps_candidates:
        return {"logs": ["No candidates to score."]}

    # We use a semaphore to limit parallel browser-based GitHub analysis
    semaphore = asyncio.Semaphore(2) 
    
    async def process_candidate(app, candidate):
        async with semaphore:
            print(f"[SCORE] Starting analysis for candidate: {candidate.id}")
            # 1. Resume Match Score (0-100)
            fit_result = await score_fit(candidate.resume_text, job.description, job.requirements)
            resume_score = fit_result.score
            
            # 2. GitHub Scores (0-10)
            mcp_results = await get_mcp_scores(candidate.resume_url)
            github_score = mcp_results["github_score"] * 10  # Scale to 0-100
            
            # 3. Calculate Weighted Unified Score
            final_score = (resume_score * 0.50) + (github_score * 0.50)
            
            app.fit_score = int(final_score)
            app.fit_reasoning = (
                f"Unified Score: {int(final_score)}/100. "
                f"(Resume: {resume_score}, Git: {int(github_score)}). "
                f"Analysis: {fit_result.reasoning}"
            )
            print(f"[SCORE] Finished candidate: {candidate.id} | Score: {int(final_score)}")
            return app

    print(f"[SCORE] Processing {len(apps_candidates)} candidates in parallel (limit: 2)...")
    tasks = [process_candidate(app, candidate) for app, candidate in apps_candidates]
    scored_apps = await asyncio.gather(*tasks)
    
    for app in scored_apps:
        db.add(app)
        
    await db.commit()
    print("[SCORE] All candidates scored and committed.")
    return {"logs": [f"Unified Scoring complete for {len(scored_apps)} candidates"]}


async def finalize_recruitment_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: finalize_recruitment_node ---")
    db = config["configurable"].get("db")
    job_id = state["job_id"]
    job = await db.get(Job, job_id)
    
    # Fetch apps that were screened and have fit scores
    stmt = select(Application).where(and_(Application.job_id == job_id, Application.status == "screening")).order_by(Application.fit_score.desc())
    result = await db.execute(stmt)
    scored_apps = result.scalars().all()
    
    print(f"[FINALIZE] Found {len(scored_apps)} scored applications to process.")
    
    top_n = job.max_shortlist or 5
    now_utc = datetime.now(timezone.utc)
    
    for i, app in enumerate(scored_apps):
        if i < top_n:
            print(f"[FINALIZE] Shortlisting Application: {app.id}")
            app.status = "shortlisted"
            app.shortlisted_at = now_utc
            app.interview_deadline = now_utc + timedelta(hours=24)
            
            session = InterviewSession(
                application_id=app.id, 
                status="pending", 
                deadline_at=app.interview_deadline
            )
            db.add(session)
            
            cand = await db.get(Candidate, app.candidate_id)
            if cand:
                db.add(Notification(
                    user_id=cand.user_id, 
                    message=f"Shortlisted for {job.title}!", 
                    type="shortlisted"
                ))
            else:
                print(f"[FINALIZE] Warning: Candidate not found for app {app.id}")
        else:
            print(f"[FINALIZE] Rejecting Application: {app.id}")
            app.status = "rejected"
        db.add(app)
        
    print("[FINALIZE] Closing Job status.")
    job.status = "closed"
    db.add(job)
    
    print("[FINALIZE] Committing changes to DB...")
    await db.commit()
    print("[FINALIZE] Database commit successful. Pipeline finished.")
    return {"logs": ["Recruitment finalized"]}

