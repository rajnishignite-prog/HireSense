"""
modules/ui.py
=============
Top-level UI orchestrator.

render_app() is the single entry point called by app.py.
It wires together all modules in the correct order:
  styles -> sidebar -> input -> processing pipeline -> results

API keys are NEVER handled here — they live in .env and are
accessed only through modules/config.py and modules/insights.py.
"""

import time
import streamlit as st

from modules.styles     import inject_css
from modules.components import (
    render_hero,
    render_sidebar,
    render_input_panel,
    render_summary_metrics,
    render_candidate_card,
)
from modules.pdf_extractor import extract_text, clean_candidate_name
from modules.scorer        import load_model, embed_text, compute_match_score, rank_candidates
from modules.insights      import get_insights
from modules.exporter      import build_csv


def render_app() -> None:
    """
    Main application function — called by app.py.

    Flow:
      1.  Configure the Streamlit page
      2.  Inject custom CSS
      3.  Render hero header
      4.  Render sidebar (shows .env key status — no user input)
      5.  Render input panel (JD textarea + PDF uploader)
      6.  On Analyse click:
            a. Validate inputs
            b. Load embedding model
            c. Embed the JD
            d. For each PDF: extract -> embed -> score -> get insights
            e. Rank all candidates
            f. Display summary metrics
            g. Display individual cards
            h. Offer CSV download
    """

    # 1. Page config
    st.set_page_config(
        page_title="HireSense · AI Screening",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Styles
    inject_css()

    # 3. Hero
    render_hero()

    # 4. Sidebar — shows which LLM is active (keys from .env, not UI)
    render_sidebar()

    # 5. Input panel
    jd_text, uploaded_files, analyse_clicked = render_input_panel()

    # 6. Processing
    if not analyse_clicked:
        return

    # Validate inputs
    if not jd_text.strip():
        st.error("⚠️  Please enter a Job Description before analysing.")
        return

    if not uploaded_files:
        st.error("⚠️  Please upload at least one PDF resume.")
        return

    # Load model
    with st.spinner("Loading embedding model…"):
        model = load_model()

    # Embed the job description
    jd_embedding = embed_text(model, jd_text)

    # Process each resume
    results  = []
    n_files  = len(uploaded_files)
    progress = st.progress(0, text="Extracting & scoring resumes…")

    for i, pdf_file in enumerate(uploaded_files):
        candidate_name = clean_candidate_name(pdf_file.name)

        pdf_file.seek(0)
        resume_text = extract_text(pdf_file)

        if not resume_text:
            st.warning(
                f"⚠️  Could not extract text from **{pdf_file.name}** — "
                "the file may be empty, scanned, or password-protected. Skipping."
            )
            progress.progress((i + 1) / n_files)
            continue

        # Score
        resume_embedding = embed_text(model, resume_text)
        score            = compute_match_score(jd_embedding, resume_embedding)

        # LLM insights — keys loaded from .env inside get_insights()
        try:
            insights = get_insights(jd=jd_text, resume_text=resume_text, score=score)
        except ValueError as e:
            # Bad API key in .env — show once and stop
            st.error(f"🔑 API key error: {e}")
            return

        results.append({
            "name":     candidate_name,
            "score":    score,
            "insights": insights,
            "filename": pdf_file.name,
        })

        progress.progress(
            (i + 1) / n_files,
            text=f"Processed {i + 1}/{n_files}: {candidate_name}",
        )
        time.sleep(0.05)

    progress.empty()

    if not results:
        st.error(
            "No valid resumes could be processed. "
            "Please check that your PDFs contain selectable text."
        )
        return

    # Rank
    results = rank_candidates(results)

    # Summary metrics
    render_summary_metrics(results)

    # Candidate cards
    st.markdown("### 🎯 Candidate Rankings")
    for r in results:
        render_candidate_card(
            rank     = r["rank"],
            name     = r["name"],
            score    = r["score"],
            insights = r["insights"],
        )

    # CSV download
    st.download_button(
        label     = "⬇️  Download Results as CSV",
        data      = build_csv(results),
        file_name = "screening_results.csv",
        mime      = "text/csv",
    )