import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

