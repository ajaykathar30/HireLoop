from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.company import CompanyUpdate
from services.company_service import update_company
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/companies", tags=["companies"])

@router.patch("/update")
async def update_company_details(
    user_id: uuid.UUID = Depends(get_current_user_id),
    name: str = Form(None),
    industry: str = Form(None),
    website: str = Form(None),
    description: str = Form(None),
    logo_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    data = CompanyUpdate(
        name=name,
        industry=industry,
        website=website,
        description=description
    )
    return await update_company(db, user_id, data, logo_file)
