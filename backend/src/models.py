import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ─── Users ────────────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(sa_column_kwargs={"nullable": False})  # "candidate" or "company"
    created_at: datetime = Field(default_factory=utcnow)


# ─── Candidates ───────────────────────────────────────────────────────────────

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
    created_at: datetime = Field(default_factory=utcnow)


# ─── Companies ────────────────────────────────────────────────────────────────

class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)