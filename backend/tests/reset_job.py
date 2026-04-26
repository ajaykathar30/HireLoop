import asyncio
import os
import sys
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from core.config import settings

async def reset_job(job_id_str: str):
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        job_id = uuid.UUID(job_id_str)
    except ValueError:
        print(f"Invalid UUID: {job_id_str}")
        return

    async with async_session() as db:
        print(f"\n--- RESETTING JOB: {job_id} ---")
        
        # 1. Reset Job Status
        await db.execute(
            text("UPDATE jobs SET status = 'open', pipeline_triggered = False WHERE id = :id"),
            {"id": job_id}
        )
        
        # 2. Delete linked Interviews & Notifications (Cleanup)
        # We find application IDs first
        res = await db.execute(text("SELECT id FROM applications WHERE job_id = :id"), {"id": job_id})
        app_ids = [row[0] for row in res.fetchall()]
        
        if app_ids:
            # Delete Interview Sessions
            await db.execute(
                text("DELETE FROM interview_sessions WHERE application_id = ANY(:ids)"),
                {"ids": app_ids}
            )
            print(f"Deleted interview sessions for {len(app_ids)} applications.")

        # 3. Reset Application status
        await db.execute(
            text("""
                UPDATE applications 
                SET status = 'applied', 
                    fit_score = NULL, 
                    fit_reasoning = NULL, 
                    shortlisted_at = NULL, 
                    interview_deadline = NULL 
                WHERE job_id = :id
            """),
            {"id": job_id}
        )
        
        await db.commit()
        print(f"Successfully reset job and {len(app_ids)} applications to 'applied' state.")
        print("You can now trigger the pipeline again from the UI or API.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tests/reset_job.py <JOB_UUID>")
    else:
        asyncio.run(reset_job(sys.argv[1]))
