import os
import sys
import asyncio
import logging
from typing import Dict, Optional

# Add MCP_AGENTS to path
MCP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "MCP_AGENTS"))
if MCP_PATH not in sys.path:
    sys.path.insert(0, MCP_PATH)

# Now we can import MCP modules
try:
    from tools.pdf_tools import download_pdf, extract_links_from_pdf
    from orchestrator import run_pipeline as run_github_pipeline
except ImportError as e:
    print(f"Error importing MCP modules: {e}")
    raise

# Configure RecruitSight logging for terminal visibility
def setup_mcp_logging():
    rs_logger = logging.getLogger("recruitsight")
    if not rs_logger.handlers:
        rs_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '\033[94m%(asctime)s │ %(levelname)-7s │ %(name)-25s │ %(message)s\033[0m',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        rs_logger.addHandler(handler)
        rs_logger.propagate = False # Prevent double logging if root also has a handler

setup_mcp_logging()
logger = logging.getLogger("hireloop.mcp_bridge")


async def get_mcp_scores(resume_url: str) -> Dict[str, float]:
    """
    Downloads the resume, extracts links, and runs the GitHub pipeline.
    Returns a dictionary with 'github_score' (0-10).
    """
    results = {
        "github_score": 0.0
    }

    if not resume_url:
        return results

    temp_pdf_path = None
    try:
        # 1. Download and Parse
        logger.info(f"🚀 MCP Bridge: Processing candidate resume {resume_url}")
        temp_pdf_path = download_pdf(resume_url)
        links = extract_links_from_pdf(temp_pdf_path)
        
        github_urls = links.get("github", [])
        
        # 2. Prepare task
        github_task = None
        
        if github_urls:
            logger.info(f"🐙 MCP Bridge: Found GitHub Repository: {github_urls[0]}")
            logger.info("   Starting multi-agent analysis. This may take 2-3 minutes...")
            github_task = asyncio.create_task(run_github_pipeline(github_urls[0]))
        else:
            logger.warning("❌ MCP Bridge: No GitHub repository found in candidate's resume.")
            return results
            
        # 3. Run
        await github_task
        
        # 4. Collect scores
        if github_task and not isinstance(github_task.result(), Exception):
            github_res = github_task.result()
            if github_res and getattr(github_res, "composite_score", None) is not None:
                score = float(github_res.composite_score)
                results["github_score"] = score
                logger.info(f"✅ MCP Bridge: GitHub Analysis Complete. Score: {score}/10")
            else:
                logger.error("❌ MCP Bridge: Pipeline completed but returned no valid score.")
                
    except Exception as e:
        logger.error(f"❌ MCP Bridge Error during pipeline execution: {e}", exc_info=True)

    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp PDF {temp_pdf_path}: {e}")
                
    return results

