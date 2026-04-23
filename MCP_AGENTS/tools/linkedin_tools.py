"""
RecruitSight — LinkedIn Tools (MCP-Powered)
Uses the official MCP Python SDK to fetch data via stdio.
"""

import re
import json
import logging
from urllib.parse import urlparse
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("recruitsight.linkedin_tools")


def validate_linkedin_url(url: str) -> bool:
    """Validate that a URL is a LinkedIn profile URL."""
    pattern = r"https?://(www\.)?linkedin\.com/in/[^/]+/?$"
    return bool(re.match(pattern, url.strip()))


def extract_username_from_url(url: str) -> str:
    """Extract the LinkedIn profile slug/username from a URL."""
    parsed = urlparse(url.strip().rstrip("/"))
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2 and path_parts[0] == "in":
        return path_parts[1]
    return parsed.path.strip("/").split("/")[-1]


async def get_linkedin_profile(linkedin_url: str) -> dict:
    """Fetch a LinkedIn person's full profile via the MCP server using stdio transport."""
    logger.info(f"🔗 Fetching LinkedIn profile via MCP (stdio): {linkedin_url}")
    
    server_params = StdioServerParameters(
        command="uvx",
        args=["linkedin-scraper-mcp@latest", "--transport", "stdio"],
        env={"UV_HTTP_TIMEOUT": "300"}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                logger.info("Initializing MCP session...")
                await session.initialize()
                
                logger.info(f"Calling tool: get_person_profile for {linkedin_url}")
                result = await session.call_tool("get_person_profile", arguments={"profile_url": linkedin_url})
                
                if not result or not hasattr(result, 'content'):
                    return {"error": "Empty response from tool"}
                    
                full_text = ""
                for block in result.content:
                    if block.type == "text":
                        full_text += block.text
                
                try:
                    profile_data = json.loads(full_text)
                    logger.info(f"✅ MCP profile fetched for: {profile_data.get('name', 'Unknown')}")
                    return profile_data
                except json.JSONDecodeError:
                    return {"raw_text": full_text}
                    
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return {"error": str(e)}


async def fetch_linkedin_context(linkedin_url: str) -> str:
    """
    High-level function: fetches real LinkedIn data via MCP server
    and returns a formatted context string for agent consumption.
    """
    profile_data = await get_linkedin_profile(linkedin_url)
    username = extract_username_from_url(linkedin_url)
    
    lines = [
        f"LINKEDIN PROFILE URL: {linkedin_url}",
        f"PROFILE USERNAME: {username}",
        "",
    ]

    if "error" in profile_data and not profile_data.get("name"):
        lines.append(f"⚠️ MCP DATA FETCH STATUS: FAILED — {profile_data.get('error')}")
        lines.append("NOTE: Perform analysis using URL/username + training knowledge only.")
        lines.append("Clearly mark all data as INFERRED.")
        return "\n".join(lines)

    lines.append("MCP DATA FETCH STATUS: SUCCESS — Real LinkedIn data below")
    lines.append("")

    if "raw_text" in profile_data:
        lines.append("RAW PROFILE DATA:")
        lines.append("-" * 60)
        lines.append(profile_data["raw_text"][:10000])
        lines.append("-" * 60)
        return "\n".join(lines)

    def _safe(key, default="Data unavailable"):
        return profile_data.get(key) or default

    lines.append(f"FULL NAME: {_safe('name')}")
    lines.append(f"HEADLINE: {_safe('headline')}")
    lines.append(f"LOCATION: {_safe('location')}")
    lines.append(f"ABOUT SECTION:\n{_safe('about', 'No About section')}")
    lines.append("")

    experience = profile_data.get("experience") or []
    if experience:
        lines.append(f"EXPERIENCE ({len(experience)} roles):")
        for i, exp in enumerate(experience, 1):
            if isinstance(exp, dict):
                title = exp.get("title") or exp.get("role") or "Unknown Role"
                company = exp.get("company") or exp.get("company_name") or "Unknown Company"
                start = exp.get("start_date") or exp.get("start") or "?"
                end = exp.get("end_date") or exp.get("end") or "Present"
                desc = exp.get("description") or exp.get("summary") or ""
                lines.append(f"  {i}. {title} @ {company} ({start} – {end})")
                if desc:
                    lines.append(f"     Description: {str(desc)[:200]}")
            else:
                lines.append(f"  {i}. {exp}")
    else:
        lines.append("EXPERIENCE: None listed")

    lines.append("")

    education = profile_data.get("education") or []
    if education:
        lines.append(f"EDUCATION ({len(education)} entries):")
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree") or edu.get("field_of_study") or ""
                school = edu.get("school") or edu.get("institution") or ""
                dates = edu.get("dates") or f"{edu.get('start_year', '')}–{edu.get('end_year', '')}"
                lines.append(f"  - {degree} @ {school} ({dates})")
            else:
                lines.append(f"  - {edu}")
    else:
        lines.append("EDUCATION: None listed")

    lines.append("")

    skills = profile_data.get("skills") or []
    if skills:
        lines.append(f"SKILLS ({len(skills)} listed):")
        for sk in skills[:20]:
            if isinstance(sk, dict):
                name = sk.get("name") or sk.get("skill") or str(sk)
                endorsements = sk.get("endorsements") or sk.get("endorsement_count") or ""
                lines.append(f"  - {name}" + (f" ({endorsements} endorsements)" if endorsements else ""))
            else:
                lines.append(f"  - {sk}")
    else:
        lines.append("SKILLS: None listed")

    lines.append("")

    certs = profile_data.get("certifications") or []
    if certs:
        lines.append(f"CERTIFICATIONS ({len(certs)}):")
        for c in certs:
            if isinstance(c, dict):
                name = c.get("name") or c.get("title") or ""
                issuer = c.get("issuing_organization") or c.get("issuer") or ""
                date = c.get("issue_date") or c.get("date") or ""
                lines.append(f"  - {name} | {issuer} | {date}")
            else:
                lines.append(f"  - {c}")
    else:
        lines.append("CERTIFICATIONS: None listed")

    lines.append("")

    honors = profile_data.get("honors") or profile_data.get("awards") or []
    if honors:
        lines.append(f"HONORS & AWARDS ({len(honors)}):")
        for h in honors:
            lines.append(f"  - {h}" if isinstance(h, str) else f"  - {json.dumps(h)}")
    else:
        lines.append("HONORS & AWARDS: None listed")

    lines.append("")

    projects = profile_data.get("projects") or []
    if projects:
        lines.append(f"PROJECTS ({len(projects)}):")
        for p in projects:
            if isinstance(p, dict):
                lines.append(f"  - {p.get('name', '')}: {p.get('description', '')[:150]}")
            else:
                lines.append(f"  - {p}")
    else:
        lines.append("LINKEDIN PROJECTS: None listed")

    lines.append("")

    recs = profile_data.get("recommendations") or []
    if recs:
        lines.append(f"RECOMMENDATIONS: {len(recs)} received")
    else:
        lines.append("RECOMMENDATIONS: None visible")

    connections = profile_data.get("connections") or profile_data.get("connection_count") or ""
    if connections:
        lines.append(f"CONNECTIONS: {connections}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF MCP PROFILE DATA")

    return "\n".join(lines)
