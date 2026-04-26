from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.application import ApplicationCreate, ApplicationResponse
from services.application_service import apply_to_job, get_candidate_applications, get_job_applications
from middleware.ownership import verify_job_ownership
from models.job import Job
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    data: ApplicationCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await apply_to_job(db, user_id, data)

@router.get("/my-applications")
async def get_my_applications(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_candidate_applications(db, user_id)

@router.get("/job/{job_id}")
async def get_applicants_for_job(
    job: Job = Depends(verify_job_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all applicants for a specific job.
    Only accessible by the company that posted the job.
    """
    return await get_job_applications(db, job.id)
