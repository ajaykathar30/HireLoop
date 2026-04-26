from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.job import JobCreate
from services.job_service import create_job, get_company_jobs, get_all_jobs
from middleware.auth import get_current_user_id
from middleware.ownership import verify_job_ownership
from pipeline.runner import run_job_pipeline
from models.job import Job
import uuid

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_job(
    data: JobCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await create_job(db, user_id, data)

@router.get("")
async def list_jobs(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_jobs(db)

@router.get("/my-jobs")
async def get_my_jobs(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await get_company_jobs(db, user_id)

@router.post("/{job_id}/trigger-pipeline")
async def trigger_job_pipeline(
    job_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    job: Job = Depends(verify_job_ownership),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually triggers the recruitment pipeline for a specific job.
    Only accessible by the company that posted the job.
    """
    background_tasks.add_task(run_job_pipeline, job.id, db)
    return {"message": "Pipeline triggered successfully", "job_id": job.id}
