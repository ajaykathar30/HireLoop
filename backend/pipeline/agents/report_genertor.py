import os
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class ScoredQuestion(BaseModel):
    question_index: int
    score: float = Field(description="Score from 0 to 20")
    feedback: str = Field(description="Brief feedback for this specific answer")

class FinalInterviewReport(BaseModel):
    individual_scores: List[ScoredQuestion] = Field(description="Scores for each of the 5 questions")
    total_score: float = Field(description="Total score out of 100")
    summary: str = Field(description="A professional 3-4 sentence summary of the candidate's performance")
    strengths: List[str] = Field(description="List of 3 key strengths observed")
    weaknesses: List[str] = Field(description="List of 2-3 areas for improvement")
    overall_recommendation: str = Field(description="Hire, No Hire, or Consider for different role")

async def generate_batch_evaluation_report(job_title: str, job_description: str, qa_list: List[dict]) -> FinalInterviewReport:
    """
    Evaluates all 5 interview answers and generates a final report in a single Gemini call.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )
    
    parser = PydanticOutputParser(pydantic_object=FinalInterviewReport)
    
    conversation = ""
    for i, item in enumerate(qa_list):
        conversation += f"QUESTION {i+1}: {item['question']}\nCANDIDATE ANSWER: {item['answer']}\n\n"
    
    prompt = ChatPromptTemplate.from_template(
        "You are a senior hiring manager. Review the full transcript of a 5-question technical interview for a {title} position. "
        "Your task is to:\n"
        "1. Score each answer individually from 0 to 20 marks based on technical depth and JD relevance.\n"
        "2. Provide a total score out of 100.\n"
        "3. Write a comprehensive hiring report.\n\n"
        "JOB DESCRIPTION:\n{jd}\n\n"
        "INTERVIEW TRANSCRIPT:\n{conversation}\n\n"
        "{format_instructions}"
    )
    
    chain = prompt | llm | parser
    
    result = await chain.ainvoke({
        "title": job_title,
        "jd": job_description,
        "conversation": conversation,
        "format_instructions": parser.get_format_instructions()
    })
    
    return result
