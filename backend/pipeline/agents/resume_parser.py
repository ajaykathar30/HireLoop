# pip install langchain-google-genai
from dotenv import load_dotenv
import os
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.candidate import Candidate

load_dotenv()

class ParsedResume(BaseModel):
    full_name: Optional[str] = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="Technical skills only, max 10, no soft skills")
    experience_years: int = Field(description="Total years of experience, 0 if fresher")
    education: Optional[str] = Field(description="Highest education degree and institution")
    current_role: Optional[str] = Field(description="Current or most recent job title")
    projects: List[str] = Field(description="Brief one line descriptions of key projects")
    summary: str = Field(description="2-3 sentence professional summary")

async def parse_resume_text(text: str) -> ParsedResume:
    """
    Parses raw resume text using Gemini AI with structured output.
    Does NOT interact with the database.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", # Use a stable model name or your preferred version
        google_api_key=api_key,
        temperature=0.3
    )
    
    structured_llm = llm.with_structured_output(ParsedResume)
    
    parsed_result = await structured_llm.ainvoke(
        f"Parse the following resume text:\n\n{text}"
    )
    
    return parsed_result

async def parse_resume(candidate_id: str, db: AsyncSession) -> Optional[ParsedResume]:
    """
    Parses resume text from DB using Gemini AI with structured output.
    Updates the candidate record in the database only if not already parsed.
    """
    # 1. Read candidate from DB
    statement = select(Candidate).where(Candidate.id == candidate_id)
    result = await db.execute(statement)
    candidate = result.scalar_one_or_none()
    
    if not candidate or not candidate.resume_text:
        raise ValueError(f"Candidate {candidate_id} not found or has no resume text")

    # 2. Skip if already parsed (has skills)
    if candidate.skills and len(candidate.skills) > 0:
        # Return a mock or empty ParsedResume if the caller expects one, 
        # but runner.py doesn't actually use the return value.
        return None

    # 3. Parse using the core logic
    parsed_result = await parse_resume_text(candidate.resume_text)
    
    # 4. Update candidate record
    candidate.skills = parsed_result.skills
    candidate.experience_years = parsed_result.experience_years
    
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    
    return parsed_result
