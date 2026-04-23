"""
RecruitSight — Dependency Auditor Agent
Analyzes the project's dependencies to evaluate technical maturity,
appropriateness of library choices, and detect over-reliance on heavy frameworks.
Uses gemini-2.5-flash for structured extraction.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.schemas import DependencyAuditOutput
from tools.git_tools import git_show, list_files

logger = logging.getLogger("recruitsight.dependency_auditor")

SYSTEM_PROMPT = """You are the Dependency Auditor Agent for RecruitSight.

Your responsibilities:
1. Analyze the dependency files provided to you: package.json, requirements.txt,
   Cargo.toml, pom.xml, go.mod, Gemfile, pubspec.yaml — whichever apply.
2. List all dependencies (production + development separately if possible).
3. Evaluate DEPENDENCY APPROPRIATENESS:
   - Are the libraries a sensible fit for the stated problem?
   - Are heavy frameworks used for simple tasks? (e.g., Express for a static page)
   - Are there multiple libraries solving the same problem (dependency confusion)?
   - Are dependencies pinned to specific versions (good practice)?
4. Check for SECURITY RED FLAGS:
   - Any known deprecated or vulnerable packages?
   - Are there packages that seem unrelated to the project purpose?
5. Evaluate DEPENDENCY MATURITY:
   - Does the candidate use battle-tested, popular libraries?
   - Or do they rely on obscure, unmaintained, or personal forks?
6. Check if a lock file exists (package-lock.json, poetry.lock, etc.) — good practice.

Your core principles:
- EVIDENCE OVER CLAIMS — cite specific package names and versions.
- NO HALLUCINATION — only analyze dependencies you can see.
- FAIRNESS — flag both red flags AND genuine strengths."""


async def dependency_auditor_agent(
    local_path: str, project_type: str = "unknown"
) -> DependencyAuditOutput | None:
    """
    Audit the dependencies of a repository.
    
    Reads all dependency files, checks for lock files, then sends
    to Gemini for appropriateness analysis.
    """
    logger.info(f"📦 Dependency Auditor Agent analyzing: {local_path}")

    # Possible dependency files
    dep_file_candidates = [
        "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "requirements.txt", "requirements.in", "Pipfile", "Pipfile.lock",
        "pyproject.toml", "poetry.lock", "setup.py", "setup.cfg",
        "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum",
        "pom.xml", "build.gradle", "build.gradle.kts",
        "Gemfile", "Gemfile.lock",
        "pubspec.yaml", "pubspec.lock",
        "composer.json", "composer.lock",
    ]

    all_files = list_files(local_path)
    
    # Read dependency files
    dep_files_content = {}
    lock_files_found = []
    for df in dep_file_candidates:
        # Check in root and common subdirs
        for prefix in ["", "backend/", "frontend/", "server/", "client/", "app/"]:
            path = prefix + df
            if path in all_files or path.replace("/", "\\") in all_files:
                content = git_show(local_path, path, max_bytes=30000)
                if content:
                    dep_files_content[path] = content
                    if "lock" in df.lower() or df.endswith(".sum"):
                        lock_files_found.append(path)

    if not dep_files_content:
        logger.warning("No dependency files found")
        # Still run the agent to note the absence
    
    user_content = f"""Analyze the dependencies of this repository:

PROJECT TYPE: {project_type}

DEPENDENCY FILES FOUND: {json.dumps(list(dep_files_content.keys()))}
LOCK FILES FOUND: {json.dumps(lock_files_found)}

DEPENDENCY FILE CONTENTS:
"""
    
    for filepath, content in dep_files_content.items():
        user_content += f"\n{'='*60}\nFILE: {filepath}\n{'='*60}\n{content}\n"

    user_content += "\nProvide your dependency audit assessment."

    result = await run_agent(
        agent_name="Dependency Auditor",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=DependencyAuditOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(f"✅ Dependency Audit complete. Score: {result.dependency_appropriateness_score}/10")
    return result
