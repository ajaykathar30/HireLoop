from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from pipeline.recruitment_graph import recruitment_app

async def run_job_pipeline(job_id: uuid.UUID, db: AsyncSession):
    """
    Triggers the LangGraph-based recruitment pipeline.
    """
    print(f"Starting LangGraph pipeline for Job: {job_id}")
    
    initial_state = {
        "job_id": job_id,
        "application_ids": [],
        "top_candidate_ids": [],
        "logs": []
    }
    
    # Correct LangGraph pattern: pass 'db' through configurable
    config = {"configurable": {"db": db}}
    
    try:
        final_state = await recruitment_app.ainvoke(
            initial_state,
            config=config
        )
        
        for log in final_state.get("logs", []):
            print(f"PIPELINE LOG: {log}")
            
        print(f"LangGraph pipeline completed for Job: {job_id}")
        return final_state
    except Exception as e:
        print(f"LangGraph Pipeline Error for job {job_id}: {e}")
        raise e
