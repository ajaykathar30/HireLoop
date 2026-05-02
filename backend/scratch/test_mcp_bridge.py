import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root and backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline")))

load_dotenv()

from pipeline.agents.mcp_bridge import get_mcp_scores

async def test_bridge():
    # Example resume with links
    # You can replace this with a real Cloudinary URL from your DB
    test_url = "https://res.cloudinary.com/ddr4nbahy/image/upload/v1777079465/HireLoop/Resume/resume_e373f9f5-308e-4878-9f82-6e1464215402.pdf"
    
    print(f"Testing MCP Bridge with URL: {test_url}")
    scores = await get_mcp_scores(test_url)
    print("\nFINAL RESULTS:")
    print(f"GitHub Score:   {scores['github_score']}/10")

if __name__ == "__main__":

    asyncio.run(test_bridge())
