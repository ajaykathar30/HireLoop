import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    message: str = Field(nullable=False)
    type: str = Field(default="info") # e.g., "shortlisted", "rejected", "info"
    is_read: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=utcnow)
