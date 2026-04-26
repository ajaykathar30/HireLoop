from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from models.company import Company
from schemas.company import CompanyUpdate
from core.cloudinary import upload_file
import uuid

async def update_company(db: AsyncSession, user_id: uuid.UUID, data: CompanyUpdate, logo_file: UploadFile = None):
    statement = select(Company).where(Company.user_id == user_id)
    result = await db.execute(statement)
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update text fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    
    # Handle Logo upload
    if logo_file:
        file_content = await logo_file.read()
        logo_url = await upload_file(
            file_content=file_content,
            folder_path="HireLoop/CompanyLogo",
            public_id=f"logo_{user_id}"
        )
        company.logo_url = logo_url
    
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
