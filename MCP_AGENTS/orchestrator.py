"""
RecruitSight — Orchestrator
Master coordinator that receives a GitHub URL, launches all agents in the
correct DAG order, passes outputs between agents, and triggers the Report Compiler.

Execution Flow:
  Phase 1:  Repo Ingestion (sequential — must complete first)
  Phase 2:  5 parallel agents: File Structure, Commit Forensics, Code Quality,
            Dependency Auditor, README vs Reality
  Phase 2B: Similar Repo Discovery (uses Phase 2 outputs as context)
  Phase 3:  2 parallel agents: Plagiarism & Originality, Uniqueness & Value
            (both depend on Phase 2 + 2B results)
  Phase 4:  Report Compiler (final synthesis — depends on everything)
"""

import asyncio
import logging
import time

from models.schemas import (
    PipelineResult,
    AgentResult,
    IngestionStatus,
)
from agents.repo_ingestion import repo_ingestion_agent
from agents.file_structure import file_structure_agent
from agents.commit_forensics import commit_forensics_agent
from agents.code_quality import code_quality_agent
from agents.dependency_auditor import dependency_auditor_agent
from agents.readme_reality import readme_reality_agent
from agents.similar_repo_discovery import similar_repo_discovery_agent
from agents.plagiarism_originality import plagiarism_originality_agent
from agents.uniqueness_value import uniqueness_value_agent
from agents.report_compiler import report_compiler_agent

logger = logging.getLogger("recruitsight.orchestrator")


def _make_result(agent_name: str, output) -> AgentResult:
    """Wrap an agent output into an AgentResult for status tracking."""
    if output is None:
        return AgentResult(
            agent_name=agent_name,
            status="failed",
            error="Agent returned no output after all retries",
            output=None,
        )
    return AgentResult(
        agent_name=agent_name,
        status="success",
        output=output.model_dump() if hasattr(output, "model_dump") else None,
    )


def _unpack(results: list, names: list[str], pipeline: PipelineResult) -> list:
    """Unpack asyncio.gather results, log status, store in pipeline."""
    unpacked = []
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            logger.error(f"❌ [{name}] Exception: {result}")
            pipeline.agent_results[name] = AgentResult(
                agent_name=name,
                status="failed",
                error=str(result),
            )
            unpacked.append(None)
        else:
            pipeline.agent_results[name] = _make_result(name, result)
            if result:
                logger.info(f"✅ [{name}] Completed")
            else:
                logger.warning(f"⚠️  [{name}] Returned None (agent failed internally)")
            unpacked.append(result)
    return unpacked


async def run_pipeline(repo_url: str) -> PipelineResult:
    """
    Execute the full RecruitSight analysis pipeline.

    Coordinates all 10 agents across 4 phases using asyncio for
    maximum parallelism while respecting data dependencies.

    Args:
        repo_url: Public GitHub repository URL

    Returns:
        PipelineResult with all agent outputs and final report path
    """
    start_time = time.time()
    pipeline = PipelineResult(repo_url=repo_url, owner="", repo_name="")

    logger.info("=" * 70)
    logger.info("🎯 RecruitSight Analysis Pipeline Starting")
    logger.info(f"   Repository: {repo_url}")
    logger.info("=" * 70)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Repo Ingestion (Sequential — gate for all other agents)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n📥 PHASE 1: Repo Ingestion")
    logger.info("-" * 40)

    ingestion = await repo_ingestion_agent(repo_url)
    pipeline.agent_results["repo_ingestion"] = _make_result("repo_ingestion", ingestion)

    if ingestion is None or ingestion.status == IngestionStatus.FAILED:
        error_msg = ingestion.error if ingestion else "Unknown ingestion error"
        logger.error(f"❌ Repo Ingestion FAILED: {error_msg}")
        logger.error("   Cannot proceed — aborting pipeline.")
        pipeline.owner = ingestion.owner if ingestion else ""
        pipeline.repo_name = ingestion.repo_name if ingestion else ""
        return pipeline

    pipeline.owner = ingestion.owner
    pipeline.repo_name = ingestion.repo_name
    local_path = ingestion.local_path

    logger.info(
        f"✅ Repo cloned → {ingestion.owner}/{ingestion.repo_name} "
        f"({ingestion.total_commits} commits, branch: {ingestion.default_branch})"
    )

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: Parallel — 5 Independent Analysis Agents
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n⚡ PHASE 2: Parallel Analysis (5 agents)")
    logger.info("-" * 40)

    phase2_raw = await asyncio.gather(
        file_structure_agent(local_path, ingestion.repo_name),
        commit_forensics_agent(local_path),
        code_quality_agent(local_path),
        dependency_auditor_agent(local_path),
        readme_reality_agent(local_path),
        return_exceptions=True,
    )

    phase2_names = [
        "file_structure", "commit_forensics", "code_quality",
        "dependency_audit", "readme_reality",
    ]
    (
        file_structure,
        commit_forensics,
        code_quality,
        dependency_audit,
        readme_reality,
    ) = _unpack(phase2_raw, phase2_names, pipeline)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2B: Similar Repo Discovery (uses Phase 2 context)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🔍 PHASE 2B: Similar Repo Discovery")
    logger.info("-" * 40)

    # Extract context from Phase 2 outputs for better search queries
    project_type = file_structure.project_type if file_structure else "unknown"
    primary_language = code_quality.primary_language if code_quality else "unknown"
    key_libs = dependency_audit.key_libraries if dependency_audit else []
    readme_summary = readme_reality.summary if readme_reality else ""

    try:
        similar_repos = await similar_repo_discovery_agent(
            repo_name=ingestion.repo_name,
            project_type=project_type,
            primary_language=primary_language,
            key_libraries=key_libs,
            readme_summary=readme_summary,
        )
    except Exception as e:
        logger.error(f"❌ [similar_repos] Exception: {e}")
        similar_repos = None

    pipeline.agent_results["similar_repos"] = _make_result("similar_repos", similar_repos)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: Parallel — Plagiarism + Uniqueness (needs 2 + 2B)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🔗 PHASE 3: Deep Forensics (2 parallel agents)")
    logger.info("-" * 40)

    is_tutorial = similar_repos.is_common_tutorial_project if similar_repos else False
    completion = code_quality.completion_level.value if code_quality else "unknown"

    phase3_raw = await asyncio.gather(
        plagiarism_originality_agent(
            local_path=local_path,
            similar_repos=similar_repos,
            file_structure=file_structure,
            is_common_tutorial=is_tutorial,
        ),
        uniqueness_value_agent(
            repo_name=ingestion.repo_name,
            project_type=project_type,
            similar_repos=similar_repos,
            readme_output=readme_reality,
            code_quality=code_quality,
            is_common_tutorial=is_tutorial,
            completion_level=completion,
        ),
        return_exceptions=True,
    )

    plagiarism, uniqueness = _unpack(phase3_raw, ["plagiarism", "uniqueness"], pipeline)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: Report Compilation (needs everything)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n📄 PHASE 4: Report Compilation")
    logger.info("-" * 40)

    try:
        report = await report_compiler_agent(
            repo_url=repo_url,
            owner=ingestion.owner,
            repo_name=ingestion.repo_name,
            ingestion=ingestion,
            file_structure=file_structure,
            commit_forensics=commit_forensics,
            code_quality=code_quality,
            dependency_audit=dependency_audit,
            readme_reality=readme_reality,
            similar_repos=similar_repos,
            plagiarism=plagiarism,
            uniqueness=uniqueness,
        )
    except Exception as e:
        logger.error(f"❌ [report_compiler] Exception: {e}")
        report = None

    pipeline.agent_results["report_compiler"] = _make_result("report_compiler", report)

    if report:
        pipeline.report_path = report.report_path
        pipeline.composite_score = report.composite_score
        pipeline.grade = report.grade.value
        pipeline.verdict = report.verdict.value

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════
    elapsed = time.time() - start_time
    successful = sum(1 for r in pipeline.agent_results.values() if r.status == "success")
    total = len(pipeline.agent_results)

    logger.info("\n" + "=" * 70)
    logger.info("🏁 RecruitSight Pipeline Complete")
    logger.info(f"   Time:    {elapsed:.1f}s")
    logger.info(f"   Agents:  {successful}/{total} succeeded")
    if report:
        logger.info(f"   Grade:   {report.grade.value}  ({report.composite_score}/10)")
        logger.info(f"   Verdict: {report.verdict.value}")
        logger.info(f"   Report:  {report.report_path}")
    else:
        logger.error("   ❌ Report compilation FAILED — check agent logs above")
    logger.info("=" * 70)

    return pipeline
