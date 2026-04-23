"""
RecruitSight — Real-World Value & Uniqueness Agent
Evaluates whether the project addresses a genuine, current real-world problem
or is a tired solution to an already-saturated problem with no differentiation.
Uses gemini-2.5-pro for market context reasoning + Exa for web research.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_PRO
from models.schemas import (
    UniquenessOutput,
    SimilarRepoOutput,
    ReadmeRealityOutput,
    CodeQualityOutput,
)
from tools.exa_tools import search_web_context

logger = logging.getLogger("recruitsight.uniqueness")

SYSTEM_PROMPT = """You are the Real-World Value & Uniqueness Agent for RecruitSight.

Your responsibilities:
1. Classify the project into one of these categories:
   - TUTORIAL_CLONE: A well-known tutorial project (todo app, weather app, CRUD app)
   - SATURATED_SPACE: Real idea but done by thousands (another social media clone,
     another task manager, another chat app with nothing new)
   - INCREMENTAL: Solves a real problem but in a space already well-served with
     minor improvements or a different angle
   - GENUINELY_USEFUL: Addresses a specific real pain point that isn't oversaturated
   - INNOVATIVE: Novel approach, unique problem, or creative combination of ideas

2. Based on the web research results provided, assess:
   - "Is there a real market or community need for this type of project?"
   - "What are the most common beginner projects in this language/framework?"
   - "Are there existing popular solutions that make this project redundant?"

3. Evaluate the candidate's DIFFERENTIATION:
   - Even if the problem is saturated, did the candidate add something unique?
   - Is there a specific niche or user group this serves better than alternatives?
   - Does the tech stack choice add value (e.g., performance, accessibility)?

4. Consider project COMPLETION and AMBITION:
   - A half-finished ambitious project may show more potential than a complete
     but trivial one.

Your core principles:
- EVIDENCE OVER CLAIMS — base assessment on the web research data provided.
- NO HALLUCINATION — only reference information from the search results.
- FAIRNESS — even common projects can demonstrate skill if well-executed."""


async def uniqueness_value_agent(
    repo_name: str,
    project_type: str,
    similar_repos: SimilarRepoOutput | None,
    readme_output: ReadmeRealityOutput | None,
    code_quality: CodeQualityOutput | None,
    is_common_tutorial: bool = False,
    completion_level: str = "unknown",
) -> UniquenessOutput | None:
    """
    Evaluate the real-world value and uniqueness of a project.
    
    Conducts web research via Exa for market context, then sends
    all data to Gemini Pro for assessment.
    """
    logger.info(f"🌍 Uniqueness & Value Agent analyzing: {repo_name}")

    # Conduct web research for market context
    primary_lang = code_quality.primary_language if code_quality else "unknown"
    
    research_queries = [
        f"Is there a need for {project_type} projects in {primary_lang} 2025 2026",
        f"most common beginner projects {primary_lang} tutorial",
        f"existing popular {project_type} applications alternatives",
    ]

    web_research = {}
    for query in research_queries:
        logger.info(f"  Researching: {query}")
        results = search_web_context(query, num_results=3)
        web_research[query] = results

    # Gather similar repo data
    similar_repos_data = []
    if similar_repos:
        similar_repos_data = [
            {
                "url": r.url,
                "name": r.name,
                "description": r.description,
                "similarity_type": r.similarity_type.value,
                "is_tutorial": r.is_tutorial_project,
                "stars": r.stars,
            }
            for r in similar_repos.similar_repos
        ]

    # Gather README claims
    readme_claims = []
    if readme_output and readme_output.claims_analyzed:
        readme_claims = [
            {"claim": c.claim, "status": c.status.value}
            for c in readme_output.claims_analyzed
        ]

    user_content = f"""Evaluate the real-world value and uniqueness of this project:

PROJECT DETAILS:
- Name: {repo_name}
- Type: {project_type}
- Primary Language: {primary_lang}
- Completion Level: {completion_level}
- Is Common Tutorial: {is_common_tutorial}

README CLAIMS:
{json.dumps(readme_claims, indent=2)}

SIMILAR REPOSITORIES:
{json.dumps(similar_repos_data, indent=2)}

WEB RESEARCH ON MARKET CONTEXT:
{json.dumps(web_research, indent=2)}

CODE QUALITY SUMMARY:
{json.dumps(code_quality.model_dump() if code_quality else {}, indent=2)}

Provide your assessment of the project's real-world value, uniqueness, and what it reveals about the candidate."""

    result = await run_agent(
        agent_name="Real-World Value & Uniqueness",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=UniquenessOutput,
        model=MODEL_PRO,
    )

    if result:
        logger.info(
            f"✅ Uniqueness analysis complete. "
            f"Category: {result.project_category}, "
            f"Uniqueness: {result.uniqueness_score}/10"
        )
    return result
