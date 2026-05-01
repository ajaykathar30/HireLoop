from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from models.interview import InterviewSession, InterviewQuestion
from models.application import Application
from models.candidate import Candidate
from models.job import Job
import uuid
from typing import List, Dict, Any

async def get_job_reports_summary(db: AsyncSession, job_id: uuid.UUID) -> Dict[str, Any]:
    """
    Aggregates interview data for a specific job into a summary report.
    """
    # 1. Fetch the job details
    job = await db.get(Job, job_id)
    if not job:
        return {"error": "Job not found"}

    # 2. Fetch all completed interview sessions for this job
    stmt = (
        select(InterviewSession, Application, Candidate)
        .join(Application, InterviewSession.application_id == Application.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id)
        .where(InterviewSession.status == "completed")
        .order_by(InterviewSession.total_score.desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()

    candidates_summary = []
    total_score_sum = 0
    count = 0

    for session, app, cand in rows:
        candidates_summary.append({
            "name": cand.full_name,
            "score": session.total_score,
            "summary": session.report_summary,
            "session_id": str(session.id)
        })
        if session.total_score:
            total_score_sum += session.total_score
            count += 1

    avg_score = (total_score_sum / count) if count > 0 else 0

    return {
        "job_title": job.title,
        "total_interviews": len(candidates_summary),
        "average_score": round(avg_score, 2),
        "candidates": candidates_summary
    }
