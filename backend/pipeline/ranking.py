from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

async def rank_candidates_by_similarity(job_id: uuid.UUID, db: AsyncSession) -> list[uuid.UUID]:
    """
    Ranks candidates for a job based on cosine similarity of embeddings using pgvector.
    Returns a list of application IDs.
    """
    # Note: <=> is cosine distance in pgvector. 1 - distance = similarity.
    # We want smaller distance (more similarity) at the top.
    query = text("""
        SELECT a.id
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.job_id = :job_id AND a.status = 'applied'
        ORDER BY c.resume_embedding <=> j.job_embedding
        LIMIT 20
    """)
    
    result = await db.execute(query, {"job_id": job_id})
    # result.scalars().all() might not work correctly with raw SQL select of ID
    application_ids = [row[0] for row in result.fetchall()]
    
    return application_ids
