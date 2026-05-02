import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class Question(BaseModel):
    text: str = Field(description="The interview question text")
    type: str = Field(description="Type of question: 'technical', 'behavioral', 'resume_gap', 'follow_up'")

class AnswerEvaluation(BaseModel):
    score: float = Field(description="Score from 0 to 20")
    feedback: str = Field(description="1-2 sentence feedback on the answer")

# ---------------------------------------------------------------------------
# Dynamic Question Generation (Vector Memory Context)
# ---------------------------------------------------------------------------

async def generate_first_question(resume_text: str, job_description: str, job_requirements: str) -> Question:
    """
    Generates the very first introductory/personalized question.
    """
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    
    parser = PydanticOutputParser(pydantic_object=Question)
    
    prompt = ChatPromptTemplate.from_template(
        "You are an expert technical recruiter starting an interview. Based on the candidate's resume and the job description below, "
        "generate the very first introductory/personalized project question to kick off the interview.\n\n"
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
    
    return result

async def generate_next_question(conversation_history: str, job_description: str, question_index: int, rag_context: str = "") -> Question:
    """
    Generates the next question dynamically based on previous interactions (Vector DB context).
    """
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    
    parser = PydanticOutputParser(pydantic_object=Question)
    
    prompt_text = (
        "You are an expert technical recruiter conducting an interview. This is question {question_number} of 5. "
        "Based on the job description and the relevant conversation history from earlier in this interview, generate a highly relevant follow-up question. "
        "If the previous answer lacked detail, ask them to dive deeper into that specific area. If it was complete, pivot to a new technical or behavioral topic.\n\n"
    )
    
    if rag_context:
        prompt_text += (
            "IMPORTANT: Base your next question strictly on the following advanced technical scenario/concept:\n"
            "DEEP DOMAIN KNOWLEDGE:\n{rag_context}\n"
            "Do not ask a basic question. Frame it as a real-world problem the candidate must solve based on the knowledge provided.\n\n"
        )
        
    prompt_text += (
        "JOB DESCRIPTION:\n{jd}\n\n"
        "RELEVANT CONVERSATION HISTORY:\n{history}\n\n"
        "{format_instructions}"
    )

    prompt = ChatPromptTemplate.from_template(prompt_text)
    
    chain = prompt | llm | parser
    
    result = await chain.ainvoke({
        "question_number": question_index + 1,
        "jd": job_description,
        "history": conversation_history,
        "rag_context": rag_context,
        "format_instructions": parser.get_format_instructions()
    })
    
    return result

# ---------------------------------------------------------------------------
# evaluate_interview_answer (Legacy check - replaced by batch report)
# ---------------------------------------------------------------------------

async def evaluate_interview_answer(question: str, candidate_answer: str, job_description: str) -> AnswerEvaluation:
    """
    Evaluates a single answer on a scale of 0-20.
    """
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
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
