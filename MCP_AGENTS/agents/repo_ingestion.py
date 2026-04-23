"""
RecruitSight — Repo Ingestion Agent
Clones the candidate's GitHub repository and validates it.
Uses subprocess for git operations (not LLM-driven).
"""

import logging
import re
from datetime import datetime, timezone

from config import CLONE_BASE_DIR
from models.schemas import RepoIngestionOutput, IngestionStatus
from tools.git_tools import git_clone, git_log, git_branch

logger = logging.getLogger("recruitsight.repo_ingestion")


def parse_github_url(url: str) -> tuple[str, str] | None:
    """
    Extract owner and repo name from a GitHub URL.
    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    """
    # HTTPS format
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip()
    )
    if match:
        return match.group(1), match.group(2)

    # SSH format
    match = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", url.strip())
    if match:
        return match.group(1), match.group(2)

    return None


async def repo_ingestion_agent(repo_url: str) -> RepoIngestionOutput:
    """
    Repo Ingestion Agent — clones and validates a GitHub repository.
    
    This agent doesn't use the LLM at all — it's pure Python logic
    because the task is deterministic (clone, validate, count commits).
    
    Input: GitHub repository URL
    Output: RepoIngestionOutput with clone path and metadata
    """
    logger.info(f"🔄 Repo Ingestion Agent starting for: {repo_url}")

    # 1. Parse the URL
    parsed = parse_github_url(repo_url)
    if parsed is None:
        logger.error(f"Invalid GitHub URL: {repo_url}")
        return RepoIngestionOutput(
            status=IngestionStatus.FAILED,
            local_path="",
            owner="",
            repo_name="",
            default_branch="",
            total_commits=0,
            clone_timestamp=datetime.now(timezone.utc).isoformat(),
            error=f"Invalid GitHub URL format: {repo_url}",
        )

    owner, repo_name = parsed
    target_dir = str(CLONE_BASE_DIR / f"{owner}_{repo_name}")

    # 2. Clone the repository
    logger.info(f"Cloning {repo_url} to {target_dir}...")
    success = git_clone(repo_url, target_dir)
    if not success:
        return RepoIngestionOutput(
            status=IngestionStatus.FAILED,
            local_path=target_dir,
            owner=owner,
            repo_name=repo_name,
            default_branch="",
            total_commits=0,
            clone_timestamp=datetime.now(timezone.utc).isoformat(),
            error="Failed to clone repository. It may be private, deleted, or inaccessible.",
        )

    # 3. Verify clone — check for commits
    commits = git_log(target_dir, max_count=1)
    if not commits:
        return RepoIngestionOutput(
            status=IngestionStatus.FAILED,
            local_path=target_dir,
            owner=owner,
            repo_name=repo_name,
            default_branch="",
            total_commits=0,
            clone_timestamp=datetime.now(timezone.utc).isoformat(),
            error="Repository appears to be empty (no commits found).",
        )

    # 4. Get metadata
    default_branch = git_branch(target_dir)
    all_commits = git_log(target_dir, max_count=10000)
    total_commits = len(all_commits)

    logger.info(
        f"✅ Repo Ingestion complete: {owner}/{repo_name}, "
        f"{total_commits} commits, branch: {default_branch}"
    )

    return RepoIngestionOutput(
        status=IngestionStatus.SUCCESS,
        local_path=target_dir,
        owner=owner,
        repo_name=repo_name,
        default_branch=default_branch,
        total_commits=total_commits,
        clone_timestamp=datetime.now(timezone.utc).isoformat(),
        error=None,
    )
