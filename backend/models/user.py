import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
