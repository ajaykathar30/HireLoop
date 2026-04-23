"""
RecruitSight — Configuration & Client Initialization
Loads environment variables, initializes the Google GenAI client,
and defines model routing constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ─── Load Environment ──────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Add it to .env")

# ─── GenAI Client ──────────────────────────────────────────────────
client = genai.Client(api_key=GEMINI_API_KEY)

# ─── Model Routing ─────────────────────────────────────────────────
# Deep reasoning: complex analysis, cross-referencing, report synthesis
MODEL_PRO = "gemini-2.5-pro"

# Fast & capable: parsing, structured extraction, pattern matching
MODEL_FLASH = "gemini-2.5-flash"

# Ultra-fast: simple validation, URL parsing
MODEL_FLASH_LITE = "gemini-2.5-flash-lite"

# ─── Paths ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
CLONE_BASE_DIR = PROJECT_ROOT / "cloned_repos"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Ensure directories exist
CLONE_BASE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Agent Defaults ───────────────────────────────────────────────
MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2
DEFAULT_TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 65536
