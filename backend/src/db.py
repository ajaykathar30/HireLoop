from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,        # set True temporarily if you want to see SQL queries in terminal
    pool_pre_ping=True # auto-reconnects if Supabase drops the connection
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # prevents SQLModel from expiring objects after commit
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)