from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from core.db import get_db
from middleware.auth import get_current_user_id
from models.interview import InterviewSession, InterviewQuestion
from models.candidate import Candidate
from models.application import Application
from models.company import Company
from models.job import Job
from pipeline.interview_graph import interview_app
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _config(session_id: uuid.UUID, db: AsyncSession) -> dict:
    return {"configurable": {"thread_id": str(session_id), "db": db}}

async def _assert_candidate_owns_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> InterviewSession:
    session = await db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    app = await db.get(Application, session.application_id)
    cand = await db.get(Candidate, app.candidate_id)
    if cand.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session

# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/my-sessions")
async def get_my_interview_sessions(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    cand_stmt = select(Candidate).where(Candidate.user_id == user_id)
    cand_res = await db.execute(cand_stmt)
    candidate = cand_res.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    stmt = select(InterviewSession).join(Application).where(Application.candidate_id == candidate.id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{session_id}/start")
async def start_interview_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    await _assert_candidate_owns_session(session_id, user_id, db)
    config = _config(session_id, db)

    try:
        # Initial run to generate first question
        await interview_app.ainvoke(
            {
                "session_id": session_id,
                "current_q_idx": 0,
                "questions": [],
                "status": "asking",
                "logs": []
            }, 
            config=config
        )
        
        # Fetch the question we just generated
        q_stmt = select(InterviewQuestion).where(
            and_(InterviewQuestion.session_id == session_id, InterviewQuestion.order_index == 0)
        ).limit(1)
        q_res = await db.execute(q_stmt)
        db_q = q_res.scalar_one_or_none()
        
        if not db_q:
            raise HTTPException(status_code=500, detail="Failed to initialize interview")
        
        return {
            "question_number": 1,
            "total_questions": 5,
            "text": db_q.question_text,
            "audio_base64": db_q.question_audio_url,
            "status": "ongoing"
        }
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/submit-answer")
async def submit_interview_answer(
    session_id: uuid.UUID,
    audio_file: Optional[UploadFile] = File(None),
    is_timeout: bool = Form(False),
    force_finalize: bool = Form(False),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    session = await _assert_candidate_owns_session(session_id, user_id, db)
    audio_bytes = await audio_file.read() if audio_file else None
    config = _config(session_id, db)

    try:
        # 1. Update state with answer and trigger 'saving' node
        await interview_app.aupdate_state(
            config,
            {
                "session_id": session_id,
                "last_answer_audio": audio_bytes,
                "is_timeout": is_timeout or force_finalize,
                "status": "saving"
            }
        )
        await interview_app.ainvoke(None, config=config)

        # 2. Check if finished
        snapshot = await interview_app.aget_state(config)
        if snapshot.values.get("status") == "completed":
            return {"status": "completed", "message": "Interview finished"}

        # 3. Get next question
        # After save_answer, the current_q_idx in state points to the NEXT question
        next_idx = snapshot.values.get("current_q_idx")
        
        q_stmt = select(InterviewQuestion).where(
            and_(InterviewQuestion.session_id == session_id, InterviewQuestion.order_index == next_idx)
        ).limit(1)
        q_res = await db.execute(q_stmt)
        db_q = q_res.scalar_one_or_none()

        return {
            "status": "ongoing",
            "question_number": next_idx + 1,
            "text": db_q.question_text if db_q else "Loading...",
            "audio_base64": db_q.question_audio_url if db_q else None
        }
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{application_id}")
async def get_session_by_application(
    application_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    app = await db.get(Application, application_id)
    if not app: raise HTTPException(status_code=404)
    cand = await db.get(Candidate, app.candidate_id)
    if cand.user_id != user_id: raise HTTPException(status_code=403)

    stmt = select(InterviewSession).where(InterviewSession.application_id == application_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

@router.get("/{session_id}")
async def get_interview_session_details(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(InterviewSession).where(InterviewSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session: raise HTTPException(status_code=404)

    app = await db.get(Application, session.application_id)
    cand = await db.get(Candidate, app.candidate_id)
    job = await db.get(Job, app.job_id)
    
    # Simple check for candidate or company
    q_stmt = select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.order_index)
    q_res = await db.execute(q_stmt)
    return {"session": session, "transcript": q_res.scalars().all()}

@router.get("/job/{job_id}/reports")
async def get_job_interview_reports(
    job_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # Verify company
    comp_stmt = select(Company).where(Company.user_id == user_id)
    comp_res = await db.execute(comp_stmt)
    company = comp_res.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=403, detail="Only companies can access reports")

    # Verify job ownership
    job = await db.get(Job, job_id)
    if not job or job.company_id != company.id:
        raise HTTPException(status_code=403, detail="Not authorized to view reports for this job")

    # Fetch interview sessions, applications, and candidates
    stmt = (
        select(InterviewSession, Application, Candidate)
        .join(Application, InterviewSession.application_id == Application.id)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id)
    )
    res = await db.execute(stmt)
    rows = res.all()

    reports = []
    for session, app, cand in rows:
        q_stmt = select(InterviewQuestion).where(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.order_index)
        q_res = await db.execute(q_stmt)
        questions = q_res.scalars().all()
        
        reports.append({
            "candidate_id": cand.id,
            "candidate_name": cand.full_name,
            "application_id": app.id,
            "session_id": session.id,
            "status": session.status,
            "total_score": session.total_score,
            "report_summary": session.report_summary,
            "completed_at": session.completed_at,
            "questions": [
                {
                    "question": q.question_text,
                    "answer": q.answer_text,
                    "score": q.score,
                    "feedback": q.feedback
                } for q in questions
            ]
        })

    return {
        "job_id": job.id,
        "job_title": job.title,
        "total_reports": len(reports),
        "reports": reports
    }

