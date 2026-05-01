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
    from linkedin_orchestrator import run_linkedin_pipeline
except ImportError as e:
    print(f"Error importing MCP modules: {e}")
    raise

logger = logging.getLogger("hireloop.mcp_bridge")

async def get_mcp_scores(resume_url: str) -> Dict[str, float]:
    """
    Downloads the resume, extracts links, and runs the GitHub and LinkedIn pipelines.
    Returns a dictionary with 'github_score' and 'linkedin_score' (both 0-10).
    """
    results = {
        "github_score": 0.0,
        "linkedin_score": 0.0
    }

    if not resume_url:
        return results

    temp_pdf_path = None
    try:
        # 1. Download and Parse
        temp_pdf_path = download_pdf(resume_url)
        links = extract_links_from_pdf(temp_pdf_path)
        
        github_urls = links.get("github", [])
        linkedin_urls = links.get("linkedin", [])
        
        # 2. Prepare tasks
        tasks = []
        github_task = None
        linkedin_task = None
        
        if github_urls:
            logger.info(f"Triggering GitHub pipeline for {github_urls[0]}")
            github_task = asyncio.create_task(run_github_pipeline(github_urls[0]))
            tasks.append(github_task)
            
        if linkedin_urls:
            logger.info(f"Triggering LinkedIn pipeline for {linkedin_urls[0]}")
            linkedin_task = asyncio.create_task(run_linkedin_pipeline(linkedin_urls[0]))
            tasks.append(linkedin_task)
            
        if not tasks:
            logger.warning("No GitHub or LinkedIn links found in resume.")
            return results
            
        # 3. Run in parallel
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 4. Collect scores
        if github_task and not isinstance(github_task.result(), Exception):
            github_res = github_task.result()
            if github_res and getattr(github_res, "composite_score", None) is not None:
                results["github_score"] = float(github_res.composite_score)
                
        if linkedin_task and not isinstance(linkedin_task.result(), Exception):
            linkedin_res = linkedin_task.result()
            if linkedin_res and getattr(linkedin_res, "composite_score", None) is not None:
                results["linkedin_score"] = float(linkedin_res.composite_score)
                
    except Exception as e:
        logger.error(f"MCP Bridge Error: {e}")
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp PDF {temp_pdf_path}: {e}")
                
    return results
