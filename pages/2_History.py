import streamlit as st
from core.export import to_csv_bytes
from core.state import init

init()

st.header("History")
st.caption("Snapshots saved during this session. Each entry is a frozen copy — editing the current table won't affect past snapshots.")

history = st.session_state.get("history", [])

if not history:
    st.info("No snapshots saved yet. Go to Extract, review your results, then click 'Save Snapshot'.")
    st.stop()

# Show most recent first
for entry in reversed(history):
    label = f"{entry['timestamp']} — {entry['row_count']} requirement(s)"
    with st.expander(label):
        st.dataframe(entry["df"], use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV",
            data=to_csv_bytes(entry["df"]),
            file_name=f"requirements_{entry['timestamp'].replace(' ', '_').replace(':', '')}.csv",
            mime="text/csv",
            key=f"dl_{entry['timestamp']}",
        )
