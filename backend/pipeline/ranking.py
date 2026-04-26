from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

async def rank_candidates_by_similarity(job_id: uuid.UUID, db: AsyncSession) -> list[uuid.UUID]:
    """
    Ranks candidates for a job based on cosine similarity of embeddings using pgvector.
    Returns a list of application IDs.
    """
    print(f"[RANKING] Starting similarity search for Job ID: {job_id}")
    
    # Note: <=> is cosine distance in pgvector. 1 - distance = similarity.
    # We want smaller distance (more similarity) at the top.
    query = text("""
        SELECT a.id, c.resume_embedding, j.job_embedding
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.job_id = :job_id 
          AND a.status = 'screening'
          AND c.resume_embedding IS NOT NULL
          AND j.job_embedding IS NOT NULL
        ORDER BY c.resume_embedding <=> j.job_embedding
        LIMIT 2
    """)
    
    result = await db.execute(query, {"job_id": job_id})
    rows = result.fetchall()
    
    # Extract just the IDs
    application_ids = [row[0] for row in rows]
    
    print(f"[RANKING] Found {len(application_ids)} candidates with valid embeddings and 'screening' status.")
    if len(application_ids) == 0:
        print("[RANKING] WARNING: No candidates found. Check if candidates have status 'screening' and non-null embeddings.")
    
    return application_ids
