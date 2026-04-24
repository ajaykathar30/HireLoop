# pip install apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from datetime import datetime, timezone
import asyncio

from core.db import AsyncSessionLocal
from models.job import Job
from pipeline.runner import run_job_pipeline

scheduler = AsyncIOScheduler()

async def check_and_run_pipelines():
    """
    Checks for jobs with passed deadlines and triggers the pipeline.
    """
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        
        # Check for jobs where:
        # 1. application_deadline <= now
        # 2. pipeline_triggered = False
        # 3. status = "open"
        statement = select(Job).where(
            and_(
                Job.application_deadline <= now,
                Job.pipeline_triggered == False,
                Job.status == "open"
            )
        )
        
        result = await db.execute(statement)
        jobs_to_run = result.scalars().all()
        
        for job in jobs_to_run:
            try:
                # Run the pipeline for each job
                await run_job_pipeline(job.id, db)
            except Exception as e:
                print(f"Error running pipeline for job {job.id}: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(check_and_run_pipelines, "interval", minutes=30)
        scheduler.start()
        print("Scheduler started: Running every 30 minutes.")
