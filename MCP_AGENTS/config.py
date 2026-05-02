"""
RecruitSight - Configuration & Client Initialization
Loads environment variables, initializes the Google GenAI client,
and defines model routing constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import openai

# ─── Load Environment ──────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment. Add it to .env")

# ─── GenAI Client ──────────────────────────────────────────────────
client = openai.AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

import google.generativeai as genai
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found. Gemini fallback will fail.")

# ─── Model Routing ─────────────────────────────────────────────────
MODEL_GEMINI_FALLBACK = "gemini-2.5-flash"
# Deep reasoning: complex analysis, cross-referencing, report synthesis
MODEL_PRO = "minimax/minimax-m2.5:free"

# Fast & capable: parsing, structured extraction, pattern matching
MODEL_FLASH = "openai/gpt-oss-120b:free"

# Intermediate performance: dependency auditing, specific pipeline stages
MODEL_NEMOTRON = "nvidia/nemotron-3-nano-30b-a3b:free"

# Ultra-fast: simple validation, URL parsing
MODEL_FLASH_LITE = "openai/gpt-oss-20b:free"

# Specialized: code quality and logic
MODEL_MINIMAX = "minimax/minimax-m2.5:free"

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
