"""
modules/styles.py
=================
All custom CSS for the HireSense Streamlit app.

Keeping styles in one place makes it easy to retheme the app without
touching any business logic. Call inject_css() once at app startup.
"""

import streamlit as st


def inject_css() -> None:
    """Inject the full custom stylesheet into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root design tokens ─────────────────────────────────────────────────── */
:root {
    --bg:        #0d0f14;
    --surface:   #14171f;
    --border:    #1e2330;
    --accent:    #c8f135;        /* electric lime  */
    --accent2:   #4f8dff;        /* cool blue      */
    --text:      #e8eaf0;
    --muted:     #6b7280;
}

/* ── Global base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1200px; }

/* ── Hero header ─────────────────────────────────────────────────────────── */
.hero {
    display: flex;
    align-items: baseline;
    gap: .6rem;
    margin-bottom: .25rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -.02em;
    color: var(--text);
    line-height: 1;
}
.hero-badge {
    font-family: 'DM Mono', monospace;
    font-size: .75rem;
    background: var(--accent);
    color: #0d0f14;
    padding: .2rem .55rem;
    border-radius: 4px;
    font-weight: 500;
    letter-spacing: .04em;
}
.hero-sub {
    color: var(--muted);
    font-size: .95rem;
    margin-bottom: 2rem;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Form labels ─────────────────────────────────────────────────────────── */
label, .stTextArea label, .stFileUploader label {
    font-family: 'DM Mono', monospace !important;
    font-size: .72rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── Text areas ──────────────────────────────────────────────────────────── */
textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
textarea:focus { border-color: var(--accent) !important; }

/* ── File uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 1px dashed var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
    padding: 1rem !important;
}

/* ── Primary button ──────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #0d0f14 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: .65rem 2rem !important;
    letter-spacing: .02em !important;
    transition: opacity .2s !important;
    width: 100%;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Candidate result cards ──────────────────────────────────────────────── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    transition: border-color .2s;
}
.card:hover { border-color: #2e3347; }

.card-rank {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    color: var(--border);
    position: absolute;
    top: .8rem;
    right: 1.2rem;
    line-height: 1;
    user-select: none;
}

.card-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    margin-bottom: .25rem;
}

/* ── Score row ───────────────────────────────────────────────────────────── */
.card-score-wrap {
    display: flex;
    align-items: center;
    gap: .8rem;
    margin: .6rem 0;
}
.score-pill {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    padding: .15rem .6rem;
    border-radius: 6px;
}
.score-bar-bg {
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 99px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 99px;
}

/* ── Recommendation badges ───────────────────────────────────────────────── */
.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: .7rem;
    padding: .2rem .55rem;
    border-radius: 4px;
    font-weight: 500;
    letter-spacing: .04em;
}
.badge-strong   { background: #14532d; color: #86efac; }
.badge-moderate { background: #451a03; color: #fcd34d; }
.badge-notfit   { background: #450a0a; color: #fca5a5; }

/* ── Insight section labels ──────────────────────────────────────────────── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: .65rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--muted);
    margin: .8rem 0 .3rem;
}

/* ── Strengths / Gaps lists ──────────────────────────────────────────────── */
.insight-list { margin: 0; padding-left: 1.1rem; }
.insight-list li {
    font-size: .88rem;
    color: var(--text);
    margin-bottom: .2rem;
    line-height: 1.5;
}
.insight-list.gaps li { color: #fca5a5; }

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Summary metric tiles ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .8rem 1rem;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: .65rem !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ── Alert / info boxes ──────────────────────────────────────────────────── */
.stAlert { border-radius: 8px !important; }
</style>
"""