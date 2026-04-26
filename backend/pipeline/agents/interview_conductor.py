import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class Question(BaseModel):
    text: str = Field(description="The interview question text")
    type: str = Field(description="Type of question: 'technical', 'behavioral', 'resume_gap', 'follow_up'")

class InterviewPlan(BaseModel):
    questions: List[Question] = Field(description="List of exactly 5 interview questions")

class AnswerEvaluation(BaseModel):
    score: float = Field(description="Score from 0 to 20")
    feedback: str = Field(description="1-2 sentence feedback on the answer")

# ---------------------------------------------------------------------------
# generate_interview_questions (BATCH)
#
# Generates ALL 5 questions at once to ensure a logical flow.
# ---------------------------------------------------------------------------

async def generate_interview_questions(resume_text: str, job_description: str, job_requirements: str) -> List[Question]:
    """
    Generates 5 tailored interview questions based on the candidate's resume and job details.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )
    
    parser = PydanticOutputParser(pydantic_object=InterviewPlan)
    
    prompt = ChatPromptTemplate.from_template(
        "You are an expert technical recruiter. Based on the candidate's resume and the job description below, "
        "generate exactly 5 interview questions. \n"
        "The questions should follow this flow:\n"
        "1. Introduction/Personalized project question\n"
        "2. Technical question based on a core skill required for the job\n"
        "3. Another technical or problem-solving question\n"
        "4. A behavioral or scenario-based question\n"
        "5. A closing question or 'why this company' based on the role.\n\n"
        "JOB DESCRIPTION:\n{jd}\n\n"
        "JOB REQUIREMENTS:\n{req}\n\n"
        "CANDIDATE RESUME:\n{resume}\n\n"
        "{format_instructions}"
    )
    
    chain = prompt | llm | parser
    
    result = await chain.ainvoke({
        "jd": job_description,
        "req": job_requirements,
        "resume": resume_text,
        "format_instructions": parser.get_format_instructions()
    })
    
    return result.questions[:5]

# ---------------------------------------------------------------------------
# evaluate_interview_answer (Legacy check - replaced by batch report)
# ---------------------------------------------------------------------------

async def evaluate_interview_answer(question: str, candidate_answer: str, job_description: str) -> AnswerEvaluation:
    """
    Evaluates a single answer on a scale of 0-20.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2
    )
    
    parser = PydanticOutputParser(pydantic_object=AnswerEvaluation)
    
    prompt = ChatPromptTemplate.from_template(
        "You are an interviewer. Evaluate the candidate's answer to the following question.\n\n"
        "JOB DESCRIPTION:\n{jd}\n\n"
        "QUESTION: {question}\n"
        "CANDIDATE ANSWER: {answer}\n\n"
        "Score the answer from 0 to 20.\n"
        "{format_instructions}"
    )
    
    chain = prompt | llm | parser
    
    if not candidate_answer or candidate_answer.strip().lower() in ["timeout", "no answer"]:
        return AnswerEvaluation(score=0.0, feedback="No response provided.")

    result = await chain.ainvoke({
        "jd": job_description,
        "question": question,
        "answer": candidate_answer,
        "format_instructions": parser.get_format_instructions()
    })
    
    return result
