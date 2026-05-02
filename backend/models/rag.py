import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import TEXT, Column
from pgvector.sqlalchemy import Vector

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class DomainKnowledgeBase(SQLModel, table=True):
    __tablename__ = "domain_knowledge_base"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    domain: str = Field(sa_column=Column(TEXT, nullable=False)) # e.g. Frontend, Backend, AI Agents, DSA
    source_file: str = Field(sa_column=Column(TEXT, nullable=True)) # e.g. "DDIA.pdf"
    content: str = Field(sa_column=Column(TEXT, nullable=False))
    embedding: list[float] = Field(sa_column=Column(Vector(768)))
    created_at: datetime = Field(default_factory=utcnow)
