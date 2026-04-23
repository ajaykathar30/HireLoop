"""
RecruitSight — Code Quality & Logic Agent
Evaluates whether the code is logically sound, follows good practices,
and actually does what it claims to do.
Uses gemini-2.5-pro for deep code reasoning.
"""

import json
import logging
from pathlib import Path

from agents.base import run_agent
from config import MODEL_PRO
from models.schemas import CodeQualityOutput
from tools.git_tools import (
    git_show,
    git_search_code,
    list_files,
    get_file_extensions_summary,
)

logger = logging.getLogger("recruitsight.code_quality")

SYSTEM_PROMPT = """You are the Code Quality & Logic Agent for RecruitSight.

Your responsibilities:
1. Identify the primary programming language(s) used.
2. Analyze the key files provided: entry points, core logic files, and utility files.
3. Evaluate CODE LOGIC:
   - Does the logic make sense for the stated problem?
   - Are there obvious algorithmic errors or nonsensical logic?
   - Is there dead code (functions defined but never called)?
   - Are there TODO/FIXME comments indicating incomplete work?
4. Evaluate CODE QUALITY:
   - Is there consistent naming convention?
   - Are functions small and single-purpose or massive and tangled?
   - Is there proper error handling (try/catch, validation)?
   - Are there hardcoded secrets, API keys, or credentials? (CRITICAL red flag)
   - Is there input validation on user-facing functions?
5. Evaluate TEST QUALITY (if tests exist):
   - Are tests meaningful (assert real behavior) or trivial (assert True)?
   - What is the approximate test coverage scope?
   - Are edge cases tested?
6. Check for signs of AI-generated code:
   - Unusually perfect formatting with inconsistent logic
   - Generic variable names (result, data, item) throughout
   - Comments that explain obvious things excessively

Your core principles:
- EVIDENCE OVER CLAIMS — cite specific file paths, function names, line patterns.
- NO HALLUCINATION — only analyze code you can see. If you cannot verify, say UNVERIFIABLE.
- FAIRNESS — flag both red flags AND genuine strengths."""


def _select_key_files(local_path: str, all_files: list[str]) -> list[str]:
    """
    Intelligently select the most important files to sample.
    Prioritizes entry points, core logic, and test files.
    """
    selected = []

    # Priority patterns (order matters)
    priority_patterns = [
        # Entry points
        "main.py", "app.py", "index.py", "server.py", "manage.py",
        "index.js", "index.ts", "app.js", "app.ts", "server.js", "server.ts",
        "main.go", "main.rs", "Main.java", "Program.cs",
        # Core logic (src/ files)
        "src/", "lib/", "core/", "api/", "services/", "controllers/",
        # Config
        "package.json", "requirements.txt", "Cargo.toml", "pom.xml",
        "pyproject.toml", "go.mod", "Gemfile",
        # Tests
        "test", "spec", "__test__",
    ]

    # Categorize files
    entry_points = []
    core_files = []
    test_files = []
    config_files = []
    other_code = []

    code_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
        ".java", ".cs", ".rb", ".php", ".cpp", ".c", ".h",
    }

    for f in all_files:
        name = Path(f).name.lower()
        ext = Path(f).suffix.lower()
        f_lower = f.lower().replace("\\", "/")

        if name in ["main.py", "app.py", "index.js", "index.ts", "app.js",
                     "server.py", "server.js", "manage.py", "main.go", "main.rs"]:
            entry_points.append(f)
        elif "test" in f_lower or "spec" in f_lower:
            test_files.append(f)
        elif any(p in f_lower for p in ["src/", "lib/", "core/", "api/", "services/", "controllers/"]):
            if ext in code_extensions:
                core_files.append(f)
        elif ext in {".json", ".toml", ".yaml", ".yml", ".cfg"}:
            config_files.append(f)
        elif ext in code_extensions:
            other_code.append(f)

    # Build selection: entry points first, then core, then tests, then others
    selected.extend(entry_points[:3])
    selected.extend(core_files[:8])
    selected.extend(test_files[:3])
    selected.extend(config_files[:2])
    
    # Fill up to 15 with other code files
    remaining = 15 - len(selected)
    if remaining > 0:
        selected.extend(other_code[:remaining])

    return selected[:15]


async def code_quality_agent(
    local_path: str, project_type: str = "unknown"
) -> CodeQualityOutput | None:
    """
    Evaluate the code quality and logic of a repository.
    
    Samples key files, searches for patterns (TODOs, secrets, error handling),
    then sends to Gemini Pro for deep analysis.
    """
    logger.info(f"💻 Code Quality Agent analyzing: {local_path}")

    # Gather data
    all_files = list_files(local_path)
    ext_summary = get_file_extensions_summary(local_path)
    key_files = _select_key_files(local_path, all_files)

    # Read sampled files
    file_contents = {}
    for f in key_files:
        content = git_show(local_path, f, max_bytes=15000)
        if content:
            file_contents[f] = content

    # Search for patterns
    todos = git_search_code(local_path, "TODO\\|FIXME\\|HACK\\|XXX")
    secrets_patterns = git_search_code(
        local_path,
        "api_key\\|API_KEY\\|secret\\|password\\|token\\|sk-\\|AIza",
    )
    error_handling = git_search_code(local_path, "try\\|catch\\|except\\|rescue")

    user_content = f"""Analyze the code quality and logic of this repository:

PROJECT TYPE: {project_type}

FILE EXTENSION BREAKDOWN:
{json.dumps(ext_summary, indent=2)}

TOTAL FILES: {len(all_files)}

SAMPLED FILES ({len(file_contents)} files):
"""
    
    for filepath, content in file_contents.items():
        user_content += f"\n{'='*60}\nFILE: {filepath}\n{'='*60}\n{content}\n"

    user_content += f"""

TODO/FIXME OCCURRENCES ({len(todos)} found):
{json.dumps(todos[:20], indent=2)}

POTENTIAL SECRETS/API KEYS ({len(secrets_patterns)} found):
{json.dumps(secrets_patterns[:20], indent=2)}

ERROR HANDLING PATTERNS ({len(error_handling)} found):
{json.dumps(error_handling[:20], indent=2)}

Provide your detailed code quality and logic assessment."""

    result = await run_agent(
        agent_name="Code Quality & Logic",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=CodeQualityOutput,
        model=MODEL_PRO,
    )

    if result:
        logger.info(f"✅ Code Quality complete. Score: {result.overall_code_score}/10")
    return result
