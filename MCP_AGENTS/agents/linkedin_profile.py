"""
RecruitSight — LinkedIn Profile Intelligence Agent
The foundation agent that all other LinkedIn agents depend on.
Fetches and analyzes the full structured profile — experience, education,
skills, certifications, honors, and projects.

Uses gemini-2.5-pro for deep profile reasoning.
"""

import logging

from agents.base import run_agent
from config import MODEL_PRO
from models.linkedin_schemas import LinkedInProfileOutput
from tools.linkedin_tools import fetch_linkedin_context

logger = logging.getLogger("recruitsight.linkedin_profile")

SYSTEM_PROMPT = """You are the LinkedIn Profile Intelligence Agent for RecruitSight.

You are given a LinkedIn profile URL and any data that was scraped from the profile.
Your job is to extract and structure the candidate's full professional profile.

Your responsibilities:
1. Extract and structure the EXPERIENCE TIMELINE:
   - All roles: company, title, start date, end date, description
   - Calculate total years of professional experience
   - Flag any employment gaps longer than 6 months
   - Detect promotions within the same company (loyalty + growth signal)

2. Extract EDUCATION:
   - Degrees, institutions, graduation years, specializations if mentioned

3. Extract SKILLS:
   - Top skills and endorsement counts (if visible)

4. Extract CERTIFICATIONS:
   - Name, issuer, date obtained, expiry if present
   - Flag certifications relevant to their claimed role
   - Flag certifications that don't align with their experience (padding signal)
   - Are certs clustered in a short period? (bulk cramming for job search)

5. Extract HONORS & AWARDS:
   - Is it from a credible external body or entirely self-reported?

6. Extract LINKEDIN PROJECTS section:
   - Any projects listed beyond obvious course projects?
   - Do they show real-world application?

7. Evaluate PROFILE COMPLETENESS:
   - Photo present? About section written? All sections filled?
   - About section: generic ("Passionate developer seeking...") vs personalized
     with a specific professional narrative

8. Flag CONSISTENCY ISSUES:
   - Experience years vs skill endorsement levels mismatch
   - Claimed senior role but no detailed experience descriptions

CRITICAL RULES:
- Use ALL available information from the scraped data.
- If LinkedIn blocked scraping and you have limited data, make your BEST inference 
  from the URL, username, metadata, and any training knowledge you have about this profile.
- Clearly distinguish between CONFIRMED data (from scraping) and INFERRED data.
- NEVER hallucinate specific companies or roles — if you don't know, say "Data unavailable".
- Be thorough but honest about data limitations.

Provide your analysis as a structured JSON response."""


async def linkedin_profile_agent(
    linkedin_url: str,
    scraped_context: str = "",
) -> LinkedInProfileOutput | None:
    """
    Analyze a LinkedIn profile to extract full professional data.
    
    This is the foundation agent — all other LinkedIn agents depend
    on its output for context.
    
    Args:
        linkedin_url: The LinkedIn profile URL
        scraped_context: Pre-fetched LinkedIn context string
        
    Returns:
        LinkedInProfileOutput with full profile data, or None on failure
    """
    logger.info(f"🧠 LinkedIn Profile Intelligence Agent analyzing: {linkedin_url}")

    # Fetch context if not provided
    if not scraped_context:
        scraped_context = await fetch_linkedin_context(linkedin_url)

    user_content = f"""Analyze this LinkedIn profile and extract all available professional data:

{scraped_context}

Extract the full professional profile following the schema structure.
Include experience timeline, education, skills, certifications, honors, projects,
profile completeness assessment, and consistency analysis.

If data is limited due to scraping restrictions, use any available metadata
(page title, OG tags, visible text) plus your knowledge to provide the most
comprehensive analysis possible. Mark inferred data clearly."""

    result = await run_agent(
        agent_name="LinkedIn Profile Intelligence",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=LinkedInProfileOutput,
        model=MODEL_PRO,
    )

    if result:
        logger.info(
            f"✅ LinkedIn Profile complete. "
            f"Name: {result.full_name}, "
            f"Experience: {result.total_experience_years} years, "
            f"Completeness: {result.profile_completeness_score}/10"
        )
    return result
