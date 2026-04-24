import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import func, TIMESTAMP
from pgvector.sqlalchemy import Vector

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )

    company_id: Optional[uuid.UUID] = Field(default=None, foreign_key="companies.id")
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    requirements: str = Field(nullable=False)
    location: Optional[str] = Field(default=None)
    job_type: Optional[str] = Field(default=None)
    salary_min: Optional[int] = Field(default=None)
    salary_max: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default="open")
    
    # Pipeline fields
    pipeline_triggered: bool = Field(default=False)
    max_shortlist: int = Field(default=5)
    min_fit_score: int = Field(default=60)

    job_posted_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now()),
        default_factory=utcnow
    )
    application_deadline: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        default=None
    )

    job_embedding: Optional[List[float]] = Field(
        sa_column=Column(Vector(768)), 
        default=None
    )

    created_at: datetime = Field(default_factory=utcnow)
