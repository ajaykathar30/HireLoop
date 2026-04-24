from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_deadline: Optional[datetime] = None

class JobResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    description: str
    requirements: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: str
    job_posted_at: datetime
    application_deadline: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
