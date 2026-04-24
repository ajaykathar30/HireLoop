from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_, not_
from datetime import datetime, timedelta, timezone
import uuid

from models.job import Job
from models.application import Application
from models.candidate import Candidate
from models.interview import InterviewSession
from models.notification import Notification

from pipeline.agents.resume_parser import parse_resume
from pipeline.agents.fit_scorer import score_fit
from pipeline.ranking import rank_candidates_by_similarity

async def run_job_pipeline(job_id: uuid.UUID, db: AsyncSession):
    """
    Full recruitment pipeline: Parse -> Rank -> Score -> Shortlist -> Notify -> Close
    """
    # 0. Fetch job
    job_stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(job_stmt)
    job = result.scalar_one_or_none()
    if not job:
        print(f"Pipeline Error: Job {job_id} not found")
        return

    print(f"Starting pipeline for Job: {job.title}")

    # STEP 1 — Parse resumes
    app_stmt = select(Application).where(
        and_(Application.job_id == job_id, Application.status == "applied")
    )
    result = await db.execute(app_stmt)
    applications = result.scalars().all()
    
    for app in applications:
        try:
            await parse_resume(str(app.candidate_id), db)
            app.status = "screening"
            db.add(app)
        except Exception as e:
            print(f"Error parsing resume for application {app.id}: {e}")
    
    await db.commit()

    # STEP 2 — pgvector pre-filter
    top_20_ids = await rank_candidates_by_similarity(job_id, db)
    
    # Reject others
    reject_others_stmt = select(Application).where(
        and_(
            Application.job_id == job_id,
            Application.status == "screening",
            not_(Application.id.in_(top_20_ids))
        )
    )
    result = await db.execute(reject_others_stmt)
    rejected_apps = result.scalars().all()
    for app in rejected_apps:
        app.status = "rejected"
        db.add(app)
    
    await db.commit()

    # STEP 3 — Gemini fit scoring (only top 20)
    top_apps_stmt = select(Application, Candidate).join(Candidate).where(
        Application.id.in_(top_20_ids)
    )
    result = await db.execute(top_apps_stmt)
    top_pairs = result.all() # list of (Application, Candidate)
    
    final_scores = [] # store (app, fit_score_obj)
    
    for app, candidate in top_pairs:
        try:
            fit_result = await score_fit(
                candidate.resume_text, 
                job.description, 
                job.requirements
            )
            app.fit_score = fit_result.score
            app.fit_reasoning = fit_result.reasoning
            db.add(app)
            final_scores.append((app, fit_result))
        except Exception as e:
            print(f"Error scoring fit for application {app.id}: {e}")
            
    await db.commit()

    # STEP 4 — Final shortlisting
    # Sort final_scores by score descending
    final_scores.sort(key=lambda x: x[1].score, reverse=True)
    
    top_n = job.max_shortlist
    shortlisted_apps = final_scores[:top_n]
    remaining_apps = final_scores[top_n:]
    
    now_utc = datetime.now(timezone.utc)
    
    for app, fit_obj in shortlisted_apps:
        app.status = "shortlisted"
        app.shortlisted_at = now_utc
        app.interview_deadline = now_utc + timedelta(hours=24)
        db.add(app)
        
        # Create InterviewSession
        interview = InterviewSession(
            application_id=app.id,
            status="pending",
            deadline_at=app.interview_deadline
        )
        db.add(interview)
        
    for app, fit_obj in remaining_apps:
        app.status = "rejected"
        db.add(app)
        
    await db.commit()

    # STEP 5 — Notifications
    # Re-fetch applications with user info for notifications if needed, 
    # but we can use candidate.user_id
    for app, _ in shortlisted_apps:
        # Get candidate to get user_id
        cand_result = await db.execute(select(Candidate).where(Candidate.id == app.candidate_id))
        cand = cand_result.scalar_one()
        notif = Notification(
            user_id=cand.user_id,
            message=f"You have been shortlisted for {job.title}! Complete your AI interview within 24 hours.",
            type="shortlisted"
        )
        db.add(notif)
        
    # Get all rejected apps for this job to notify
    rejected_final_stmt = select(Application, Candidate).join(Candidate).where(
        and_(Application.job_id == job_id, Application.status == "rejected")
    )
    result = await db.execute(rejected_final_stmt)
    all_rejected = result.all()
    for app, cand in all_rejected:
        notif = Notification(
            user_id=cand.user_id,
            message=f"Thank you for applying to {job.title}. We have moved forward with other candidates.",
            type="rejected"
        )
        db.add(notif)
        
    await db.commit()

    # STEP 6 — Close the job
    job.status = "closed"
    job.pipeline_triggered = True
    db.add(job)
    await db.commit()
    
    print(f"Pipeline completed for Job: {job.title}")
