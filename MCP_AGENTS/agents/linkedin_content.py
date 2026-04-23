"""
RecruitSight — LinkedIn Content & Thought Leadership Agent
Analyzes the candidate's posts and content to evaluate how they communicate,
what they know, and whether they contribute to their professional community —
or if their LinkedIn is just a static, dormant resume.

Uses gemini-2.5-flash for content analysis.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.linkedin_schemas import (
    LinkedInContentOutput,
    LinkedInProfileOutput,
)
from tools.linkedin_tools import fetch_linkedin_context

logger = logging.getLogger("recruitsight.linkedin_content")

SYSTEM_PROMPT = """You are the LinkedIn Content & Thought Leadership Agent for RecruitSight.

You analyze a candidate's LinkedIn posting activity and content quality.

Your responsibilities:
1. Analyze the candidate's posts (if any are visible from the scraped data).
   Look for post content, topics, engagement signals in the extracted text.

2. For each post or piece of content, evaluate:
   - Topic: What is this post about?
   - Type: Original content / Reshare / Announcement / Motivational / Job update
   - Technical depth: Does it demonstrate real expertise or surface-level buzzwords?
   - Engagement: Reactions + comments count (if visible)

3. Categorize PRIMARY TOPICS into:
   - Technical (code, architecture, tools, frameworks)
   - Career advice or job updates
   - Project announcements or achievements
   - Motivational / hustle content
   - Reshares with no original commentary added

4. Evaluate EXPERTISE ALIGNMENT:
   - Do post topics match their claimed role and skills?
   - "ML Engineer" only posting soft skills content = misalignment signal
   - "Backend Developer" writing deep system design posts = strong signal

5. Evaluate COMMUNICATION QUALITY:
   - Well-structured and clearly written?
   - Technical concepts explained accurately?
   - Or vague, buzzword-heavy, grammatically poor?

6. Assign THOUGHT LEADERSHIP LEVEL:
   - "None": No posts at all (neutral — not a red flag by itself)
   - "Emerging": Occasional relevant posts, low engagement
   - "Established": Regular posting, peer engagement in comments
   - "Influential": High engagement, industry figures engaging with their work

7. Flag CONCERNS:
   - Posts contradicting professional claims
   - Only motivational content, zero technical substance
   - Posting frequency suddenly spiked before job search (burst signal)

CRITICAL RULES:
- Use ALL available information. If post data isn't directly visible, infer from
  metadata, profile activity signals, and any text fragments.
- If no posts are found, set thought_leadership_level to "none" and provide
  honest assessment that the profile appears content-inactive.
- Be fair — not everyone posts on LinkedIn, and that's not inherently negative.

Provide your analysis as a structured JSON response."""


async def linkedin_content_agent(
    linkedin_url: str,
    profile_data: LinkedInProfileOutput | None,
    scraped_context: str = "",
) -> LinkedInContentOutput | None:
    """
    Analyze a candidate's LinkedIn content and thought leadership.
    
    Args:
        linkedin_url: The LinkedIn profile URL
        profile_data: Output from the Profile Intelligence agent
        scraped_context: Pre-fetched LinkedIn context string
        
    Returns:
        LinkedInContentOutput with content evaluation, or None on failure
    """
    logger.info(f"✍️ LinkedIn Content & Thought Leadership Agent analyzing: {linkedin_url}")

    if not scraped_context:
        scraped_context = await fetch_linkedin_context(linkedin_url)

    # Build context from profile agent output
    profile_context = ""
    if profile_data:
        profile_context = f"""
PROFILE AGENT CONTEXT (from Agent 1):
- Full Name: {profile_data.full_name}
- Current Role: {profile_data.current_role}
- Headline: {profile_data.headline}
- Top Skills: {', '.join(profile_data.top_skills[:10])}
- Total Experience: {profile_data.total_experience_years} years
"""

    user_content = f"""Analyze the content and thought leadership of this LinkedIn profile:

{scraped_context}

{profile_context}

Evaluate their posting activity, content quality, topic alignment with their
claimed expertise, and overall thought leadership level. Look for any post
content, activity signals, or engagement indicators in the scraped data.

If no post content is directly visible, provide an honest assessment based on
whatever signals are available."""

    result = await run_agent(
        agent_name="LinkedIn Content & Thought Leadership",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=LinkedInContentOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(
            f"✅ LinkedIn Content complete. "
            f"Leadership: {result.thought_leadership_level.value}, "
            f"Score: {result.content_score}/10"
        )
    return result
