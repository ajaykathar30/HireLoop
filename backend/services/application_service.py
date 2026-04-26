from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from fastapi import HTTPException, status
from models.application import Application
from models.job import Job
from models.candidate import Candidate
from models.company import Company
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
    
async def get_candidate_applications(db: AsyncSession, user_id: uuid.UUID):
    # 1. Get candidate record
    candidate_stmt = select(Candidate).where(Candidate.user_id == user_id)
    result = await db.execute(candidate_stmt)
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # 2. Fetch applications with Job and Company info
    # We join Application -> Job -> Company
    statement = (
        select(Application, Job, Company)
        .join(Job, Application.job_id == Job.id)
        .join(Company, Job.company_id == Company.id)
        .where(Application.candidate_id == candidate.id)
        .order_by(Application.applied_at.desc())
    )
    
    result = await db.execute(statement)
    
    my_apps = []
    for app, job, company in result:
        data = app.model_dump()
        data["job_title"] = job.title
        data["company_name"] = company.name
        data["company_logo"] = company.logo_url
        data["location"] = job.location
        my_apps.append(data)
        
    return my_apps
        
async def get_job_applications(db: AsyncSession, job_id: uuid.UUID):
    """
    Returns all applications for a specific job with candidate details.
    """
    statement = (
        select(Application, Candidate)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id)
        .order_by(Application.fit_score.desc())
    )
    
    result = await db.execute(statement)
    
    applicants = []
    for app, candidate in result:
        data = app.model_dump()
        data["candidate_name"] = candidate.full_name
        data["candidate_skills"] = candidate.skills
        data["candidate_experience"] = candidate.experience_years
        applicants.append(data)
        
    return applicants
