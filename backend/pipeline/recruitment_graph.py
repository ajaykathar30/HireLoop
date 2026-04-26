from langgraph.graph import StateGraph, END
from pipeline.nodes.recruitment_nodes import (
    PipelineState,
    fetch_applications_node,
    parse_resumes_node,
    rank_candidates_node,
    score_fit_node,
    finalize_recruitment_node
)

# ─── RECRUITMENT WORKFLOW ──────────────────────────────────────────────────

workflow = StateGraph(PipelineState)

workflow.add_node("fetch", fetch_applications_node)
workflow.add_node("parse", parse_resumes_node)
workflow.add_node("rank", rank_candidates_node)
workflow.add_node("score", score_fit_node)
workflow.add_node("finalize", finalize_recruitment_node)

workflow.set_entry_point("fetch")
workflow.add_edge("fetch", "parse")
workflow.add_edge("parse", "rank")
workflow.add_edge("rank", "score")
workflow.add_edge("score", "finalize")
workflow.add_edge("finalize", END)

# Compiled Recruitment Application
recruitment_app = workflow.compile()
