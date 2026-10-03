"""
dashboard/pages/audit_logs.py
-----------------------------
System & Investigation Audit Trail.
Immutable record of all case creations, state transitions, investigator assignments,
and timestamped notes for regulatory compliance and transparency.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import sqlite3
import pandas as pd
import streamlit as st

from dashboard.components import (
    card_container,
    inject_theme,
    render_header,
    render_kpi_card,
)
from dashboard.utils.data_loader import DB_PATH

st.set_page_config(
    page_title="Audit Trail | Case Logs",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

render_header(
    title="Investigation Audit Trail & Activity Logs",
    subtitle="Immutable, regulatory-grade audit record of every case state transition, investigator assignment, and forensic note.",
    badge_text="Compliance & Governance",
    badge_variant="primary",
)

from api.db import db

events_df = pd.DataFrame()
notes_df = pd.DataFrame()

if db:
    try:
        e_rows = db.query_all("SELECT * FROM case_events ORDER BY timestamp DESC")
        n_rows = db.query_all("SELECT * FROM case_notes ORDER BY created_at DESC")
        if e_rows:
            events_df = pd.DataFrame(e_rows)
        if n_rows:
            notes_df = pd.DataFrame(n_rows)
    except Exception:
        pass

if events_df.empty and notes_df.empty and DB_PATH.exists():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            events_df = pd.read_sql_query("SELECT * FROM case_events ORDER BY timestamp DESC", conn)
            notes_df = pd.read_sql_query("SELECT * FROM case_notes ORDER BY created_at DESC", conn)
    except Exception:
        pass

if not events_df.empty and "timestamp" in events_df.columns:
    events_df["timestamp"] = events_df["timestamp"].astype(str).str.slice(0, 19)

if not notes_df.empty and "created_at" in notes_df.columns:
    notes_df["created_at"] = notes_df["created_at"].astype(str).str.slice(0, 19)

c1, c2, c3 = st.columns(3)
with c1:
    render_kpi_card(
        title="State Transition Events",
        value=f"{len(events_df):,}",
        subtitle="Immutable case actions",
        accent_color="#3b82f6",
    )
with c2:
    render_kpi_card(
        title="Investigator Notes",
        value=f"{len(notes_df):,}",
        subtitle="Forensic observations",
        accent_color="#10b981",
    )
with c3:
    unique_actors = len(events_df["actor"].dropna().unique()) if not events_df.empty else 0
    render_kpi_card(
        title="Active Investigators",
        value=f"{unique_actors}",
        subtitle="Distinct actors recorded",
        accent_color="#6366f1",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 Case Events & State Transitions", "📝 Forensic Notes Log"])

with tab1:
    with card_container("Chronological Lifecycle Events"):
        if not events_df.empty:
            actors = ["All"] + sorted(events_df["actor"].dropna().unique().tolist())
            c_filter, _ = st.columns([1, 2])
            with c_filter:
                selected_actor = st.selectbox("Filter by Actor:", options=actors)
            if selected_actor != "All":
                display_events = events_df[events_df["actor"] == selected_actor]
            else:
                display_events = events_df

            st.dataframe(
                display_events,
                use_container_width=True,
                height=420,
            )
        else:
            st.info("No case events recorded yet.")

with tab2:
    with card_container("Investigator Notes & Observations"):
        if not notes_df.empty:
            st.dataframe(
                notes_df,
                use_container_width=True,
                height=420,
            )
        else:
            st.info("No investigator notes recorded yet.")
