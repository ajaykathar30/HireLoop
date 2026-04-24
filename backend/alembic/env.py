import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from sqlmodel import SQLModel
import pgvector.sqlalchemy

from core.config import settings
# Import all models here so SQLModel.metadata knows about them
from models.user import User
from models.candidate import Candidate
from models.company import Company
from models.job import Job
from models.application import Application
from models.interview import InterviewSession
from models.notification import Notification

# this is the Alembic Config object
config = context.config

# setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# point Alembic at your SQLModel metadata
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    # Handle the postgresql+asyncpg case
    url = settings.DATABASE_URL
    connectable = create_async_engine(url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
