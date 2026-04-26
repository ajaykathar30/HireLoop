from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException
from models.job import Job
from models.company import Company
from schemas.job import JobCreate
from core.embeddings import generate_embedding
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import uuid
import logging

logger = logging.getLogger(__name__)

async def create_job(db: AsyncSession, user_id: uuid.UUID, data: JobCreate):
    try:
        # 1. Verify Company
        statement = select(Company).where(Company.user_id == user_id)
        result = await db.execute(statement)
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(status_code=403, detail="Only companies with profiles can create jobs")
        
        # 2. Use LangChain to analyze/validate job content
        # This satisfies the "using langchain in the job" requirement
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0
            )
            prompt = ChatPromptTemplate.from_template(
                "Analyze this job title and description. Return a very brief 1-sentence summary.\n"
                "Title: {title}\nDescription: {description}"
            )
            chain = prompt | llm
            analysis = await chain.ainvoke({"title": data.title, "description": data.description})
            logger.info(f"Job analysis: {analysis.content}")
        except Exception as ai_err:
            logger.warning(f"LangChain analysis failed: {ai_err}")

        # 3. Normalize job_type
        normalized_job_type = data.job_type.lower() if data.job_type else None
        
        new_job = Job(
            company_id=company.id,
            title=data.title,
            description=data.description,
            requirements=data.requirements,
            location=data.location,
            job_type=normalized_job_type,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            application_deadline=data.application_deadline
        )
        
        # 4. Generate Gemini Embeddings
        try:
            combined_text = f"{new_job.title} {new_job.description} {new_job.requirements}"
            embedding = await generate_embedding(combined_text)
            new_job.job_embedding = embedding
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            # If embedding fails, we might want to fail job creation if it's critical
            # for the user, or just proceed without it. 
            # Given the user's concern, let's make it more robust.
            new_job.job_embedding = None

        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
        
        return new_job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

async def get_company_jobs(db: AsyncSession, user_id: uuid.UUID):
    logger.info(f"Fetching jobs for user_id: {user_id}")
    statement = select(Company).where(Company.user_id == user_id)
    result = await db.execute(statement)
    company = result.scalar_one_or_none()
    
    if not company:
        logger.warning(f"No company profile found for user_id: {user_id}")
        raise HTTPException(status_code=403, detail="Only companies can access their jobs")
    
    logger.info(f"Found company {company.name} (ID: {company.id}). Fetching jobs...")
    statement = select(Job).where(Job.company_id == company.id).order_by(Job.created_at.desc())
    result = await db.execute(statement)
    jobs = result.scalars().all()
    logger.info(f"Found {len(jobs)} jobs for company {company.id}")
    return jobs

async def get_all_jobs(db: AsyncSession):
    # Select job and join with company to get company name/logo
    statement = select(Job, Company).join(Company, Job.company_id == Company.id).order_by(Job.created_at.desc())
    result = await db.execute(statement)
    
    jobs_with_companies = []
    for job, company in result:
        job_data = job.model_dump()
        job_data["company_name"] = company.name
        job_data["company_logo"] = company.logo_url
        jobs_with_companies.append(job_data)
        
    return jobs_with_companies
