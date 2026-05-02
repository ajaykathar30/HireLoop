from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from middleware.auth import get_current_user_id
from services.report_service import get_job_reports_summary
from models.company import Company
from models.job import Job
from sqlmodel import select
import uuid

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/job/{job_id}")
async def get_job_report(
    job_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a summarized report for all interviews conducted for a specific job.
    Accessible only by the company that posted the job.
    """
    # 1. Verify user is a company
    comp_stmt = select(Company).where(Company.user_id == user_id)
    comp_res = await db.execute(comp_stmt)
    company = comp_res.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=403, detail="Only companies can access reports")

    # 2. Verify job ownership
    job = await db.get(Job, job_id)
    if not job or job.company_id != company.id:
        raise HTTPException(status_code=403, detail="Not authorized to view reports for this job")

    # 3. Generate summary
    report = await get_job_reports_summary(db, job_id)
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
        
    return report
