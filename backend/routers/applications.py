from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.application import ApplicationCreate, ApplicationResponse
from services.application_service import apply_to_job
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    data: ApplicationCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await apply_to_job(db, user_id, data)
