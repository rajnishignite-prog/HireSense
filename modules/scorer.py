"""
modules/scorer.py
=================
Handles all embedding and similarity scoring logic.

Responsibilities:
  - Load & cache the sentence-transformer model
  - Convert text → embedding vector
  - Compute cosine similarity between JD and resume
  - Normalise raw similarity to a 0–100 score
  - Assign a recommendation tier based on score
"""

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ── Model name — change here if you want to swap models ──────────────────────
MODEL_NAME = "all-MiniLM-L6-v2"

# ── Thresholds for recommendation tiers ──────────────────────────────────────
STRONG_FIT_THRESHOLD   = 70   # score >= 70  → Strong Fit
MODERATE_FIT_THRESHOLD = 50   # score >= 50  → Moderate Fit
                               # score <  50  → Not Fit


@st.cache_resource(show_spinner=False)
def load_model() -> SentenceTransformer:
    """
    Load the sentence-transformer model once and cache it for the
    lifetime of the Streamlit session (avoids reloading on every rerun).

    Returns:
        A loaded SentenceTransformer instance.
    """
    return SentenceTransformer(MODEL_NAME)


def embed_text(model: SentenceTransformer, text: str) -> np.ndarray:
    """
    Convert a plain-text string into a 2-D embedding array (shape: 1 × dim).

    Args:
        model: A loaded SentenceTransformer model.
        text:  The text to embed (JD or resume content).

    Returns:
        np.ndarray of shape (1, embedding_dim).
    """
    return model.encode([text], convert_to_numpy=True)


def compute_match_score(jd_embedding: np.ndarray,
                        resume_embedding: np.ndarray) -> float:
    """
    Compute a normalised match score between 0 and 100.

    Cosine similarity produces values in [-1, 1].
    We map that linearly to [0, 100] so scores are intuitive.

    Formula:  score = (cosine_similarity + 1) / 2 × 100

    Args:
        jd_embedding:     Embedding of the job description (shape 1 × dim).
        resume_embedding: Embedding of the resume text    (shape 1 × dim).

    Returns:
        Float rounded to one decimal place, in range [0.0, 100.0].
    """
    raw_similarity = cosine_similarity(jd_embedding, resume_embedding)[0][0]
    normalised     = (raw_similarity + 1) / 2 * 100
    return round(float(normalised), 1)


def get_recommendation(score: float) -> str:
    """
    Map a numeric match score to a human-readable recommendation tier.

    Tiers:
        Strong Fit   → score ≥ STRONG_FIT_THRESHOLD
        Moderate Fit → score ≥ MODERATE_FIT_THRESHOLD
        Not Fit      → score <  MODERATE_FIT_THRESHOLD

    Args:
        score: The normalised match score (0–100).

    Returns:
        One of: "Strong Fit", "Moderate Fit", "Not Fit".
    """
    if score >= STRONG_FIT_THRESHOLD:
        return "Strong Fit"
    elif score >= MODERATE_FIT_THRESHOLD:
        return "Moderate Fit"
    else:
        return "Not Fit"


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """
    Sort a list of candidate result dicts by score (highest first)
    and inject a 1-based rank field.

    Args:
        candidates: List of dicts, each with at least a "score" key.

    Returns:
        The same list sorted descending by score, with "rank" added.
    """
    sorted_candidates = sorted(candidates, key=lambda c: c["score"], reverse=True)
    for rank, candidate in enumerate(sorted_candidates, start=1):
        candidate["rank"] = rank
    return sorted_candidates