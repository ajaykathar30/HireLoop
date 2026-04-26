import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import TIMESTAMP


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )

    job_id: Optional[uuid.UUID] = Field(default=None, foreign_key="jobs.id")
    candidate_id: Optional[uuid.UUID] = Field(default=None, foreign_key="candidates.id")
    cover_note: Optional[str] = Field(default=None)

    # Status: "applied", "screening", "shortlisted", "rejected", "hired"
    status: Optional[str] = Field(default="applied")

    fit_score: Optional[int] = Field(default=None)
    fit_reasoning: Optional[str] = Field(default=None)
    
    # New fields for pipeline
    shortlisted_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        default=None
    )
    interview_deadline: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        default=None
    )

    applied_at: datetime = Field(
        default_factory=utcnow, 
        sa_column_kwargs={"server_default": "now()"}
    )
