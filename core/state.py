import streamlit as st


def init():
    """Call at the top of every page to ensure session state keys exist."""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "current_df" not in st.session_state:
        st.session_state["current_df"] = None
