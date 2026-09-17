"""
dashboard/pages/audit_logs.py
-----------------------------
System & Investigation Audit Trail.
Immutable record of all case creations, state transitions, investigator assignments,
and timestamped notes for regulatory compliance and transparency.
"""

from __future__ import annotations

import sqlite3
import pandas as pd
import streamlit as st

from dashboard.utils.data_loader import DB_PATH

st.set_page_config(page_title="Audit Trail | Case Logs", layout="wide")

st.title("📜 Investigation Audit Trail & Activity Logs")
st.markdown(
    "Maintains an immutable, append-only log of every state transition, note, and assignment. "
    "Ensures full accountability, reproducibility, and audit readiness."
)

if not DB_PATH.exists():
    st.warning("Database not found.")
    st.stop()

with sqlite3.connect(DB_PATH) as conn:
    events_df = pd.read_sql_query("SELECT * FROM case_events ORDER BY timestamp DESC", conn)
    notes_df = pd.read_sql_query("SELECT * FROM case_notes ORDER BY created_at DESC", conn)

c1, c2 = st.columns(2)
with c1:
    st.metric("Total State Transition Events", f"{len(events_df):,}")
with c2:
    st.metric("Total Case Notes Recorded", f"{len(notes_df):,}")

st.markdown("---")

tab1, tab2 = st.tabs(["1. Case Events & State Transitions", "2. Investigator Notes Log"])

with tab1:
    st.subheader("Lifecycle Events Log")
    if not events_df.empty:
        # Filter by event type or actor
        actors = ["All"] + sorted(events_df["actor"].dropna().unique().tolist())
        selected_actor = st.selectbox("Filter by Actor:", options=actors)
        if selected_actor != "All":
            events_df = events_df[events_df["actor"] == selected_actor]

        st.dataframe(events_df, use_container_width=True, height=450)
    else:
        st.info("No case events recorded yet.")

with tab2:
    st.subheader("Investigator Notes Log")
    if not notes_df.empty:
        st.dataframe(notes_df, use_container_width=True, height=450)
    else:
        st.info("No investigator notes recorded yet.")
