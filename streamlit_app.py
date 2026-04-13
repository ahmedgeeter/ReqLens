import os
import streamlit as st
from core.state import init

st.set_page_config(
    page_title="ReqLens",
    page_icon="🔍",
    layout="wide",
)

init()

# Warn early if the API key is missing — no crash, just a clear nudge
try:
    _key_present = bool(os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY"))
except Exception:
    _key_present = bool(os.getenv("GEMINI_API_KEY"))
if not _key_present:
    st.warning(
        "⚠ GEMINI_API_KEY not configured. "
        "Add it to `.streamlit/secrets.toml` or set the environment variable before extracting."
    )

st.title("🔍 ReqLens")
st.caption("Structured requirement extraction and review — paste engineering text, extract, review, export.")

st.markdown(
    """
    - **Extract** — paste notes or upload a .txt file, run extraction, review and validate results
    - **History** — browse and download snapshots saved during this session
    """
)
