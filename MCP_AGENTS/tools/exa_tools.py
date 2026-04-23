"""
RecruitSight — Exa Web Search Tools
Wrapper around the Exa Python SDK for discovering similar repositories
and researching real-world relevance of projects.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("recruitsight.exa_tools")

# Lazy-init the Exa client
_exa_client = None


def _get_exa():
    """Lazily initialize the Exa client."""
    global _exa_client
    if _exa_client is None:
        try:
            from exa_py import Exa
            api_key = os.getenv("EXA_API_KEY")
            if not api_key:
                logger.error("EXA_API_KEY not found in environment")
                return None
            _exa_client = Exa(api_key=api_key)
        except ImportError:
            logger.error("exa-py not installed. Run: pip install exa-py")
            return None
    return _exa_client


def search_similar_repos(
    query: str,
    num_results: int = 10,
    include_domains: Optional[list[str]] = None,
) -> list[dict]:
    """
    Search for similar GitHub repositories using Exa.
    Returns a list of dicts with: url, title, snippet.
    """
    exa = _get_exa()
    if exa is None:
        logger.warning("Exa client not available, returning empty results")
        return []

    try:
        domains = include_domains or ["github.com"]
        results = exa.search_and_contents(
            query,
            num_results=num_results,
            include_domains=domains,
            text={"max_characters": 2000},
            type="auto",
        )

        repos = []
        for r in results.results:
            repos.append({
                "url": r.url,
                "title": r.title or "",
                "snippet": (r.text or "")[:500],
            })
        return repos

    except Exception as e:
        logger.error(f"Exa search failed for query '{query}': {e}")
        return []


def search_web_context(
    query: str,
    num_results: int = 5,
    include_domains: Optional[list[str]] = None,
) -> list[dict]:
    """
    General web search for context (market research, tutorial detection, etc.).
    Returns a list of dicts with: url, title, snippet.
    """
    exa = _get_exa()
    if exa is None:
        logger.warning("Exa client not available, returning empty results")
        return []

    try:
        results = exa.search_and_contents(
            query,
            num_results=num_results,
            include_domains=include_domains or [],
            text={"max_characters": 3000},
            type="auto",
        )

        items = []
        for r in results.results:
            items.append({
                "url": r.url,
                "title": r.title or "",
                "snippet": (r.text or "")[:800],
            })
        return items

    except Exception as e:
        logger.error(f"Exa web search failed for query '{query}': {e}")
        return []
