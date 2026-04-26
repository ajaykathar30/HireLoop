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

async def check_readiness(job_id_str: str):
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        job_id = uuid.UUID(job_id_str)
    except ValueError:
        print(f"Invalid UUID: {job_id_str}")
        return

    async with async_session() as db:
        print(f"\n=== PIPELINE READINESS CHECK FOR JOB: {job_id} ===")
        
        # 1. Check Job
        job_res = await db.execute(text("SELECT title, job_embedding FROM jobs WHERE id = :id"), {"id": job_id})
        job = job_res.fetchone()
        if not job:
            print("❌ FAIL: Job not found in database.")
            return
        
        print(f"Job Title: {job[0]}")
        if job[1] is not None:
            print("✅ PASS: Job has an embedding.")
        else:
            print("❌ FAIL: Job is missing an embedding. (Try updating the job description to regenerate).")

        # 2. Check Applications
        app_res = await db.execute(
            text("""
                SELECT a.id, a.status, c.resume_text, c.resume_embedding, c.full_name
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.id
                WHERE a.job_id = :id
            """), 
            {"id": job_id}
        )
        apps = app_res.fetchall()
        
        print(f"\nTotal Applications Found: {len(apps)}")
        
        applied_count = 0
        ready_count = 0
        
        for app in apps:
            app_id, status, r_text, r_embed, name = app
            is_ready = True
            
            print(f"\n- Candidate: {name or 'Unknown'} (App ID: {app_id})")
            print(f"  Current Status: {status}")
            
            if r_text:
                print("  ✅ Resume Text: Present")
            else:
                print("  ❌ Resume Text: MISSING")
                is_ready = False
                
            if r_embed:
                print("  ✅ Embedding: Present")
            else:
                print("  ❌ Embedding: MISSING (AI Ranker will skip this person)")
                is_ready = False
            
            if status == "applied":
                applied_count += 1
                if is_ready:
                    ready_count += 1

        print(f"\n=== SUMMARY ===")
        print(f"Candidates in 'applied' status: {applied_count}")
        print(f"Candidates ready for pipeline (Text + Embedding + Applied): {ready_count}")
        
        if ready_count == 0:
            print("\n❌ WARNING: No candidates are ready. The pipeline will have nothing to do!")
        elif ready_count < len(apps):
            print(f"\n⚠️ WARNING: {len(apps) - ready_count} candidates are not ready and will be skipped.")
        else:
            print("\n🚀 ALL SYSTEMS GO: Pipeline is ready to run.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tests/check_pipeline_readiness.py <JOB_UUID>")
    else:
        asyncio.run(check_readiness(sys.argv[1]))
