from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.candidate import CandidateUpdate
from services.candidate_service import update_candidate
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.patch("/update")
async def update_candidate_details(
    user_id: uuid.UUID = Depends(get_current_user_id),
    full_name: str = Form(None),
    phone: str = Form(None),
    linkedin_url: str = Form(None),
    experience_years: int = Form(None),
    resume_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    data = CandidateUpdate(
        full_name=full_name,
        phone=phone,
        linkedin_url=linkedin_url,
        experience_years=experience_years
    )
    return await update_candidate(db, user_id, data, resume_file)
