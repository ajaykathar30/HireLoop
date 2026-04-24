from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    cover_note: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    cover_note: Optional[str] = None
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True
