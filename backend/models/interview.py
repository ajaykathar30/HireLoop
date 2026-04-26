import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import TIMESTAMP, TEXT, INTEGER, BOOLEAN


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
    
    # Status: "pending", "ongoing", "completed", "expired"
    status: str = Field(default="pending")
    
    current_question_number: int = Field(default=1)
    total_score: Optional[float] = Field(default=0.0)
    report_summary: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    
    deadline_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    
    completed_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        default=None
    )
    
    created_at: datetime = Field(default_factory=utcnow)

    # Relationships
    questions: List["InterviewQuestion"] = Relationship(back_populates="session", cascade_delete=True)


class InterviewQuestion(SQLModel, table=True):
    __tablename__ = "interview_questions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    session_id: uuid.UUID = Field(foreign_key="interview_sessions.id")
    
    question_text: str = Field(sa_column=Column(TEXT, nullable=False))
    question_type: str = Field(default="technical") # "technical", "behavioral", etc.
    order_index: int = Field(default=0)
    
    # Audio for the question (Bulbul v3 base64 or URL)
    question_audio_url: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    
    # Candidate's answer
    answer_text: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    answer_audio_url: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    
    # Evaluation
    score: Optional[float] = Field(default=None) # 0-20
    feedback: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    
    was_asked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow)

    # Relationships
    session: "InterviewSession" = Relationship(back_populates="questions")
