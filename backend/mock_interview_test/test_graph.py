
import uuid
import operator
from typing import List, Annotated, Optional, TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from pipeline.agents.interview_conductor import generate_first_question, generate_next_question
from pipeline.agents.report_genertor import generate_batch_evaluation_report
from datetime import datetime, timezone
from .mock_data import HARDCODED_CONTEXT

# State Definition (Same as original)
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
    qa_history: List[dict] # To keep track of QA without DB

# --- MOCK NODES ---

async def init_interview_node_test(state: InterviewState, config: RunnableConfig):
    print("\n--- TEST NODE: init_interview ---")
    
    first_q = await generate_first_question(
        HARDCODED_CONTEXT["resume_text"], 
        HARDCODED_CONTEXT["job_description"], 
        HARDCODED_CONTEXT["job_requirements"]
    )
    
    return {
        "questions": [first_q.text], 
        "status": "asking", 
        "current_q_idx": 0, 
        "used_rag_chunks": [], 
        "next_question_text": first_q.text,
        "qa_history": []
    }

async def ask_question_node_test(state: InterviewState, config: RunnableConfig):
    idx = state["current_q_idx"]
    print(f"\n--- TEST NODE: ask_question ({idx+1}/5) ---")
    return {"status": "saving"}

async def save_answer_node_test(state: InterviewState, config: RunnableConfig):
    idx = state["current_q_idx"]
    print(f"\n--- TEST NODE: save_answer ({idx+1}/1) ---")
    
    # This comes from the submit-answer endpoint which already transcribes it
    transcript = state.get("last_answer_text") or "No transcript generated."
    
    # Save to history
    current_q_text = state["next_question_text"]
    qa_history = state.get("qa_history", [])
    qa_history.append({
        "question": current_q_text, 
        "answer": transcript,
        "timestamp": datetime.now().isoformat()
    })
    
    new_idx = idx + 1
    next_q_text = None
    used_rag = state.get("used_rag_chunks", [])

    if new_idx < 1:
        # This block will now never be reached since new_idx starts at 1
        history_str = "\n".join([f"Q: {i['question']}\nA: {i['answer']}" for i in qa_history])
        next_q = await generate_next_question(history_str, HARDCODED_CONTEXT["job_description"], new_idx, "")
        next_q_text = next_q.text
        
    return {
        "current_q_idx": new_idx,
        "status": "asking" if new_idx < 1 else "finalizing",
        "used_rag_chunks": used_rag,
        "next_question_text": next_q_text,
        "qa_history": qa_history
    }

async def finalize_interview_node_test(state: InterviewState, config: RunnableConfig):
    print("\n--- TEST NODE: finalize_interview ---")
    qa_list = state.get("qa_history", [])
    session_id = state.get("session_id", "unknown")
    
    # Save transcript to file
    import json
    import os
    os.makedirs("test_transcripts", exist_ok=True)
    filename = f"test_transcripts/transcript_{session_id}.json"
    with open(filename, "w") as f:
        json.dump(qa_list, f, indent=4)
    print(f"[TEST FINAL] Transcript saved to {filename}")

    batch_report = await generate_batch_evaluation_report(
        "Full Stack Developer", 
        HARDCODED_CONTEXT["job_description"], 
        qa_list
    )
    
    print(f"[TEST FINAL] Total Score: {batch_report.total_score}")
    return {"status": "completed"}

# --- GRAPH BUILDER ---

def after_save_router(state: InterviewState):
    return state["status"]

builder = StateGraph(InterviewState)

builder.add_node("init",     init_interview_node_test)
builder.add_node("ask",      ask_question_node_test)
builder.add_node("save",     save_answer_node_test)
builder.add_node("finalize", finalize_interview_node_test)

builder.add_edge(START,      "init")
builder.add_edge("init",     "ask")
builder.add_edge("ask",      "save")
builder.add_edge("finalize", END)

builder.add_conditional_edges("save", after_save_router, {
    "asking":     "ask",
    "finalizing": "finalize",
})

test_checkpointer = MemorySaver()
test_interview_app = builder.compile(
    checkpointer=test_checkpointer,
    interrupt_after=["ask"],
)
