from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from core.db import get_db
from models.job import Job
from models.company import Company
from middleware.auth import get_current_user_id
import uuid

async def verify_job_ownership(
    job_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Job:
    """
    Dependency to verify that a job exists and belongs to the currently logged-in company.
    """
    # 1. Get the company profile for the logged-in user
    comp_stmt = select(Company).where(Company.user_id == user_id)
    comp_res = await db.execute(comp_stmt)
    company = comp_res.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies with profiles can perform this action"
        )

    # 2. Get the job and check if it belongs to this company
    job_stmt = select(Job).where(Job.id == job_id)
    job_res = await db.execute(job_stmt)
    job = job_res.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this job's pipeline"
        )

    return job
