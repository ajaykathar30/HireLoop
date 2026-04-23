"""
RecruitSight — Unified Candidate Resume Analyzer
Entry point that processes a resume PDF, extracts links, and runs multi-agent pipelines.

Usage:
    python main.py <resume_pdf_url>

Example:
    python main.py https://res.cloudinary.com/demo/image/upload/sample_resume.pdf
"""

import asyncio
import logging
import sys
import os
import re

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.pdf_tools import download_pdf, extract_links_from_pdf
from orchestrator import run_pipeline as run_github_pipeline
from linkedin_orchestrator import run_linkedin_pipeline

def setup_logging():
    """Configure structured logging for the pipeline."""
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-7s │ %(name)-30s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def validate_github_url(url: str) -> bool:
    """Basic validation that the URL looks like a GitHub repo URL."""
    pattern = r"https?://github\.com/[^/]+/[^/]+/?$"
    return bool(re.match(pattern, url.strip()))

def validate_linkedin_url(url: str) -> bool:
    """Basic validation that the URL looks like a LinkedIn profile URL."""
    pattern = r"https?://(www\.)?linkedin\.com/in/[^/]+/?$"
    return bool(re.match(pattern, url.strip()))

def print_banner():
    """Print the RecruitSight banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██╗████████╗         ║
║   ██╔══██╗██╔════╝██╔════╝██╔══██╗██║   ██║██║╚══██╔══╝         ║
║   ██████╔╝█████╗  ██║     ██████╔╝██║   ██║██║   ██║            ║
║   ██╔══██╗██╔══╝  ██║     ██╔══██╗██║   ██║██║   ██║            ║
║   ██║  ██║███████╗╚██████╗██║  ██║╚██████╔╝██║   ██║            ║
║   ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝   ╚═╝            ║
║                                                                  ║
║   ███████╗██╗ ██████╗ ██╗  ██╗████████╗                         ║
║   ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝                         ║
║   ███████╗██║██║  ███╗███████║   ██║                             ║
║   ╚════██║██║██║   ██║██╔══██║   ██║                             ║
║   ███████║██║╚██████╔╝██║  ██║   ██║                             ║
║   ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                             ║
║                                                                  ║
║   Unified Candidate Resume Analyzer                              ║
║   Multi-Agent System with Google Gemini                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def main():
    """Main entry point."""
    setup_logging()
    print_banner()

    logger = logging.getLogger("recruitsight.main")

    # Get PDF URL from command line or prompt
    if len(sys.argv) > 1:
        pdf_url = sys.argv[1].strip()
    else:
        pdf_url = input("\n📄 Enter Resume PDF URL (e.g., Cloudinary): ").strip()

    if not pdf_url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

    print(f"\n📥 Downloading and parsing Resume: {pdf_url}")
    print("   This may take a few moments...\n")

    try:
        temp_pdf_path = download_pdf(pdf_url)
        extracted_links = extract_links_from_pdf(temp_pdf_path)
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        sys.exit(1)
    finally:
        # Cleanup temp file
        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except:
                pass

    github_urls = extracted_links.get("github", [])
    linkedin_urls = extracted_links.get("linkedin", [])

    # Filter for valid URLs
    valid_github = [url for url in github_urls if validate_github_url(url)]
    if not valid_github and github_urls:
        logger.warning(f"Found GitHub links but none matched the strict repo format: {github_urls}")
        valid_github = [github_urls[0]]
        
    valid_linkedin = [url for url in linkedin_urls if validate_linkedin_url(url)]
    if not valid_linkedin and linkedin_urls:
        logger.warning(f"Found LinkedIn links but none matched the strict profile format: {linkedin_urls}")
        valid_linkedin = [linkedin_urls[0]]

    selected_github = valid_github[0] if valid_github else None
    selected_linkedin = valid_linkedin[0] if valid_linkedin else None

    print("\n" + "=" * 70)
    print("🔍 EXTRACTION RESULTS")
    print("=" * 70)
    
    if selected_github:
        print(f"   🐙 GitHub URL:   {selected_github}")
    else:
        print("   🐙 GitHub URL:   ❌ None found in resume")
        
    if selected_linkedin:
        print(f"   💼 LinkedIn URL: {selected_linkedin}")
    else:
        print("   💼 LinkedIn URL: ❌ None found in resume")
        
    print("=" * 70 + "\n")

    github_result = None
    linkedin_result = None

    # Run GitHub Pipeline
    if selected_github:
        print(f"\n🚀 STARTING GITHUB PIPELINE: {selected_github}\n")
        try:
            github_result = await run_github_pipeline(selected_github)
        except Exception as e:
            logger.error(f"GitHub pipeline failed: {e}", exc_info=True)
    else:
        print("\n⚠️ Skipping GitHub Pipeline: No valid project link found.\n")

    # Run LinkedIn Pipeline
    if selected_linkedin:
        print(f"\n🚀 STARTING LINKEDIN PIPELINE: {selected_linkedin}\n")
        try:
            linkedin_result = await run_linkedin_pipeline(selected_linkedin)
        except Exception as e:
            logger.error(f"LinkedIn pipeline failed: {e}", exc_info=True)
    else:
        print("\n⚠️ Skipping LinkedIn Pipeline: No valid profile link found.\n")

    # Print Combined Summary
    print("\n" + "═" * 70)
    print("🏆 FINAL UNIFIED ANALYSIS COMPLETE")
    print("═" * 70)

    # GitHub Summary
    print("\n[ GitHub Analysis ]")
    if github_result:
        successful = sum(1 for r in github_result.agent_results.values() if r.status == "success")
        total = len(github_result.agent_results)
        print(f"   Agents: {successful}/{total} succeeded")
        if github_result.report_path:
            print(f"   📋 Grade:   {github_result.grade}")
            print(f"   📈 Score:   {github_result.composite_score}/10")
            print(f"   👔 Verdict: {github_result.verdict}")
            print(f"   📄 Report:  {github_result.report_path}")
        else:
            print("   ❌ Report generation failed.")
    else:
        print("   ⚠️ No GitHub project analyzed. (Note: Project section empty in report)")

    # LinkedIn Summary
    print("\n[ LinkedIn Analysis ]")
    if linkedin_result:
        successful = sum(1 for r in linkedin_result.agent_results.values() if r.status == "success")
        total = len(linkedin_result.agent_results)
        print(f"   Agents: {successful}/{total} succeeded")
        if linkedin_result.report_path:
            print(f"   📋 Grade:   {linkedin_result.grade}")
            print(f"   📈 Score:   {linkedin_result.composite_score}/10")
            print(f"   👔 Verdict: {linkedin_result.verdict}")
            print(f"   📄 Report:  {linkedin_result.report_path}")
        else:
            print("   ❌ Report generation failed.")
    else:
        print("   ⚠️ No LinkedIn profile analyzed. (Note: LinkedIn section empty in report)")
        
    print("\n" + "═" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user.")
        sys.exit(130)
