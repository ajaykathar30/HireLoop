"""
RecruitSight — LinkedIn Interaction & Engagement Agent
Analyzes HOW the candidate engages with others. Comment quality, who they
interact with, and collaborative behavior reveal professional maturity and
communication style that no resume or portfolio can capture.

Uses gemini-2.5-flash for interaction analysis.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.linkedin_schemas import (
    LinkedInInteractionOutput,
    LinkedInProfileOutput,
    LinkedInContentOutput,
)
from tools.linkedin_tools import fetch_linkedin_context

logger = logging.getLogger("recruitsight.linkedin_interaction")

SYSTEM_PROMPT = """You are the LinkedIn Interaction & Engagement Agent for RecruitSight.

You analyze HOW the candidate engages with others on LinkedIn.

Your responsibilities:
1. Observe the candidate's interaction behavior from available data.
   Look for: comments they've made, reactions, engagement patterns,
   who they interact with, and the nature of their interactions.

2. Evaluate COMMENT QUALITY on other people's posts:
   - Substantive: "This reminds me of X pattern — here's a tradeoff worth noting..."
   - Surface-level: "Great post! 🔥" or "Totally agree!" with nothing added
   - Intellectual: Do they respectfully correct errors? Ask smart follow-ups?
   - Self-promotional: Do they redirect other people's posts toward themselves?

3. Analyze WHO they interact with:
   - Mostly seniors / industry leaders (aspiring, learning signal)
   - Mostly peers in their domain (community engaged signal)
   - Mostly recruiters / hiring managers (actively job hunting signal)
   - Mostly juniors or students (mentorship signal)
   - Indiscriminate with no clear pattern

4. Detect COLLABORATION SIGNALS:
   - Tag teammates or collaborators in project posts?
   - Publicly credit or thank colleagues?
   - Cross-functional engagement (developer engaging with product/design posts)?
   - Share others' work with genuine added commentary (curator signal)?

5. Evaluate PROFESSIONAL TONE:
   - Constructive even in disagreements?
   - Respectful and inclusive language?
   - Any divisive, aggressive, or unprofessional public interactions?

6. Flag RED FLAGS:
   - Zero interaction history (profile created only for job applications)
   - Aggressive or condescending tone in comment threads
   - Interaction activity suddenly spiked in last 2-4 weeks (job hunt burst)
   - Only interacts with their own content (insular signal)

CRITICAL RULES:
- Use ALL available data to infer interaction behavior.
- If direct interaction data isn't visible, use indirect signals: network size
  mentions, any comment text visible, reaction counts, engagement patterns.
- If truly no interaction data is available, honestly report that and base
  the score on the lack of visible engagement (which is itself a signal).
- Be fair — some excellent professionals are simply not active on LinkedIn.

Provide your analysis as a structured JSON response."""


async def linkedin_interaction_agent(
    linkedin_url: str,
    profile_data: LinkedInProfileOutput | None,
    content_data: LinkedInContentOutput | None,
    scraped_context: str = "",
) -> LinkedInInteractionOutput | None:
    """
    Analyze how a candidate engages with others on LinkedIn.
    
    Args:
        linkedin_url: The LinkedIn profile URL
        profile_data: Output from the Profile Intelligence agent
        content_data: Output from the Content & Thought Leadership agent
        scraped_context: Pre-fetched LinkedIn context string
        
    Returns:
        LinkedInInteractionOutput with engagement evaluation, or None on failure
    """
    logger.info(f"🤝 LinkedIn Interaction & Engagement Agent analyzing: {linkedin_url}")

    if not scraped_context:
        scraped_context = await fetch_linkedin_context(linkedin_url)

    # Build context from previous agents
    prev_context = ""
    if profile_data:
        prev_context += f"""
PROFILE AGENT CONTEXT (from Agent 1):
- Full Name: {profile_data.full_name}
- Current Role: {profile_data.current_role}
- Headline: {profile_data.headline}
- Total Experience: {profile_data.total_experience_years} years
"""

    if content_data:
        prev_context += f"""
CONTENT AGENT CONTEXT (from Agent 2):
- Posting Frequency: {content_data.posting_frequency.value}
- Thought Leadership Level: {content_data.thought_leadership_level.value}
- Primary Topics: {', '.join(content_data.primary_topics[:5])}
- Expertise Alignment: {content_data.expertise_alignment.value}
"""

    user_content = f"""Analyze the interaction and engagement behavior of this LinkedIn profile:

{scraped_context}

{prev_context}

Evaluate how this person engages with others: comment quality, who they interact
with, collaboration signals, professional tone, and any red flags or positive signals.

Look for any interaction data, comments, reactions, or engagement patterns in the
scraped data. If interaction data is limited, provide an honest assessment based
on available signals."""

    result = await run_agent(
        agent_name="LinkedIn Interaction & Engagement",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=LinkedInInteractionOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(
            f"✅ LinkedIn Interaction complete. "
            f"Comment Quality: {result.comment_quality.value}, "
            f"Score: {result.interaction_score}/10"
        )
    return result
