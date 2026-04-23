"""
RecruitSight — README vs Reality Agent
Compares what the README claims the project does against what the code
actually implements. Detects over-claiming and under-delivery.
Uses gemini-2.5-flash for cross-referencing.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_FLASH
from models.schemas import ReadmeRealityOutput
from tools.git_tools import git_show, git_search_code, list_files

logger = logging.getLogger("recruitsight.readme_reality")

SYSTEM_PROMPT = """You are the README vs Reality Agent for RecruitSight.

Your responsibilities:
1. Read the README content provided to you.
2. Extract all CLAIMS made in the README:
   - Feature list
   - Technology stack claims
   - Architecture claims ("microservices", "real-time", "scalable")
   - Performance claims ("handles 10k requests/second")
   - Setup/installation instructions
3. For each major claim, verify against the actual code provided:
   - Does the code implement the feature described?
   - Is the claimed tech stack actually used?
   - Are setup instructions accurate and complete?
4. Classify each claim as:
   - VERIFIED — code confirms the claim
   - PARTIAL — code has basic implementation but not the full claim
   - UNVERIFIABLE — claim cannot be confirmed from code alone
   - FALSE — code clearly contradicts the claim
5. Calculate a README Honesty Score from 1-10.

Your core principles:
- EVIDENCE OVER CLAIMS — cite specific file paths and code patterns as evidence.
- NO HALLUCINATION — if you cannot find evidence for or against a claim, mark it UNVERIFIABLE.
- FAIRNESS — recognize both accurate and inaccurate claims."""


async def readme_reality_agent(local_path: str) -> ReadmeRealityOutput | None:
    """
    Compare README claims against actual code implementation.
    
    Reads the README and key source files, searches for claimed
    features in code, then sends to Gemini for verification.
    """
    logger.info(f"📖 README vs Reality Agent analyzing: {local_path}")

    # Find and read README
    readme_content = ""
    readme_candidates = [
        "README.md", "readme.md", "Readme.md",
        "README.rst", "README.txt", "README",
    ]
    for candidate in readme_candidates:
        content = git_show(local_path, candidate)
        if content:
            readme_content = content
            break

    if not readme_content:
        logger.warning("No README found")
        # Return a minimal result
        return ReadmeRealityOutput(
            readme_exists=False,
            readme_length="minimal",
            claims_analyzed=[],
            verified_count=0,
            false_count=0,
            honesty_score=5,
            overall_impression="accurate",
            summary="No README file found in the repository. Cannot perform claim verification.",
        )

    # Gather supporting evidence from the codebase
    all_files = list_files(local_path)
    
    # Read key implementation files to cross-reference
    key_files_content = {}
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".rb", ".php"}
    code_files = [f for f in all_files if any(f.endswith(ext) for ext in code_extensions)]
    
    # Sample up to 10 code files for verification
    for f in code_files[:10]:
        content = git_show(local_path, f, max_bytes=8000)
        if content:
            key_files_content[f] = content

    # Read dependency files for tech stack verification
    dep_files = {}
    for dep_name in ["package.json", "requirements.txt", "Cargo.toml", "go.mod", "pyproject.toml", "Gemfile"]:
        content = git_show(local_path, dep_name)
        if content:
            dep_files[dep_name] = content[:5000]

    # Search for common feature keywords
    feature_searches = {}
    keywords = ["auth", "login", "database", "websocket", "real-time", "api", "test", "deploy"]
    for kw in keywords:
        results = git_search_code(local_path, kw)
        if results:
            feature_searches[kw] = results[:5]

    user_content = f"""Compare the README claims against the actual code:

README CONTENT:
{readme_content}

ALL FILES IN REPO ({len(all_files)} total, showing first 100):
{json.dumps(all_files[:100], indent=2)}

DEPENDENCY FILES:
{json.dumps(dep_files, indent=2)}

KEY SOURCE FILES:
"""
    
    for filepath, content in key_files_content.items():
        user_content += f"\n{'='*60}\nFILE: {filepath}\n{'='*60}\n{content}\n"

    user_content += f"""

FEATURE KEYWORD SEARCH RESULTS:
{json.dumps(feature_searches, indent=2)}

Verify each README claim against the code evidence and provide your assessment."""

    result = await run_agent(
        agent_name="README vs Reality",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=ReadmeRealityOutput,
        model=MODEL_FLASH,
    )

    if result:
        logger.info(f"✅ README vs Reality complete. Honesty: {result.honesty_score}/10, Impression: {result.overall_impression}")
    return result
