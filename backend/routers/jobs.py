from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.job import JobCreate
from services.job_service import create_job, get_company_jobs, get_all_jobs
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_job(
    data: JobCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await create_job(db, user_id, data)

@router.get("/")
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
