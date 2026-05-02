"""
RecruitSight - Report Compiler Agent
Aggregates all agent outputs into a clean, structured, recruiter-friendly
markdown report file. This is the final output of the entire system.
Uses gemini-2.5-pro for synthesis and report writing.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from agents.base import run_agent
from config import MODEL_GEMINI_FALLBACK, REPORTS_DIR
from mcp_models.schemas import (
    ReportCompilerOutput,
    RepoIngestionOutput,
    FileStructureOutput,
    CommitForensicsOutput,
    CodeQualityOutput,
    DependencyAuditOutput,
    ReadmeRealityOutput,
    SimilarRepoOutput,
    PlagiarismOutput,
    UniquenessOutput,
)

logger = logging.getLogger("recruitsight.report_compiler")

SYSTEM_PROMPT = """You are the Report Compiler Agent for RecruitSight.

Your responsibilities:
1. Compile agent findings into a CONCISE markdown report.
2. Calculate a COMPOSITE SCORE (weighted average):
   - Structure Score: 10%
   - Commit Authenticity Score: 20%
   - Code Quality Score: 25%
   - Dependency Score: 10%
   - README Honesty Score: 10%
   - Originality Score: 15%
   - Real-World Value Score: 10%
3. Assign an overall PROJECT GRADE: A / B / C / D / F
4. Provide exactly 5-10 key bullet points summarizing the project's quality, authenticity, and risks.
5. The report_markdown field must contain ONLY this structure:

---
# RecruitSight Summary Report
**Repository:** <URL> | **Grade:** <A/B/C/D/F> (<composite score>/10)

## 📊 Score Breakdown
| Dimension | Score | Weight |
|-----------|-------|--------|
| File Structure | X/10 | 10% |
| Commit History | X/10 | 20% |
| Code Quality | X/10 | 25% |
| Dependencies | X/10 | 10% |
| README Honesty | X/10 | 10% |
| Originality | X/10 | 15% |
| Real-World Value | X/10 | 10% |
| **FINAL SCORE** | **X.X/10** | |

## 📝 Key Analysis Points
- <Point 1: Authenticity/Commits>
- <Point 2: Code Architecture/Structure>
- <Point 3: Logic & Code Quality>
- <Point 4: Dependency Usage>
- <Point 5: README Accuracy>
- <Optional Points 6-10: Red Flags or Strengths>

## 👔 Verdict: <STRONG | MODERATE | WEAK | DISQUALIFY>
---
"""


async def report_compiler_agent(
    repo_url: str,
    owner: str,
    repo_name: str,
    ingestion: RepoIngestionOutput | None,
    file_structure: FileStructureOutput | None,
    commit_forensics: CommitForensicsOutput | None,
    code_quality: CodeQualityOutput | None,
    dependency_audit: DependencyAuditOutput | None,
    readme_reality: ReadmeRealityOutput | None,
    similar_repos: SimilarRepoOutput | None,
    plagiarism: PlagiarismOutput | None,
    uniqueness: UniquenessOutput | None,
) -> ReportCompilerOutput | None:
    """
    Compile all agent outputs into a final markdown report.
    
    Aggregates all agent data, sends to Gemini Pro for report synthesis,
    then writes the markdown file to disk.
    """
    logger.info(f"📄 Report Compiler Agent starting for: {owner}/{repo_name}")

    # Build comprehensive input for the compiler
    agent_outputs = {}
    agent_status = {}

    def _add_output(name: str, output):
        if output is not None:
            agent_outputs[name] = output.model_dump()
            agent_status[name] = "SUCCESS"
        else:
            agent_outputs[name] = None
            agent_status[name] = "FAILED"

    _add_output("repo_ingestion", ingestion)
    _add_output("file_structure", file_structure)
    _add_output("commit_forensics", commit_forensics)
    _add_output("code_quality", code_quality)
    _add_output("dependency_audit", dependency_audit)
    _add_output("readme_reality", readme_reality)
    _add_output("similar_repos", similar_repos)
    _add_output("plagiarism", plagiarism)
    _add_output("uniqueness", uniqueness)

    analysis_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    user_content = f"""Compile the final analysis report for this repository:

REPOSITORY URL: {repo_url}
CANDIDATE GITHUB: {owner}
ANALYSIS DATE: {analysis_date}

AGENT STATUS:
{json.dumps(agent_status, indent=2)}

ALL AGENT OUTPUTS:
{json.dumps(agent_outputs, indent=2)}

Generate the complete markdown report following the exact template structure.
Calculate the composite score using the weighted formula.
Write a detailed recruiter recommendation.
Set report_path to: reports/{owner}_{repo_name}_report.md"""

    result = await run_agent(
        agent_name="Report Compiler",
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        response_schema=ReportCompilerOutput,
        model=MODEL_GEMINI_FALLBACK,
    )

    if result:
        # Write the report to disk
        report_path = REPORTS_DIR / f"{owner}_{repo_name}_report.md"
        try:
            report_path.write_text(result.report_markdown, encoding="utf-8")
            result.report_path = str(report_path)
            logger.info(f"✅ Report written to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
            result.report_path = f"ERROR: {e}"

        logger.info(
            f"✅ Report Compiler complete. "
            f"Grade: {result.grade}, Score: {result.composite_score}/10, "
            f"Verdict: {result.verdict}"
        )

    return result
