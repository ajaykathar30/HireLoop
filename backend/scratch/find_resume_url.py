import sys
import os
sys.path.append(os.getcwd())
import asyncio
from core.db import AsyncSessionLocal
from models.candidate import Candidate
from sqlmodel import select

async def get_one():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Candidate).where(Candidate.resume_url.is_not(None)).limit(1))
        cand = res.scalar_one_or_none()
        print(cand.resume_url if cand else "None")

if __name__ == "__main__":
    asyncio.run(get_one())
