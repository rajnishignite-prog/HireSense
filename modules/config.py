"""
modules/config.py
=================
Central configuration loader.

Reads API keys from the `.env` file (via python-dotenv) and exposes them
as simple constants used by the rest of the app.

Only ONE key is needed:
  GEMINI_API_KEY —  from https://aistudio.google.com (no credit card)

NOTHING in this file should ever be committed with real keys inside it.
Real keys live only in `.env`, which is listed in `.gitignore`.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

# Expose key as a module-level constant
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
"""Google API key — used by Gemini 2.5 Flash Lite ."""


def active_llm() -> str:
    """Return a human-readable label for the active LLM."""
    if GEMINI_API_KEY:
        return "Gemini 2.5 Flash Lite "
    return "Keyword Rules (no API key set)"