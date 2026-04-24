from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from models.candidate import Candidate
from schemas.candidate import CandidateUpdate
from core.cloudinary import upload_file
from core.pdf_extractor import extract_text_from_pdf
from core.embeddings import generate_embedding
import uuid

async def update_candidate(db: AsyncSession, user_id: uuid.UUID, data: CandidateUpdate, resume_file: UploadFile = None):
    statement = select(Candidate).where(Candidate.user_id == user_id)
    result = await db.execute(statement)
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Update text fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(candidate, key, value)
    
    # Handle Resume upload
    if resume_file:
        file_content = await resume_file.read()
        resume_url = await upload_file(
            file_content=file_content,
            folder_path="HireLoop/Resume",
            public_id=f"resume_{user_id}"
        )
        candidate.resume_url = resume_url
        
        # New requirements: Extract text and generate embedding
        try:
            raw_text = await extract_text_from_pdf(resume_url)
            candidate.resume_text = raw_text
            
            embedding = await generate_embedding(raw_text)
            candidate.resume_embedding = embedding
        except Exception as e:
            print(f"Error processing resume PDF/Embedding: {e}")
            # We still allow the update even if AI processing fails, 
            # but in production you might want stricter error handling.
            pass
    
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate
