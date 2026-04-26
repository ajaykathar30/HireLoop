import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from pgvector.sqlalchemy import Vector
from pydantic import field_validator, field_serializer
import numpy as np


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)



class Candidate(SQLModel, table=True):
    __tablename__ = "candidates"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_url: Optional[str] = None
    resume_text: Optional[str] = None
    experience_years: Optional[int] = None
    
    # New fields for pipeline
    skills: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    resume_embedding: Optional[Any] = Field(
        sa_column=Column(Vector(768)),
        default=None
    )

    @field_serializer("resume_embedding")
    def serialize_embedding(self, v: Any) -> Any:
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v
    
    created_at: datetime = Field(default_factory=utcnow)
