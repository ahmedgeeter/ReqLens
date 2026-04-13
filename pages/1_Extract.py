from datetime import datetime
import streamlit as st
from core.gemini import extract
from core.schema import assign_ids, to_dataframe, REQ_TYPES, PRIORITIES, REVIEW_STATUSES
from core.validators import summarize_issues
from core.export import to_csv_bytes
from core.state import init

init()

st.header("Extract Requirements")
st.caption("Paste raw engineering text or upload a .txt file. The model extracts structured requirements for you to review.")

# --- Input ---
uploaded = st.file_uploader("Upload a .txt file (optional)", type=["txt"])
if uploaded:
    default_text = uploaded.read().decode("utf-8")
else:
    default_text = st.session_state.get("_last_input", "")

raw_text = st.text_area("Paste engineering text here", value=default_text, height=200)

if st.button("Extract Requirements", type="primary"):
    if not raw_text.strip():
        st.warning("Nothing to extract. Paste some text first.")
    else:
        st.session_state["_last_input"] = raw_text
        with st.spinner("Calling Gemini…"):
            result = extract(raw_text)

        if not result["ok"]:
            st.error(f"Extraction failed: {result['error']}")
            if result["raw_response"]:
                with st.expander("Raw model response"):
                    st.text(result["raw_response"])
        else:
            records = result["records"]
            if not records:
                st.warning("Model returned no requirements. Try a more detailed input.")
            else:
                assign_ids(records)
                st.session_state["current_df"] = to_dataframe(records)
                st.success(f"Extracted {len(records)} requirements.")
                st.rerun()

# --- Review table ---
df = st.session_state["current_df"]

if df is None:
    st.info("No requirements loaded yet. Extract some above.")
else:
    issues = summarize_issues(df)

    # Validation warnings
    if issues["empty_text"]:
        st.warning(f"{len(issues['empty_text'])} row(s) have empty requirement text.")
    if issues["invalid_type"]:
        st.warning(f"{len(issues['invalid_type'])} row(s) have an unrecognised type.")
    if issues["invalid_priority"]:
        st.warning(f"{len(issues['invalid_priority'])} row(s) have an unrecognised priority.")
    if issues["duplicates"]:
        st.warning(f"{len(issues['duplicates'])} row(s) flagged as potential duplicates.")
    if not any([issues["empty_text"], issues["invalid_type"], issues["invalid_priority"], issues["duplicates"]]):
        st.success("No validation issues found.")

    # Summary metrics
    accepted = int((df["review_status"] == "Accepted").sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("Accepted", accepted)
    c3.metric("Invalid rows", len(issues["invalid_rows"]))
    c4.metric("Duplicates", len(issues["duplicates"]))

    st.divider()

    col_cfg = {
        "req_id":        st.column_config.TextColumn("ID", disabled=True, width="small"),
        "text":          st.column_config.TextColumn("Requirement", width="large"),
        "req_type":      st.column_config.SelectboxColumn("Type", options=REQ_TYPES, required=True),
        "priority":      st.column_config.SelectboxColumn("Priority", options=PRIORITIES, required=True),
        "source_phrase": st.column_config.TextColumn("Source phrase", disabled=True, width="medium"),
        "review_status": st.column_config.SelectboxColumn("Status", options=REVIEW_STATUSES, required=True),
    }

    edited = st.data_editor(
        df,
        column_config=col_cfg,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="extract_editor",
    )

    # Preserve read-only columns from the stored df so edits to those cells are ignored
    edited["req_id"] = df["req_id"].values
    edited["source_phrase"] = df["source_phrase"].values

    # --- Actions ---
    col_export, col_snapshot, _ = st.columns([1, 1, 4])

    with col_export:
        st.download_button(
            "Export CSV",
            data=to_csv_bytes(edited),
            file_name="requirements.csv",
            mime="text/csv",
        )

    with col_snapshot:
        if st.button("Save Snapshot"):
            st.session_state["current_df"] = edited
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "df": edited.copy(),
                "row_count": len(edited),
            }
            st.session_state["history"].append(entry)
            st.success("Snapshot saved.")
