from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from pipeline.nodes.interview_nodes import (
    InterviewState,
    init_interview_node,
    ask_question_node,
    save_answer_node,
    finalize_interview_node,
)

# ---------------------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------------------

def after_save_router(state: InterviewState):
    return state["status"]  # "asking" | "finalizing"




builder = StateGraph(InterviewState)

builder.add_node("init",     init_interview_node)
builder.add_node("ask",      ask_question_node)
builder.add_node("save",     save_answer_node)
builder.add_node("finalize", finalize_interview_node)

builder.add_edge(START,      "init")
builder.add_edge("init",     "ask")
builder.add_edge("ask",      "save")
builder.add_edge("finalize", END)

builder.add_conditional_edges("save", after_save_router, {
    "asking":     "ask",
    "finalizing": "finalize",
})

checkpointer = MemorySaver()

interview_app = builder.compile(
    checkpointer=checkpointer,
    interrupt_after=["ask"],   # ← pauses here every time, waiting for audio
)