"""
modules/components.py
=====================
Reusable Streamlit UI components for HireSense.

Uses native Streamlit elements only — no raw HTML cards —
so output always renders correctly regardless of Streamlit version.
"""

import streamlit as st


# =============================================================================
# HERO
# =============================================================================

def render_hero() -> None:
    """Render the branded page header."""
    st.markdown(
        "<h1 style='font-size:2.4rem;font-weight:800;margin-bottom:0;'>🎯 HireSense</h1>",
        unsafe_allow_html=True,
    )
    st.caption("AI-powered resume screening · Gemini 2.5 Flash Lite · sentence-transformers")
    st.divider()


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar() -> None:
    """
    Render the configuration sidebar.
    Shows which LLM is active based on .env — no user key input.
    """
    from modules.config import GOOGLE_API_KEY, active_llm

    with st.sidebar:
        st.markdown("## ⚙️ HireSense")
        st.divider()

        st.markdown("#### 🔌 Active LLM")
        if GOOGLE_API_KEY:
            st.success(" Gemini 2.5 Flash Lite — active", icon="✅")
        else:
            st.warning(
                "No `GOOGLE_API_KEY` in `.env`.\n\nUsing keyword rules fallback.",
                icon="⚠️",
            )

        st.divider()
        st.markdown("#### 🔑 Get key")
        st.markdown(
            "1. [aistudio.google.com](https://aistudio.google.com)\n"
            "2. Click **Get API key** — no credit card\n"
            "3. Add to `.env`:"
        )
        st.code("GOOGLE_API_KEY=AIza-...", language="bash")

        st.divider()
        st.markdown("#### How it works")
        st.markdown(
            "1. Paste **Job Description**\n"
            "2. Upload **PDF resumes**\n"
            "3. Click **Analyse**\n"
            "4. Get ranked results instantly"
        )
        st.divider()
        st.caption(f"LLM: `{active_llm()}`\nEmbedding: `all-MiniLM-L6-v2`")


# =============================================================================
# INPUT PANEL
# =============================================================================

def render_input_panel() -> tuple:
    """
    Render JD textarea + PDF uploader side by side.
    Returns (jd_text, uploaded_files, analyse_clicked).
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
            st.caption(f"✅ {len(uploaded_files)} file(s) selected")

    st.markdown(" ")
    analyse_clicked = st.button(
        "🔍  Analyse Candidates",
        use_container_width=True,
        type="primary",
    )

    return jd_text, uploaded_files, analyse_clicked


# =============================================================================
# SUMMARY METRICS
# =============================================================================

def render_summary_metrics(results: list[dict]) -> None:
    """Show 4-column summary strip + top candidate callout."""
    strong   = sum(1 for r in results if r["insights"]["recommendation"] == "Strong Fit")
    moderate = sum(1 for r in results if r["insights"]["recommendation"] == "Moderate Fit")
    not_fit  = sum(1 for r in results if r["insights"]["recommendation"] == "Not Fit")

    st.divider()
    st.markdown("### 📊 Screening Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Candidates", len(results))
    c2.metric("✅ Strong Fit",    strong)
    c3.metric("🟡 Moderate Fit",  moderate)
    c4.metric("❌ Not Fit",       not_fit)

    top = results[0]
    st.success(
        f"🏆 **Top Candidate:** {top['name']}  |  "
        f"Score: **{top['score']}/100**  |  {top['insights']['recommendation']}"
    )


# =============================================================================
# CANDIDATE CARD  (native Streamlit — no raw HTML)
# =============================================================================

def render_candidate_card(rank: int, name: str, score: float, insights: dict) -> None:
    """
    Render one candidate result using native Streamlit widgets.
    No raw HTML — works reliably on all Streamlit versions.
    """
    rec    = insights["recommendation"]
    source = insights.get("source", "rules")

    # Colour and emoji based on recommendation
    rec_config = {
        "Strong Fit":   ("🟢", "green",  "✅ Strong Fit"),
        "Moderate Fit": ("🟡", "orange", "🟡 Moderate Fit"),
        "Not Fit":      ("🔴", "red",    "❌ Not Fit"),
    }
    dot, color, rec_label = rec_config.get(rec, ("⚪", "gray", rec))

    source_label = {
        "gemini": "✨ Gemini AI",
        "rules":  "🔑 Keyword Rules",
    }.get(source, "🔑 Keyword Rules")

    # Card container using Streamlit's native container + border
    with st.container(border=True):

        # ── Header row: rank · name · badge ──────────────────────────────────
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown(f"### #{rank}  {name}")
        with h_col2:
            st.markdown(
                f"<div style='text-align:right;padding-top:8px;'>"
                f"<span style='background:{'#14532d' if rec=='Strong Fit' else '#451a03' if rec=='Moderate Fit' else '#450a0a'};"
                f"color:{'#86efac' if rec=='Strong Fit' else '#fcd34d' if rec=='Moderate Fit' else '#fca5a5'};"
                f"padding:4px 12px;border-radius:6px;font-size:0.8rem;font-weight:600;'>"
                f"{rec_label}</span></div>",
                unsafe_allow_html=True,
            )

        # ── Score bar ─────────────────────────────────────────────────────────
        score_col, bar_col = st.columns([1, 4])
        with score_col:
            bar_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
            st.markdown(
                f"<p style='font-size:2.2rem;font-weight:700;color:{bar_color};"
                f"margin:0;line-height:1.2;'>{score}<span style='font-size:1rem;"
                f"color:#6b7280;'>/100</span></p>",
                unsafe_allow_html=True,
            )
        with bar_col:
            st.progress(int(score), text=f"Match Score  ·  {source_label}")

        # ── Strengths & Gaps side by side ─────────────────────────────────────
        s_col, g_col = st.columns(2)

        with s_col:
            st.markdown("**✦ Key Strengths**")
            for s in insights.get("strengths", []):
                st.markdown(f"- ✅ {s}")

        with g_col:
            st.markdown("**✦ Key Gaps**")
            for g in insights.get("gaps", []):
                st.markdown(f"- ⚠️ {g}")