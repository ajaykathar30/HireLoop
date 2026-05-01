
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
import logging
from .test_graph import test_interview_app
from core.sarvam import stream_text_to_speech, speech_to_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test-interview", tags=["test-interview"])

def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}

@router.post("/start")
async def start_test_interview(session_id: Optional[str] = None):
    # Use a fixed session ID if not provided for easy testing
    sid = session_id or "test-session-123"
    config = _config(sid)

    try:
        await test_interview_app.ainvoke(
            {
                "session_id": uuid.uuid4(), 
                "current_q_idx": 0,
                "questions": [],
                "status": "asking",
                "logs": [],
                "qa_history": []
            }, 
            config=config
        )
        
        snapshot = await test_interview_app.aget_state(config)
        next_q_text = snapshot.values.get("next_question_text")
        
        return {
            "question_number": 1,
            "total_questions": 1,
            "text": next_q_text,
            "status": "ongoing",
            "session_id": sid
        }
    except Exception as e:
        logger.error(f"Error starting test interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-answer")
async def submit_test_answer(
    session_id: str = Form(...),
    answer_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    is_timeout: bool = Form(False)
):
    config = _config(session_id)
    
    # Handle audio transcription if audio is provided
    transcript = answer_text
    if audio_file:
        audio_bytes = await audio_file.read()
        
        # --- NEW: Save file to backend for debugging ---
        import os
        os.makedirs("test_audio", exist_ok=True)
        # Use session_id and a timestamp or question_idx
        audio_path = f"test_audio/audio_{session_id}.webm"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        logger.info(f"Saved test audio to {audio_path}")
        # -----------------------------------------------

        transcript = await speech_to_text(audio_bytes)
    
    if not transcript:
        transcript = "No answer provided."

    try:
        # Update state with answer
        await test_interview_app.aupdate_state(
            config,
            {
                "last_answer_text": transcript,
                "is_timeout": is_timeout,
                "status": "saving"
            },
            as_node="ask"
        )
        await test_interview_app.ainvoke(None, config=config)

        # Check if finished
        snapshot = await test_interview_app.aget_state(config)
        if snapshot.values.get("status") == "completed":
            return {"status": "completed", "message": "Test Interview finished"}

        # Get next question
        next_idx = snapshot.values.get("current_q_idx")
        next_q_text = snapshot.values.get("next_question_text")

        return {
            "status": "ongoing",
            "question_number": next_idx + 1,
            "text": next_q_text or "Loading..."
        }
    except Exception as e:
        logger.error(f"Error submitting test answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/stream-audio/{question_idx}")
async def stream_test_audio(
    session_id: str,
    question_idx: int
):
    config = _config(session_id)
    snapshot = await test_interview_app.aget_state(config)
    
    # For testing, we just get the next_question_text from state
    # In a real session we'd fetch from DB, but here we use the graph snapshot
    q_text = snapshot.values.get("next_question_text")
    
    if not q_text:
        raise HTTPException(status_code=404, detail="Question not found in state")
        
    async def audio_generator():
        async for chunk in stream_text_to_speech(q_text):
            yield chunk

    return StreamingResponse(audio_generator(), media_type="audio/wav")
