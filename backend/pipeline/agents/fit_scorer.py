# pip install langchain-google-genai
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class FitScore(BaseModel):
    score: int = Field(description="Match score from 0 to 100")
    reasoning: str = Field(description="2-3 sentence explanation of the score")
    strengths: List[str] = Field(description="Key strengths matching the job")
    gaps: List[str] = Field(description="Key gaps in experience or skills")

async def score_fit(resume_text: str, job_description: str, job_requirements: str) -> FitScore:
    """
    Scores the fit between a resume and a job description using Gemini AI.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0
    )
    
    structured_llm = llm.with_structured_output(FitScore)
    
    prompt = f"""
    Evaluate the fit between the candidate's resume and the job posting.
    
    RULES:
    - Do not penalize non-traditional educational backgrounds.
    - Focus on actual skills and experience mentioned in the resume.
    - Score strictly based on how well the candidate matches the job requirements.
    
    JOB DESCRIPTION:
    {job_description}
    
    JOB REQUIREMENTS:
    {job_requirements}
    
    CANDIDATE RESUME:
    {resume_text}
    """
    
    fit_result = await structured_llm.ainvoke(prompt)
    return fit_result
