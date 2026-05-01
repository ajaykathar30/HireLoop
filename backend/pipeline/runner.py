import uuid
import logging
from pipeline.recruitment_graph import recruitment_app
from core.db import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def run_job_pipeline(job_id: uuid.UUID):
    """
    Triggers the LangGraph-based recruitment pipeline.
    Creates its own DB session since this runs as a background task
    outside the request lifecycle.
    """
    logger.info(f"Starting LangGraph pipeline for Job: {job_id}")
    
    initial_state = {
        "job_id": job_id,
        "application_ids": [],
        "top_candidate_ids": [],
        "logs": []
    }
    
    # Create a fresh session for the background task
    async with AsyncSessionLocal() as db:
        config = {"configurable": {"db": db}}
        
        try:
            final_state = await recruitment_app.ainvoke(
                initial_state,
                config=config
            )
            
            for log in final_state.get("logs", []):
                logger.info(f"PIPELINE LOG: {log}")
                
            logger.info(f"LangGraph pipeline completed for Job: {job_id}")
            return final_state
        except Exception as e:
            logger.error(f"LangGraph Pipeline Error for job {job_id}: {e}")
            raise e
