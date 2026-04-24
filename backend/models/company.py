import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)



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