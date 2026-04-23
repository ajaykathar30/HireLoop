"""
RecruitSight — Plagiarism & Originality Agent
Cross-references the candidate's code structure, naming patterns, and logic
against similar repos found by the Similar Repo Discovery Agent to detect copying.
Uses gemini-2.5-pro for deep cross-referencing reasoning.
"""

import json
import logging

from agents.base import run_agent
from config import MODEL_PRO
from models.schemas import PlagiarismOutput, SimilarRepoOutput, FileStructureOutput
from tools.git_tools import git_show, git_search_code, git_log, list_files, get_directory_tree

logger = logging.getLogger("recruitsight.plagiarism")

SYSTEM_PROMPT = """You are the Plagiarism & Originality Agent for RecruitSight.

Your responsibilities:
1. Compare the candidate's file structure against each similar repository structure.
   Structural matches (same folder names, same file names in same locations) are
   strong plagiarism signals.
2. If the similar repo is a tutorial or starter template:
   - Check if default/placeholder content is unchanged in the candidate's repo.
   - Look for tutorial-specific comments that weren't removed.
3. Compare variable names, function names, and class names against patterns
   that might indicate copying.
4. Check commit messages — do any commit messages reference the source repo?
   (e.g., "forked from...", "based on tutorial at...")
5. Assign an Originality Score:
   - 8-10: Clearly original work with unique approaches
   - 5-7: Inspired by existing work but meaningfully extended
   - 3-4: Heavy borrowing with minimal changes
   - 1-2: Near-verbatim copy of existing repository

Your core principles:
- EVIDENCE OVER CLAIMS — cite specific file paths, naming patterns, structural matches.
- NO HALLUCINATION — if you cannot confirm copying, do not claim it.
- FAIRNESS — common patterns (MVC structure, standard configs) are NOT plagiarism.
  Only flag truly suspicious matches. Many projects legitimately share similar structures."""


async def plagiarism_originality_agent(
    local_path: str,
    similar_repos: SimilarRepoOutput | None,
    file_structure: FileStructureOutput | None,
    is_common_tutorial: bool = False,
) -> PlagiarismOutput | None:
    """
    Assess the originality of a repository against similar repos.
    
    Gathers the candidate's code patterns, compares against known
    similar repos, then sends to Gemini Pro for cross-reference analysis.
    """
    logger.info(f"🕵️ Plagiarism & Originality Agent analyzing: {local_path}")

    # Gather candidate's code patterns
    dir_tree = get_directory_tree(local_path, max_depth=3)
    all_files = list_files(local_path)
    commits = git_log(local_path, max_count=50)

    # Check commit messages for source references
    source_references = []
    fork_keywords = ["forked from", "based on", "copied from", "tutorial", "template",
                     "starter", "boilerplate", "cloned from", "inspired by"]
    for commit in commits:
        msg = commit.get("message", "").lower()
        for kw in fork_keywords:
            if kw in msg:
                source_references.append({
                    "hash": commit["hash"][:8],
                    "message": commit["message"],
                    "keyword": kw,
                })

    # Search for tutorial remnants
    tutorial_patterns = git_search_code(local_path, "tutorial\\|example\\|sample\\|placeholder\\|TODO: replace")

    # Get similar repos info
    similar_repos_data = []
    if similar_repos:
        similar_repos_data = [
            {
                "url": r.url,
                "name": r.name,
                "description": r.description,
                "similarity_type": r.similarity_type.value,
                "is_tutorial": r.is_tutorial_project,
            }
            for r in similar_repos.similar_repos
        ]

    # Read a few key files for pattern comparison
    key_file_samples = {}
    code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java"}
    code_files = [f for f in all_files if any(f.endswith(ext) for ext in code_exts)]
    for f in code_files[:8]:
        content = git_show(local_path, f, max_bytes=5000)
        if content:
            key_file_samples[f] = content

    user_content = f"""Assess the originality of this repository against known similar repos:

CANDIDATE REPOSITORY STRUCTURE:
{dir_tree}

TOTAL FILES: {len(all_files)}

SIMILAR REPOSITORIES FOUND:
{json.dumps(similar_repos_data, indent=2)}

IS COMMON TUTORIAL PROJECT: {is_common_tutorial}

FILE STRUCTURE FROM ANALYSIS:
{json.dumps(file_structure.model_dump() if file_structure else {}, indent=2)}

COMMIT MESSAGES REFERENCING SOURCES:
{json.dumps(source_references, indent=2)}

TUTORIAL REMNANT PATTERNS FOUND:
{json.dumps(tutorial_patterns[:20], indent=2)}

KEY CODE FILE SAMPLES:
"""
    
    for filepath, content in key_file_samples.items():
        user_content += f"\n{'='*60}\nFILE: {filepath}\n{'='*60}\n{content}\n"

    user_content += "\nAssess originality vs plagiarism with specific evidence."

    result = await run_agent(
        agent_name="Plagiarism & Originality",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=PlagiarismOutput,
        model=MODEL_PRO,
    )

    if result:
        logger.info(f"✅ Plagiarism check complete. Score: {result.originality_score}/10, Verdict: {result.verdict}")
    return result
