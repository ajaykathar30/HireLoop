import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import TIMESTAMP


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class InterviewSession(SQLModel, table=True):
    __tablename__ = "interview_sessions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    application_id: uuid.UUID = Field(foreign_key="applications.id")
    
    # Status: "pending", "completed", "expired"
    status: str = Field(default="pending")
    
    deadline_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    
    created_at: datetime = Field(default_factory=utcnow)
