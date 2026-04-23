"""
RecruitSight — File Structure Analyst Agent
Analyzes the repository's folder and file structure to determine whether it
represents a real, thoughtfully designed project or a cloned template/boilerplate.
Uses gemini-2.5-flash for fast structured extraction.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.schemas import FileStructureOutput
from tools.git_tools import get_directory_tree, list_files, git_show, get_file_extensions_summary

logger = logging.getLogger("recruitsight.file_structure")

SYSTEM_PROMPT = """You are the File Structure Analyst Agent for RecruitSight.

Your responsibilities:
1. Map the complete directory tree (all folders and files, up to 4 levels deep).
2. Identify the project type (web app, CLI tool, API, ML model, library, mobile, etc.)
3. Evaluate structural quality using these signals:
   - Are there meaningful folder separations (src/, tests/, docs/, config/)?
   - Is there a proper .gitignore? What does it exclude?
   - Are there environment config files (.env.example, config.yaml)?
   - Is there a proper test directory with actual test files?
   - Are there CI/CD configuration files (.github/workflows/, Makefile, Dockerfile)?
   - Does the folder structure match the claimed project type?
4. Detect boilerplate red flags:
   - Presence of default template files (e.g., create-react-app defaults unchanged)
   - No customization in config files
   - Generic placeholder names in files
5. Score the structure on a scale of 1-10.

Your core principles:
- EVIDENCE OVER CLAIMS — every conclusion must be backed by specific file paths.
- NO HALLUCINATION — if you cannot verify something, say "UNVERIFIABLE".
- FAIRNESS — flag both red flags AND genuine strengths."""


async def file_structure_agent(local_path: str, repo_name: str) -> FileStructureOutput | None:
    """
    Analyze the file structure of a cloned repository.

    Gathers directory tree and file metadata locally, then sends
    to Gemini for structured analysis.
    """
    logger.info(f"🗂️ File Structure Agent analyzing: {repo_name}")

    # Gather data locally
    dir_tree = get_directory_tree(local_path, max_depth=4)
    all_files = list_files(local_path)
    ext_summary = get_file_extensions_summary(local_path)

    # Read key config files if they exist
    config_files = {}
    config_candidates = [
        ".gitignore", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "Makefile", ".env.example", "config.yaml", "config.json",
        "tsconfig.json", "pyproject.toml", "setup.py", "setup.cfg",
    ]
    for cfg in config_candidates:
        content = git_show(local_path, cfg)
        if content:
            config_files[cfg] = content[:1000]

    # Detect CI/CD files
    ci_files = [
        f for f in all_files
        if ".github/workflows" in f.replace("\\", "/")
        or "Jenkinsfile" in f
        or ".gitlab-ci" in f
        or "circle.yml" in f
    ]

    user_content = f"""Analyze this repository's file structure:

REPOSITORY NAME: {repo_name}

DIRECTORY TREE:
{dir_tree}

TOTAL FILES: {len(all_files)}

FILE EXTENSION BREAKDOWN:
{json.dumps(ext_summary, indent=2)}

CONFIG FILES FOUND:
{json.dumps(list(config_files.keys()), indent=2)}

CONFIG FILE CONTENTS:
{json.dumps(config_files, indent=2)}

CI/CD FILES: {json.dumps(ci_files)}

ALL FILES LIST (first 200):
{json.dumps(all_files[:200], indent=2)}

Analyze the structure and provide your assessment."""

    result = await run_agent(
        agent_name="File Structure Analyst",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=FileStructureOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(f"✅ File Structure Agent complete. Score: {result.structure_score}/10")
    return result
