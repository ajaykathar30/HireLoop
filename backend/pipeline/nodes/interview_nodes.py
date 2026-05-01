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
from models.interview import InterviewSession, InterviewQuestion, InterviewRoomMemory
from models.rag import DomainKnowledgeBase

from pipeline.agents.interview_conductor import generate_first_question, generate_next_question
from pipeline.agents.report_genertor import generate_batch_evaluation_report

from core.sarvam import text_to_speech, speech_to_text, stream_text_to_speech
from core.embeddings import generate_embedding
from core.cloudinary import upload_file

# State Definition
class InterviewState(TypedDict):
    session_id: uuid.UUID
    current_q_idx: int 
    questions: List[str]
    status: str 
    last_answer_audio: Optional[bytes]
    last_answer_text: Optional[str]
    is_timeout: bool
    used_rag_chunks: list[str]
    next_question_text: Optional[str]
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
            "current_q_idx": 0,
            "used_rag_chunks": [],
            "next_question_text": existing_qs[0].question_text if existing_qs else None
        }

    # Generate the FIRST question only
    session = await db.get(InterviewSession, session_id)
    app = await db.get(Application, session.application_id)
    cand = await db.get(Candidate, app.candidate_id)
    job = await db.get(Job, app.job_id)
    
    print(f"[INIT] Generating 1st question for {cand.full_name}...")
    first_q = await generate_first_question(cand.resume_text, job.description, job.requirements)
    
    db_q = InterviewQuestion(
        session_id=session.id, 
        question_text=first_q.text, 
        question_type=first_q.type, 
        order_index=0
    )
    db.add(db_q)
    
    session.status = "ongoing"
    session.current_question_number = 1
    await db.commit()
    
    return {"questions": [first_q.text], "status": "asking", "current_q_idx": 0, "used_rag_chunks": [], "next_question_text": first_q.text}

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

    # We no longer generate base64 audio here. Audio is streamed directly to the frontend.
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
    audio_bytes = state.get("last_answer_audio")
    if not transcript and not state.get("is_timeout") and audio_bytes:
        transcript = await speech_to_text(audio_bytes)
        # Background upload to Cloudinary
        asyncio.create_task(upload_file(audio_bytes, "HireLoop/CandidateAudio"))
        
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
        
        # Add to Vector Memory
        interaction_text = f"Q: {db_q.question_text}\nA: {transcript}"
        emb = await generate_embedding(interaction_text)
        memory = InterviewRoomMemory(
            session_id=session_id,
            interaction_text=interaction_text,
            embedding=emb
        )
        db.add(memory)
        await db.flush() # Ensure it's available for querying
        
        new_idx = idx + 1
        
        # 3. Generate Next Question Dynamically
        session = await db.get(InterviewSession, session_id)
        if new_idx < 5:
            app = await db.get(Application, session.application_id)
            job = await db.get(Job, app.job_id)
            
            # Fetch context from Vector DB (top 3 closest to latest interaction)
            mem_stmt = select(InterviewRoomMemory).where(
                InterviewRoomMemory.session_id == session_id
            ).order_by(
                InterviewRoomMemory.embedding.cosine_distance(emb)
            ).limit(3)
            mem_res = await db.execute(mem_stmt)
            memories = mem_res.scalars().all()
            history = "\n".join([m.interaction_text for m in memories])
            
            # --- RAG Retrieval for Deep Domain Knowledge ---
            used_rag = state.get("used_rag_chunks", [])
            rag_stmt = select(DomainKnowledgeBase)
            
            # Filter out already used chunks to avoid repetition
            if used_rag:
                rag_stmt = rag_stmt.where(~DomainKnowledgeBase.id.in_(used_rag))
                
            rag_stmt = rag_stmt.order_by(
                DomainKnowledgeBase.embedding.cosine_distance(emb)
            ).limit(1)
            
            rag_res = await db.execute(rag_stmt)
            rag_chunk = rag_res.scalar_one_or_none()
            
            rag_context = ""
            if rag_chunk:
                rag_context = rag_chunk.content
                used_rag.append(str(rag_chunk.id))
            
            next_q = await generate_next_question(history, job.description, new_idx, rag_context)
            db_next_q = InterviewQuestion(
                session_id=session_id,
                question_text=next_q.text,
                question_type=next_q.type,
                order_index=new_idx
            )
            db.add(db_next_q)
            
        session.current_question_number = new_idx + 1
        db.add(session)
        await db.commit()
        
        print(f"[SAVE] Progressed to Question {new_idx + 1}")

        return {
            "current_q_idx": new_idx,
            "status": "asking" if new_idx < 5 else "finalizing",
            "used_rag_chunks": used_rag,
            "next_question_text": next_q.text if new_idx < 5 else None
        }
    return state

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
    session.completed_at = datetime.now(timezone.utc)
    
    app.status = "interviewed"
    app.fit_score = int(batch_report.total_score)
    
    # Delete the room memory context
    del_stmt = select(InterviewRoomMemory).where(InterviewRoomMemory.session_id == session_id)
    mems_to_delete = await db.execute(del_stmt)
    for m in mems_to_delete.scalars().all():
        await db.delete(m)
        
    await db.commit()
    print("[FINAL] Session completed and memory cleared.")
    return {"status": "completed"}
