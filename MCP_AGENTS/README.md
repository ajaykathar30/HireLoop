# RecruitSight — Unified Agentic Pipeline (`MCP_AGENTS`)

The `MCP_AGENTS` system is a dual-pipeline, multi-agent AI framework designed to automatically evaluate a candidate by analyzing their **GitHub** projects and **LinkedIn** profile simultaneously.

## Features
- 📄 **Unified Entry Point:** Provide a single PDF URL (e.g. Cloudinary). The system downloads the resume, parses it, and automatically discovers GitHub and LinkedIn links.
- 🐙 **GitHub Multi-Agent Analysis:** Deep code forensic analysis using `uv` to securely clone and scan repositories, analyzing architecture, code quality, testing rigor, and scalability.
- 💼 **LinkedIn MCP Integration:** Uses the official `mcp` SDK to spawn the `linkedin-scraper-mcp` server, completely bypassing LinkedIn scraping blocks (999 errors) by leveraging real browser contexts.
- 🤖 **Google Gemini Powered:** Employs `gemini-2.5-flash` for high-speed analysis and `gemini-2.5-pro` for deep reasoning, resulting in distinct, comprehensive markdown reports saved in the `reports/` folder.

---

## Prerequisites

Before running the agents, you must have the following installed on your system:

1. **Python 3.10+**
2. **`uv` Package Manager:** Used by the agents for ultra-fast, isolated execution.
   - Install via PowerShell (Windows): `irm https://astral.sh/uv/install.ps1 | iex`
   - Or macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **LinkedIn Session:** The LinkedIn agent uses your local LinkedIn session. You must log in via the MCP server **once** to save the session:
   - Run: `uvx linkedin-scraper-mcp@latest --login`
   - Follow the browser prompt to log into your LinkedIn account. After successful login, close the browser.

---

## Installation

1. Clone the repository and navigate to the `MCP_AGENTS` directory:
   ```bash
   cd HireLoop/MCP_AGENTS
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the `MCP_AGENTS` directory and add the following keys:
   ```ini
   GEMINI_API_KEY=your_google_api_key_here
   EXA_API_KEY=your_exa_search_api_key_here
   ```

---

## Usage

The system is designed to be fully automated. Use `main.py` as your entry point. 

### 1. Unified PDF Pipeline (Recommended)
Run the main script and pass the URL to a candidate's resume PDF. The system will automatically download it, extract links, and run both pipelines:

```bash
python main.py "https://res.cloudinary.com/demo/image/upload/sample_resume.pdf"
```
*If you run `python main.py` without arguments, it will prompt you for the URL.*

### 2. Standalone GitHub Pipeline
If you only want to analyze a GitHub repository:
```bash
# Edit the bottom of orchestrator.py to run directly, or import it in another script.
# Currently, orchestrator.py doesn't have a direct CLI wrapper, but it exports `run_pipeline(url)`
```

### 3. Standalone LinkedIn Pipeline
If you only want to analyze a LinkedIn profile:
```bash
python linkedin_main.py "https://www.linkedin.com/in/username"
```

---

## Outputs
All generated reports are written to the `MCP_AGENTS/reports/` folder as structured Markdown files. The unified pipeline will output two distinct reports if both links are found in the resume:
- `Candidate_Name_(Inferred)_github_report.md`
- `Candidate_Name_(Inferred)_linkedin_report.md`

## Architecture Note for Developers
- **Sync/Async Execution:** The entire orchestrator relies on Python `asyncio`. Agents are executed concurrently or sequentially depending on the module (`orchestrator.py` vs `linkedin_orchestrator.py`).
- **Tool Fallbacks:** If a tool fails (e.g., the LinkedIn profile is completely private), the agents gracefully degrade and use `EXA` search or their internal training knowledge to infer candidate skills based purely on the provided metadata.
