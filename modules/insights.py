"""
modules/insights.py
===================
Generates candidate strengths, gaps, and recommendation text.

LLM used: Google Gemini 2.5 Flash Lite (FREE via Google AI Studio)
  - Sign up at https://aistudio.google.com  →  free API key instantly
  - No credit card required
  - Falls back to keyword rules if GOOGLE_API_KEY is not set in .env

Key is loaded from .env via modules/config.py — never from user input.

Public API:
  get_insights(jd, resume_text, score) -> dict
"""

import json
import re

import google.generativeai as genai

from modules.config import GOOGLE_API_KEY
from modules.scorer import get_recommendation

# -- Model --------------------------------------------------------------------
GEMINI_MODEL = "gemini-2.5-flash-lite-preview-06-17"   # free tier

# -- Max chars sent to LLM per request ----------------------------------------
MAX_CHARS = 3000

# -- Keyword pool for rule-based fallback -------------------------------------
SKILL_POOL = [
    "python", "sql", "java", "javascript", "typescript", "react", "node",
    "machine learning", "deep learning", "data analysis", "excel", "tableau",
    "power bi", "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
    "agile", "scrum", "communication", "leadership", "management",
    "tensorflow", "pytorch", "nlp", "api", "rest", "git", "spark", "hadoop",
    "bash", "linux", "selenium", "flask", "django", "fastapi", "mongodb",
]

# -- Prompt template ----------------------------------------------------------
_PROMPT_TEMPLATE = """\
You are an expert technical recruiter conducting a resume screening.

Given the job description and candidate resume below, respond with ONLY a \
valid JSON object — no markdown fences, no extra text — containing exactly \
these three keys:

{{
  "strengths":      ["2-3 short phrases — candidate's strongest matches to the JD"],
  "gaps":           ["2-3 short phrases — candidate's notable gaps vs the JD"],
  "recommendation": "Strong Fit | Moderate Fit | Not Fit"
}}

The embedding-based similarity score is {score}/100 (for context only).

--- JOB DESCRIPTION ---
{jd}

--- CANDIDATE RESUME ---
{resume}
"""


# PUBLIC ENTRY POINT

def get_insights(jd: str, resume_text: str, score: float) -> dict:
    """
    Generate structured insights for one candidate.

    Uses Gemini 2.5 Flash Lite (free). Falls back to keyword rules
    if GOOGLE_API_KEY is missing or any error occurs.

    Args:
        jd:          Full job description text.
        resume_text: Extracted resume text.
        score:       Normalised match score (0-100).

    Returns:
        dict:
            "strengths"      -> list[str]  (2-3 items)
            "gaps"           -> list[str]  (2-3 items)
            "recommendation" -> str  ("Strong Fit" | "Moderate Fit" | "Not Fit")
            "source"         -> str  ("gemini" | "rules")
    """
    if GOOGLE_API_KEY:
        result = _gemini_insights(jd, resume_text, score)
        if result:
            result["source"] = "gemini"
            return result

    # Fallback — no key set or Gemini call failed
    result = _rule_based_insights(jd, resume_text, score)
    result["source"] = "rules"
    return result


# STRATEGY 1 — Gemini 2.5 Flash Lite (FREE)
def _gemini_insights(jd: str, resume_text: str, score: float):
    """
    Call Gemini 2.5 Flash Lite and parse structured JSON response.
    API key is read from GOOGLE_API_KEY in .env — never from user input.

    Returns:
        Parsed dict on success, None on any error (caller falls to rules).
    """
    prompt = _PROMPT_TEMPLATE.format(
        score  = score,
        jd     = jd[:MAX_CHARS],
        resume = resume_text[:MAX_CHARS],
    )

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model    = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        raw = response.text.strip()
        return _parse_and_validate(_strip_fences(raw), score)

    except Exception:
        return None


# STRATEGY 2 — Rule-based keyword matching (FALLBACK, no API needed)

def _rule_based_insights(jd: str, resume_text: str, score: float) -> dict:
    """
    Deterministic keyword comparison — no network calls, no API key needed.
    Compares skills from SKILL_POOL that appear in both JD and resume.
    """
    jd_lower     = jd.lower()
    resume_lower = resume_text.lower()

    jd_skills = [s for s in SKILL_POOL if s in jd_lower]
    matched   = [s for s in jd_skills  if s in resume_lower]
    missing   = [s for s in jd_skills  if s not in resume_lower]

    strengths = (
        [f"Proficient in {s.title()}" for s in matched[:3]]
        if matched else ["General background aligns with the role"]
    )
    gaps = (
        [f"No evidence of {s.title()} experience" for s in missing[:3]]
        if missing else ["No major skill gaps detected from keyword analysis"]
    )

    return {
        "strengths":      strengths,
        "gaps":           gaps,
        "recommendation": get_recommendation(score),
    }


# =============================================================================
# SHARED HELPERS
# =============================================================================

def _strip_fences(text: str) -> str:
    """Strip markdown code fences that some LLMs add despite being told not to."""
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$",       "", text)
    return text.strip()


def _parse_and_validate(raw_json: str, score: float):
    """Parse raw JSON and validate expected keys. Returns dict or None."""
    try:
        data           = json.loads(raw_json)
        strengths      = data.get("strengths",      [])
        gaps           = data.get("gaps",           [])
        recommendation = data.get("recommendation", get_recommendation(score))

        if not isinstance(strengths, list) or not isinstance(gaps, list):
            return None
        if recommendation not in ("Strong Fit", "Moderate Fit", "Not Fit"):
            recommendation = get_recommendation(score)

        return {
            "strengths":      strengths[:3],
            "gaps":           gaps[:3],
            "recommendation": recommendation,
        }

    except (json.JSONDecodeError, AttributeError):
        return None