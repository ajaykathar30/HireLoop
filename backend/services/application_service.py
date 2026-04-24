from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from fastapi import HTTPException, status
from models.application import Application
from models.job import Job
from models.candidate import Candidate
from schemas.application import ApplicationCreate
from datetime import datetime, timezone
import uuid

async def apply_to_job(db: AsyncSession, user_id: uuid.UUID, data: ApplicationCreate):
    # 1. Find the candidate record linked to the user_id
    candidate_stmt = select(Candidate).where(Candidate.user_id == user_id)
    result = await db.execute(candidate_stmt)
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only candidates can apply for jobs"
        )
    
    # 2. Verify job existence and "open" status
    job_stmt = select(Job).where(Job.id == data.job_id)
    result = await db.execute(job_stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status.lower() != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"This job is currently {job.status} and not accepting new applications."
        )
    
    # 3. Application Deadline check
    if job.application_deadline:
        # Ensure we are comparing offset-aware datetimes if stored as TIMESTAMPTZ
        now = datetime.now(timezone.utc)
        deadline = job.application_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
            
        if now > deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The application deadline for this job has passed."
            )
    
    # 4. Prevent duplicate applications
    existing_stmt = select(Application).where(
        and_(Application.job_id == data.job_id, Application.candidate_id == candidate.id)
    )
    result = await db.execute(existing_stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You have already applied for this job."
        )
    
    # 5. Create the new application record
    new_app = Application(
        job_id=data.job_id,
        candidate_id=candidate.id,
        cover_note=data.cover_note,
        status="applied"
    )
    
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    
    return new_app
