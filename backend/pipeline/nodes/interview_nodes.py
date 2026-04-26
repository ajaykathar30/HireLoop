import uuid
import asyncio
import operator
from typing import List, Annotated, Optional, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from datetime import datetime, timezone
from langchain_core.runnables import RunnableConfig

from models.job import Job
from models.application import Application
from models.candidate import Candidate
from models.interview import InterviewSession, InterviewQuestion

from pipeline.agents.interview_conductor import generate_interview_questions
from pipeline.agents.report_genertor import generate_batch_evaluation_report

from core.sarvam import text_to_speech, speech_to_text

# State Definition
class InterviewState(TypedDict):
    session_id: uuid.UUID
    current_q_idx: int 
    questions: List[str]
    status: str 
    last_answer_audio: Optional[bytes]
    last_answer_text: Optional[str]
    is_timeout: bool
    logs: Annotated[List[str], operator.add]

async def init_interview_node(state: InterviewState, config: RunnableConfig):
    """Generates all 5 questions at the start."""
    print("\n--- NODE: init_interview (GENERATE ALL) ---")
    db = config["configurable"].get("db")
    session_id = state["session_id"]
    
    # Check if questions already exist
    q_check = await db.execute(select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).limit(1))
    if q_check.scalar_one_or_none():
        print("[INIT] Questions already exist. Moving to asking.")
        all_q_res = await db.execute(select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.order_index))
        existing_qs = all_q_res.scalars().all()
        return {
            "questions": [q.question_text for q in existing_qs],
            "status": "asking",
            "current_q_idx": 0
        }

    # Generate all 5 questions once
    session = await db.get(InterviewSession, session_id)
    app = await db.get(Application, session.application_id)
    cand = await db.get(Candidate, app.candidate_id)
    job = await db.get(Job, app.job_id)
    
    print(f"[INIT] Generating 5 questions for {cand.full_name}...")
    qs = await generate_interview_questions(cand.resume_text, job.description, job.requirements)
    
    for i, q in enumerate(qs):
        db_q = InterviewQuestion(
            session_id=session.id, 
            question_text=q.text, 
            question_type=q.type, 
            order_index=i
        )
        db.add(db_q)
    
    session.status = "ongoing"
    session.current_question_number = 1
    await db.commit()
    
    return {"questions": [q.text for q in qs], "status": "asking", "current_q_idx": 0}

async def ask_question_node(state: InterviewState, config: RunnableConfig):
    """Purely fetches the question and generates audio."""
    idx = state["current_q_idx"]
    print(f"\n--- NODE: ask_question ({idx+1}/5) ---")
    db = config["configurable"].get("db")
    session_id = state["session_id"]

    # Retrieve question from DB
    stmt = select(InterviewQuestion).where(
        and_(InterviewQuestion.session_id == session_id, InterviewQuestion.order_index == idx)
    ).limit(1)
    res = await db.execute(stmt)
    db_q = res.scalar_one_or_none()
    
    if not db_q:
        raise ValueError(f"Question not found for idx {idx}")

    # Generate Voice
    audio_b64 = await text_to_speech(db_q.question_text)
    db_q.question_audio_url = audio_b64
    db_q.was_asked = True
    db.add(db_q)
    await db.commit()

    return {"status": "saving"}

async def save_answer_node(state: InterviewState, config: RunnableConfig):
    """Transcribes and INCREMENTS the counter."""
    idx = state["current_q_idx"]
    print(f"\n--- NODE: save_answer ({idx+1}/5) ---")
    db = config["configurable"].get("db")
    session_id = state["session_id"]
    
    # 1. Transcribe
    transcript = state.get("last_answer_text")
    if not transcript and not state.get("is_timeout") and state.get("last_answer_audio"):
        transcript = await speech_to_text(state["last_answer_audio"])
    
    transcript = transcript or "No answer provided"

    # 2. Save Answer
    stmt = select(InterviewQuestion).where(
        and_(InterviewQuestion.session_id == session_id, InterviewQuestion.order_index == idx)
    ).limit(1)
    res = await db.execute(stmt)
    db_q = res.scalar_one_or_none()
    
    if db_q:
        db_q.answer_text = transcript
        db.add(db_q)
    
    # 3. CRITICAL: Increment progress in DB
    new_idx = idx + 1
    session = await db.get(InterviewSession, session_id)
    session.current_question_number = new_idx + 1
    db.add(session)
    await db.commit()
    
    print(f"[SAVE] Progressed to Question {new_idx + 1}")

    return {
        "current_q_idx": new_idx,
        "status": "asking" if new_idx < 5 else "finalizing"
    }

async def finalize_interview_node(state: InterviewState, config: RunnableConfig):
    """Batch scoring at the very end."""
    print("\n--- NODE: finalize_interview (BATCH) ---")
    db = config["configurable"].get("db")
    session_id = state["session_id"]
    
    session = await db.get(InterviewSession, session_id)
    app = await db.get(Application, session.application_id)
    job = await db.get(Job, app.job_id)
    
    stmt = select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.order_index)
    res = await db.execute(stmt)
    questions = res.scalars().all()
    
    qa_list = [{"question": q.question_text, "answer": q.answer_text} for q in questions]
    
    print("[FINAL] Gemini is reviewing all 5 answers...")
    batch_report = await generate_batch_evaluation_report(job.title, job.description, qa_list)
    
    for i, scored_q in enumerate(batch_report.individual_scores):
        if i < len(questions):
            questions[i].score = scored_q.score
            questions[i].feedback = scored_q.feedback
            db.add(questions[i])
    
    session.total_score = batch_report.total_score
    session.report_summary = batch_report.summary
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    app.status = "interviewed"
    app.fit_score = int(batch_report.total_score)
    
    await db.commit()
    print("[FINAL] Session completed.")
    return {"status": "completed"}
