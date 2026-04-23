"""
RecruitSight — LinkedIn Orchestrator
Sequential coordinator for the 5 LinkedIn analysis agents.
All agents run SEQUENTIALLY (never parallel) to respect data dependencies
and the original spec's rate-limit constraints.

Execution Flow:
  Phase 1:  Scrape LinkedIn profile data
  Phase 2:  Profile Intelligence Agent (foundation — all others depend on this)
  Phase 3:  Content & Thought Leadership Agent (depends on Phase 2)
  Phase 4:  Interaction & Engagement Agent (depends on Phase 2 + 3)
  Phase 5:  Achievement & Credibility Agent (depends on Phase 2)
  Phase 6:  Report Compiler Agent (depends on all above)
"""

import asyncio
import logging
import time

from models.linkedin_schemas import (
    LinkedInPipelineResult,
    LinkedInAgentResult,
)
from agents.linkedin_profile import linkedin_profile_agent
from agents.linkedin_content import linkedin_content_agent
from agents.linkedin_interaction import linkedin_interaction_agent
from agents.linkedin_credibility import linkedin_credibility_agent
from agents.linkedin_report_compiler import linkedin_report_compiler_agent
from tools.linkedin_tools import fetch_linkedin_context

logger = logging.getLogger("recruitsight.linkedin_orchestrator")

# Delay between agents to respect rate limits
INTER_AGENT_DELAY = 3


def _make_result(agent_name: str, output) -> LinkedInAgentResult:
    """Wrap an agent output into a LinkedInAgentResult for status tracking."""
    if output is None:
        return LinkedInAgentResult(
            agent_name=agent_name,
            status="failed",
            error="Agent returned no output after all retries",
            output=None,
        )
    return LinkedInAgentResult(
        agent_name=agent_name,
        status="success",
        output=output.model_dump() if hasattr(output, "model_dump") else None,
    )


async def run_linkedin_pipeline(linkedin_url: str) -> LinkedInPipelineResult:
    """
    Execute the full LinkedIn analysis pipeline.

    Coordinates all 5 agents SEQUENTIALLY, passing outputs between
    agents as each completes.

    Args:
        linkedin_url: Public LinkedIn profile URL

    Returns:
        LinkedInPipelineResult with all agent outputs and final report path
    """
    start_time = time.time()
    pipeline = LinkedInPipelineResult(linkedin_url=linkedin_url)

    logger.info("=" * 70)
    logger.info("🔗 RecruitSight LinkedIn Analysis Pipeline Starting")
    logger.info(f"   Profile: {linkedin_url}")
    logger.info("=" * 70)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Scrape LinkedIn Profile Data
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🌐 PHASE 1: Scraping LinkedIn Profile Data")
    logger.info("-" * 40)

    scraped_context = fetch_linkedin_context(linkedin_url)
    logger.info("✅ LinkedIn data fetched (scraping complete)")

    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: Profile Intelligence Agent (Foundation)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🧠 PHASE 2: Profile Intelligence Agent")
    logger.info("-" * 40)

    try:
        profile_data = await linkedin_profile_agent(
            linkedin_url, scraped_context=scraped_context
        )
    except Exception as e:
        logger.error(f"❌ [linkedin_profile] Exception: {e}")
        profile_data = None

    pipeline.agent_results["linkedin_profile"] = _make_result(
        "linkedin_profile", profile_data
    )

    if profile_data:
        pipeline.candidate_name = profile_data.full_name
        logger.info(f"✅ Profile: {profile_data.full_name} — {profile_data.current_role}")
    else:
        logger.warning("⚠️ Profile Intelligence Agent failed — continuing with limited data")

    await asyncio.sleep(INTER_AGENT_DELAY)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: Content & Thought Leadership Agent
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n✍️ PHASE 3: Content & Thought Leadership Agent")
    logger.info("-" * 40)

    try:
        content_data = await linkedin_content_agent(
            linkedin_url,
            profile_data=profile_data,
            scraped_context=scraped_context,
        )
    except Exception as e:
        logger.error(f"❌ [linkedin_content] Exception: {e}")
        content_data = None

    pipeline.agent_results["linkedin_content"] = _make_result(
        "linkedin_content", content_data
    )
    await asyncio.sleep(INTER_AGENT_DELAY)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: Interaction & Engagement Agent
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🤝 PHASE 4: Interaction & Engagement Agent")
    logger.info("-" * 40)

    try:
        interaction_data = await linkedin_interaction_agent(
            linkedin_url,
            profile_data=profile_data,
            content_data=content_data,
            scraped_context=scraped_context,
        )
    except Exception as e:
        logger.error(f"❌ [linkedin_interaction] Exception: {e}")
        interaction_data = None

    pipeline.agent_results["linkedin_interaction"] = _make_result(
        "linkedin_interaction", interaction_data
    )
    await asyncio.sleep(INTER_AGENT_DELAY)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 5: Achievement & Credibility Agent
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n🏆 PHASE 5: Achievement & Credibility Agent")
    logger.info("-" * 40)

    try:
        credibility_data = await linkedin_credibility_agent(
            linkedin_url,
            profile_data=profile_data,
            scraped_context=scraped_context,
        )
    except Exception as e:
        logger.error(f"❌ [linkedin_credibility] Exception: {e}")
        credibility_data = None

    pipeline.agent_results["linkedin_credibility"] = _make_result(
        "linkedin_credibility", credibility_data
    )
    await asyncio.sleep(INTER_AGENT_DELAY)

    # ═══════════════════════════════════════════════════════════════
    # PHASE 6: Report Compiler Agent (Final)
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n📄 PHASE 6: LinkedIn Report Compiler")
    logger.info("-" * 40)

    try:
        report = await linkedin_report_compiler_agent(
            linkedin_url=linkedin_url,
            profile_data=profile_data,
            content_data=content_data,
            interaction_data=interaction_data,
            credibility_data=credibility_data,
        )
    except Exception as e:
        logger.error(f"❌ [linkedin_report_compiler] Exception: {e}")
        report = None

    pipeline.agent_results["linkedin_report_compiler"] = _make_result(
        "linkedin_report_compiler", report
    )

    if report:
        pipeline.report_path = report.report_path
        pipeline.composite_score = report.composite_score
        pipeline.grade = report.grade.value
        pipeline.verdict = report.verdict.value

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════
    elapsed = time.time() - start_time
    successful = sum(
        1 for r in pipeline.agent_results.values() if r.status == "success"
    )
    total = len(pipeline.agent_results)

    logger.info("\n" + "=" * 70)
    logger.info("🏁 RecruitSight LinkedIn Pipeline Complete")
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
