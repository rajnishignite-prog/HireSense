"""
modules/components.py
=====================
Reusable Streamlit UI components.

Each function renders one isolated piece of the UI:
  - render_hero()           → top title + subtitle
  - render_sidebar()        → config panel (Gemini toggle, how-it-works)
  - render_input_panel()    → JD textarea + PDF uploader
  - render_summary_metrics()→ 4-column metric strip
  - render_candidate_card() → individual result card (rich HTML)
"""

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────

def render_hero() -> None:
    """Render the branded page header."""
    st.markdown("""
    <div class="hero">
        <span class="hero-title">HireSense</span>
        <span class="hero-badge">AI · MVP</span>
    </div>
    <p class="hero-sub">
        Drop a job description + candidate PDFs — get ranked, scored,
        and analysed results instantly.
    </p>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    """
    Render the configuration sidebar.

    API keys are read from the .env file (via config.py) — NOT entered here.
    The sidebar simply shows which LLM is active based on what keys are loaded.
    """
    from modules.config import ANTHROPIC_API_KEY, GOOGLE_API_KEY, active_llm
    from modules.insights import is_gemini_available

    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("---")

        # ── Active LLM status ────────────────────────────────────────────────
        st.markdown("#### 🔌 Active LLM")

        if ANTHROPIC_API_KEY:
            st.success("⚡ **Claude** (Anthropic) — active", icon="✅")
        else:
            st.caption("No `ANTHROPIC_API_KEY` found in `.env`")

        if GOOGLE_API_KEY and is_gemini_available():
            label = "✨ **Gemini** (Google) — active as secondary"
            if ANTHROPIC_API_KEY:
                label += " *(unused while Claude is set)*"
            st.info(label)
        elif GOOGLE_API_KEY and not is_gemini_available():
            st.warning("`GOOGLE_API_KEY` set but `google-generativeai` not installed.")

        if not ANTHROPIC_API_KEY and not GOOGLE_API_KEY:
            st.warning(
                "No API keys found — using **keyword rules** fallback.\n\n"
                "Add keys to your `.env` file to enable LLM insights.",
                icon="⚠️",
            )

        st.markdown("---")
        st.markdown("#### 🔑 Setting up keys")
        st.code(
            "# .env (project root — never commit this!)\n"
            "ANTHROPIC_API_KEY=sk-ant-...\n"
            "GOOGLE_API_KEY=AIza-...   # optional",
            language="bash",
        )
        st.caption(
            "`.env` is in `.gitignore` — your keys are safe.\n"
            "Copy `.env.example` → `.env` and fill in your values."
        )

        st.markdown("---")
        st.markdown("#### How it works")
        st.markdown("""
1. Paste your **Job Description**
2. Upload **PDF resumes** (multiple OK)
3. Hit **Analyse** — cosine similarity on sentence embeddings
4. **Claude** (or Gemini) writes the narrative insights
        """)
        st.markdown("---")
        st.caption(f"Embedding model: `all-MiniLM-L6-v2`  ·  LLM: `{active_llm()}`")


# ─────────────────────────────────────────────────────────────────────────────
# INPUT PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_input_panel() -> tuple:
    """
    Render the two-column input area (JD + PDF uploader) and the Analyse button.

    Returns:
        Tuple of (jd_text: str, uploaded_files: list, analyse_clicked: bool).
    """
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("##### 📋 Job Description")
        jd_text = st.text_area(
            label="Job Description",
            placeholder="Paste the full job description here…",
            height=300,
            label_visibility="collapsed",
        )

    with col_right:
        st.markdown("##### 📄 Candidate Resumes")
        uploaded_files = st.file_uploader(
            label="Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            st.caption(f"{len(uploaded_files)} file(s) selected")

    st.markdown("<br>", unsafe_allow_html=True)
    analyse_clicked = st.button("🎯  Analyse Candidates", use_container_width=True)

    return jd_text, uploaded_files, analyse_clicked


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY METRICS
# ─────────────────────────────────────────────────────────────────────────────

def render_summary_metrics(results: list[dict]) -> None:
    """
    Show a 4-column strip of summary metrics above the result cards.

    Args:
        results: Ranked list of candidate dicts (must include "insights").
    """
    strong   = sum(1 for r in results if r["insights"]["recommendation"] == "Strong Fit")
    moderate = sum(1 for r in results if r["insights"]["recommendation"] == "Moderate Fit")
    not_fit  = sum(1 for r in results if r["insights"]["recommendation"] == "Not Fit")

    st.markdown("---")
    st.markdown("### 📊 Screening Summary")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates",   len(results))
    m2.metric("Strong Fit",   strong)
    m3.metric("Moderate Fit", moderate)
    m4.metric("Not Fit",      not_fit)

    # Top-candidate callout
    top = results[0]
    st.success(
        f"🏆 **Top candidate:** {top['name']} — "
        f"Score **{top['score']}/100** · {top['insights']['recommendation']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# CANDIDATE CARD
# ─────────────────────────────────────────────────────────────────────────────

def render_candidate_card(rank: int, name: str, score: float, insights: dict) -> None:
    """
    Render a single candidate result as a styled HTML card.

    Args:
        rank:     1-based ranking position.
        name:     Candidate display name.
        score:    Match score (0–100).
        insights: Dict with "strengths", "gaps", "recommendation", "source".
    """
    color   = _score_color(score)
    rec     = insights["recommendation"]
    b_class = _badge_class(rec)
    source  = insights.get("source", "rules")

    source_label = {
        "claude": "⚡ Claude AI",
        "gemini": "✨ Gemini AI",
        "rules":  "🔑 Keyword Rules",
    }.get(source, "🔑 Keyword Rules")

    strengths_html = "".join(f"<li>{s}</li>" for s in insights["strengths"])
    gaps_html      = "".join(f"<li>{g}</li>" for g in insights["gaps"])

    st.markdown(f"""
    <div class="card">
        <div class="card-rank">#{rank}</div>
        <div class="card-name">{name}</div>

        <div class="card-score-wrap">
            <span class="score-pill" style="color:{color};">{score}</span>
            <div class="score-bar-bg">
                <div class="score-bar-fill"
                     style="width:{score}%; background:{color};"></div>
            </div>
            <span class="badge {b_class}">{rec}</span>
            <span style="font-size:.65rem;color:#6b7280;font-family:'DM Mono',monospace;">
                {source_label}
            </span>
        </div>

        <div class="section-label">✦ Key Strengths</div>
        <ul class="insight-list">{strengths_html}</ul>

        <div class="section-label">✦ Key Gaps</div>
        <ul class="insight-list gaps">{gaps_html}</ul>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _score_color(score: float) -> str:
    """Return a CSS hex color based on the score tier."""
    if score >= 70:
        return "#c8f135"   # lime   — Strong Fit
    elif score >= 50:
        return "#f59e0b"   # amber  — Moderate Fit
    return "#ef4444"       # red    — Not Fit


def _badge_class(recommendation: str) -> str:
    """Return the CSS class name for the recommendation badge."""
    return {
        "Strong Fit":   "badge-strong",
        "Moderate Fit": "badge-moderate",
        "Not Fit":      "badge-notfit",
    }.get(recommendation, "badge-moderate")