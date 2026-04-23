"""
RecruitSight — LinkedIn Achievement & Credibility Agent
Verifies and scores the candidate's external validation — certifications,
endorsements, and honors.
Uses gemini-2.5-flash for credibility analysis.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.linkedin_schemas import (
    LinkedInCredibilityOutput,
    LinkedInProfileOutput,
)
from tools.linkedin_tools import fetch_linkedin_context

logger = logging.getLogger("recruitsight.linkedin_credibility")

SYSTEM_PROMPT = """You are the LinkedIn Achievement & Credibility Agent for RecruitSight.

Your responsibilities:
1. Evaluate CERTIFICATIONS: issuer reputation, currency, role relevance,
   clustering patterns, cert-collector signals.
2. Evaluate SKILL ENDORSEMENT CREDIBILITY: relevance to role, proportionality
   to experience, buzzword bloat.
3. Evaluate HONORS & AWARDS: external vs self-reported, recency, relevance.
4. Flag NOTABLE ABSENCES: expected certs missing for claimed role.
5. Calculate CREDIBILITY SCORE:
   Cert quality+relevance 40% + Skill endorsements 30% + Honors 30%

RULES:
- Use Profile Intelligence Agent data as primary source.
- Be fair — not everyone pursues certifications.
- Consider career stage when evaluating.
- Clearly note when data is limited.

Provide structured JSON response."""


async def linkedin_credibility_agent(
    linkedin_url: str,
    profile_data: LinkedInProfileOutput | None,
    scraped_context: str = "",
) -> LinkedInCredibilityOutput | None:
    """Evaluate credibility of a candidate's LinkedIn achievements."""
    logger.info(f"🏆 LinkedIn Credibility Agent analyzing: {linkedin_url}")

    if not scraped_context:
        scraped_context = await fetch_linkedin_context(linkedin_url)

    profile_context = ""
    if profile_data:
        certs_json = json.dumps(
            [c.model_dump() for c in profile_data.certifications], indent=2
        )
        profile_context = f"""
PROFILE AGENT CONTEXT:
- Name: {profile_data.full_name}
- Role: {profile_data.current_role}
- Experience: {profile_data.total_experience_years} years
- Skills: {', '.join(profile_data.top_skills[:10])}
- Certifications: {certs_json}
- Honors: {', '.join(profile_data.honors_awards) if profile_data.honors_awards else 'None'}
"""

    user_content = f"""Evaluate achievement and credibility for this LinkedIn profile:

{scraped_context}

{profile_context}

Analyze certifications, skill endorsements, honors, and notable absences.
Calculate an overall credibility score."""

    result = await run_agent(
        agent_name="LinkedIn Achievement & Credibility",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=LinkedInCredibilityOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(
            f"✅ LinkedIn Credibility complete. "
            f"Pattern: {result.certification_pattern.value}, "
            f"Score: {result.credibility_score}/10"
        )
    return result
