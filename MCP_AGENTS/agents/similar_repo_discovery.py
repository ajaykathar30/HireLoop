"""
RecruitSight — Similar Repo Discovery Agent
Uses the Exa web search API to find GitHub repositories and projects
that are conceptually and technically similar to the candidate's project.
Feeds both the Plagiarism Agent and the Uniqueness Agent.
Uses gemini-2.5-flash for query formulation and result analysis.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.schemas import SimilarRepoOutput
from tools.exa_tools import search_similar_repos, search_web_context

logger = logging.getLogger("recruitsight.similar_repo")

SYSTEM_PROMPT = """You are the Similar Repo Discovery Agent for RecruitSight.

You have been given a candidate's project details and the results of web searches
for similar repositories. Your job is to analyze these search results and determine:

1. Which results are genuinely similar GitHub repositories.
2. For each similar repo, assess:
   - How similar it is conceptually (same problem domain)
   - Whether it could be a SOURCE the candidate copied from
   - Whether it's a tutorial/starter project
3. Determine if the candidate's project resembles a common tutorial project
   (e.g., todo app, weather app, CRUD app).
4. Return top 5-10 most relevant similar repositories.

Your core principles:
- EVIDENCE OVER CLAIMS — base similarity assessment on actual search result data.
- NO HALLUCINATION — only report repos that appeared in the search results.
- FAIRNESS — not all similar repos indicate plagiarism; common patterns are normal."""


async def similar_repo_discovery_agent(
    repo_name: str,
    project_type: str,
    primary_language: str = "unknown",
    key_libraries: list[str] | None = None,
    readme_summary: str = "",
) -> SimilarRepoOutput | None:
    """
    Discover similar repositories using Exa web search.

    Formulates targeted search queries, executes via Exa SDK,
    then sends all results to Gemini for analysis and classification.
    """
    logger.info(f"🔍 Similar Repo Discovery Agent searching for repos like: {repo_name}")

    libs = key_libraries or []

    # Formulate search queries
    queries = [
        f"github {project_type} {primary_language} project",
        f"github {repo_name} similar repository",
        f"github {' '.join(libs[:3])} tutorial" if libs else f"github {project_type} tutorial",
        f"github {project_type} {primary_language} starter template boilerplate",
    ]
    if readme_summary:
        queries.append(f"github {readme_summary[:100]}")

    # Execute all Exa searches
    all_results = []
    for query in queries:
        logger.info(f"  Searching Exa: {query}")
        results = search_similar_repos(query, num_results=5)
        all_results.extend(results)

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    logger.info(f"  Found {len(unique_results)} unique results across {len(queries)} queries")

    user_content = f"""Analyze these search results to find repositories similar to the candidate's project:

CANDIDATE PROJECT:
- Name: {repo_name}
- Type: {project_type}
- Primary Language: {primary_language}
- Key Libraries: {json.dumps(libs)}
- README Summary: {readme_summary[:300] if readme_summary else "N/A"}

SEARCH QUERIES USED:
{json.dumps(queries, indent=2)}

SEARCH RESULTS ({len(unique_results)} unique results):
{json.dumps(unique_results, indent=2)}

Analyze each result for conceptual similarity, tutorial-match potential, and whether
it could be a source the candidate copied from. Return only results that are
genuinely relevant."""

    result = await run_agent(
        agent_name="Similar Repo Discovery",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=SimilarRepoOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(
            f"✅ Similar Repo Discovery complete. "
            f"Found {len(result.similar_repos)} similar repos, "
            f"Tutorial match: {result.is_common_tutorial_project}"
        )
    return result
