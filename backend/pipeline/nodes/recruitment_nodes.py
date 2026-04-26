import uuid
import operator
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
    for app, candidate in result.all():
        fit_result = await score_fit(candidate.resume_text, job.description, job.requirements)
        app.fit_score = fit_result.score
        app.fit_reasoning = fit_result.reasoning
        db.add(app)
    await db.commit()
    return {"logs": ["Scoring complete"]}

async def finalize_recruitment_node(state: PipelineState, config: RunnableConfig):
    print("\n--- NODE: finalize_recruitment_node ---")
    db = config["configurable"].get("db")
    job = await db.get(Job, state["job_id"])
    stmt = select(Application).where(and_(Application.job_id == state["job_id"], Application.status == "screening")).order_by(Application.fit_score.desc())
    result = await db.execute(stmt)
    scored_apps = result.scalars().all()
    top_n = job.max_shortlist
    now_utc = datetime.now(timezone.utc)
    for i, app in enumerate(scored_apps):
        if i < top_n:
            app.status = "shortlisted"
            app.shortlisted_at = now_utc
            app.interview_deadline = now_utc + timedelta(hours=24)
            session = InterviewSession(application_id=app.id, status="pending", deadline_at=app.interview_deadline)
            db.add(session)
            cand = await db.get(Candidate, app.candidate_id)
            db.add(Notification(user_id=cand.user_id, message=f"Shortlisted for {job.title}!", type="shortlisted"))
        else:
            app.status = "rejected"
        db.add(app)
    job.status = "closed"
    job.pipeline_triggered = True
    db.add(job)
    await db.commit()
    return {"logs": ["Recruitment finalized"]}
