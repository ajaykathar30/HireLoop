"""
RecruitSight — LinkedIn Profile Analyzer
Entry point for the LinkedIn multi-agent analysis system.

Usage:
    python linkedin_main.py <linkedin_profile_url>

Example:
    python linkedin_main.py https://www.linkedin.com/in/john-doe
"""

import asyncio
import logging
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging():
    """Configure structured logging for the LinkedIn pipeline."""
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


def print_banner():
    """Print the RecruitSight LinkedIn banner."""
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
║   🔗 LinkedIn Profile Analyzer                                   ║
║   Multi-Agent System with Google Gemini                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def validate_url(url: str) -> bool:
    """Basic validation that the URL looks like a LinkedIn profile URL."""
    import re
    pattern = r"https?://(www\.)?linkedin\.com/in/[^/]+/?$"
    return bool(re.match(pattern, url.strip()))


async def main():
    """Main entry point."""
    setup_logging()
    print_banner()

    logger = logging.getLogger("recruitsight.linkedin_main")

    # Get LinkedIn URL from command line or prompt
    if len(sys.argv) > 1:
        linkedin_url = sys.argv[1].strip()
    else:
        linkedin_url = input("\n🔗 Enter LinkedIn Profile URL: ").strip()

    if not linkedin_url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

    if not validate_url(linkedin_url):
        print(f"❌ Invalid LinkedIn URL: {linkedin_url}")
        print("   Expected format: https://www.linkedin.com/in/username")
        sys.exit(1)

    print(f"\n🔍 Analyzing LinkedIn Profile: {linkedin_url}")
    print("   This may take a few minutes...\n")

    # Run the LinkedIn pipeline
    from linkedin_orchestrator import run_linkedin_pipeline

    try:
        result = await run_linkedin_pipeline(linkedin_url)
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"LinkedIn pipeline failed: {e}", exc_info=True)
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 70)
    print("📊 LINKEDIN ANALYSIS COMPLETE")
    print("=" * 70)

    successful = sum(
        1 for r in result.agent_results.values() if r.status == "success"
    )
    total = len(result.agent_results)
    print(f"   Agents: {successful}/{total} succeeded")

    if result.report_path:
        print(f"\n   📋 Grade:   {result.grade}")
        print(f"   📈 Score:   {result.composite_score}/10")
        print(f"   👔 Verdict: {result.verdict}")
        print(f"\n   📄 Report saved to: {result.report_path}")
    else:
        print("\n   ❌ Report generation failed.")
        print("   Check the logs above for details.")

    # Print failed agents
    failed = [
        name for name, r in result.agent_results.items() if r.status == "failed"
    ]
    if failed:
        print(f"\n   ⚠️ Failed agents: {', '.join(failed)}")

    print()


if __name__ == "__main__":
    asyncio.run(main())
