"""
app.py — Entry point
====================
Bootstraps the Streamlit app. All logic lives in /modules.
Run: streamlit run app.py
"""

from modules.ui import render_app

render_app()