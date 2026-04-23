"""
RecruitSight — Commit Forensics Agent
Performs forensic analysis of the commit history to determine whether
the candidate genuinely built the project over time or committed it all at once.
Uses gemini-2.5-flash for pattern analysis.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.schemas import CommitForensicsOutput
from tools.git_tools import git_log, git_diff_commit

logger = logging.getLogger("recruitsight.commit_forensics")

SYSTEM_PROMPT = """You are the Commit Forensics Agent for RecruitSight.

Your responsibilities:
1. Analyze the commit log data provided to you including: hash, author name, author email,
   commit date, and commit message.
2. Analyze commit PATTERNS:
   - Total number of commits
   - Time span from first to last commit (in days)
   - Average commits per week
   - Distribution: are commits evenly spread or clustered in 1-2 bursts?
   - Were there commits at suspicious hours (e.g., 500 commits in one night)?
3. Analyze commit MESSAGE quality:
   - Are messages descriptive ("add JWT authentication middleware") or lazy ("update", "fix", "aaa")?
   - Calculate ratio of meaningful vs meaningless commit messages.
4. Analyze commit AUTHORS:
   - Are there multiple authors (collaborative project)?
   - Does the author email match the expected GitHub username pattern?
   - If single author, is that consistent throughout?
5. Detect RED FLAGS:
   - Single massive commit containing the entire project (dump commit)
   - All commits within 24-48 hours despite claimed long development
   - Mismatched author emails across commits (forked and re-committed)
   - Commit messages that are all identical or auto-generated
6. Detect POSITIVE SIGNALS:
   - Commits showing iteration (e.g., feature added, then bug fixed in next commit)
   - Messages following conventional commit format
   - Evidence of debugging/refactoring commits

Your core principles:
- EVIDENCE OVER CLAIMS — cite specific commit hashes and dates.
- NO HALLUCINATION — only analyze the data given to you.
- FAIRNESS — flag both red flags AND genuine strengths."""


async def commit_forensics_agent(local_path: str) -> CommitForensicsOutput | None:
    """
    Perform forensic analysis on the commit history.
    
    Fetches the full commit log locally, optionally gets diff stats
    for key commits, then sends to Gemini for pattern analysis.
    """
    logger.info(f"🔬 Commit Forensics Agent analyzing: {local_path}")

    # Gather commit data
    commits = git_log(local_path, max_count=500)
    
    if not commits:
        logger.warning("No commits found in repository")
        return None

    # Get diff stats for the first commit (to detect dump commits)
    first_commit_diff = ""
    if commits:
        last_commit = commits[-1]  # Oldest commit (git log is newest-first)
        first_commit_diff = git_diff_commit(local_path, last_commit["hash"])

    # Get diff stats for largest commits (by sampling)
    sample_diffs = {}
    sample_indices = [0, len(commits) // 4, len(commits) // 2, 3 * len(commits) // 4]
    for idx in sample_indices:
        if idx < len(commits):
            c = commits[idx]
            diff = git_diff_commit(local_path, c["hash"])
            if diff:
                sample_diffs[c["hash"][:8]] = diff[:500]

    user_content = f"""Analyze this repository's commit history for forensic patterns:

TOTAL COMMITS: {len(commits)}

FULL COMMIT LOG (newest first):
{json.dumps(commits[:200], indent=2)}

{f"REMAINING COMMITS (summary): {len(commits) - 200} more commits not shown" if len(commits) > 200 else ""}

FIRST COMMIT (oldest) DIFF STATS:
{first_commit_diff[:1000] if first_commit_diff else "N/A"}

SAMPLE COMMIT DIFFS:
{json.dumps(sample_diffs, indent=2)}

Analyze the commit patterns, message quality, author consistency, and provide your forensic assessment."""

    result = await run_agent(
        agent_name="Commit Forensics",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=CommitForensicsOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(f"✅ Commit Forensics complete. Verdict: {result.verdict}, Score: {result.authenticity_score}/10")
    return result
