"""
dashboard/pages/cases.py
------------------------
Operational Case Management & Triage Queue.
Displays active SIU investigation cases, priority levels,
assigned investigators, and triage actions.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.components import (
    apply_chart_theme,
    card_container,
    inject_theme,
    render_header,
    render_kpi_card,
)
from dashboard.utils.data_loader import load_all_claims_data, load_investigation_cases

st.set_page_config(
    page_title="Investigation Cases | Triage Board",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

render_header(
    title="SIU Investigation Cases & Triage Queue",
    subtitle="Operational triage hub for active fraud investigations and investigator lifecycle management.",
    badge_text="SIU Case Management",
    badge_variant="info",
)

cases_df = load_investigation_cases()
claims_df = load_all_claims_data()

if cases_df.empty:
    st.info("No investigation cases recorded. To open a case, navigate to a claim in the Investigation page.")
    st.stop()

# Enrich cases with claim amount and type if missing
if "claim_amount" not in cases_df.columns and not claims_df.empty:
    cases_df = cases_df.merge(
        claims_df[["claim_id", "claim_amount", "claim_type", "fraud_label"]],
        on="claim_id",
        how="left",
    )

# ── 1. KPI Summary Cards ─────────────────────────────────────────────────────
total_cases = len(cases_df)
new_cases = int((cases_df["status"] == "NEW").sum())
under_review = int((cases_df["status"] == "UNDER_REVIEW").sum())
escalated = int((cases_df["status"] == "ESCALATED").sum())
resolved = int((cases_df["status"] == "RESOLVED").sum())
false_positives = int((cases_df["status"] == "FALSE_POSITIVE").sum())

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    render_kpi_card(
        title="Total Cases",
        value=f"{total_cases:,}",
        subtitle="Active pipeline",
        accent_color="#6366f1",
    )
with c2:
    render_kpi_card(
        title="New / Triage",
        value=f"{new_cases:,}",
        subtitle="Unassigned queue",
        accent_color="#06b6d4",
    )
with c3:
    render_kpi_card(
        title="Under Review",
        value=f"{under_review:,}",
        subtitle="Active inquiries",
        accent_color="#f59e0b",
    )
with c4:
    render_kpi_card(
        title="Escalated",
        value=f"{escalated:,}",
        subtitle="High priority SIU",
        accent_color="#ef4444",
    )
with c5:
    render_kpi_card(
        title="Confirmed Fraud",
        value=f"{resolved:,}",
        subtitle="Resolved claims",
        accent_color="#10b981",
    )
with c6:
    render_kpi_card(
        title="False Positives",
        value=f"{false_positives:,}",
        subtitle="Cleared claims",
        accent_color="#64748b",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 2. Filters & Breakdown ───────────────────────────────────────────────────
col_filter, col_chart = st.columns([1, 1])

with col_filter:
    with card_container("🔍 Queue Filters"):
        status_opts = sorted(cases_df["status"].unique().tolist())
        status_filter = st.multiselect(
            "Filter by Status:",
            options=status_opts,
            default=status_opts,
        )
        priority_opts = sorted(cases_df["priority"].unique().tolist())
        priority_filter = st.multiselect(
            "Filter by Priority:",
            options=priority_opts,
            default=priority_opts,
        )
        min_risk = st.slider("Minimum Risk Score:", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

with col_chart:
    with card_container("📊 Pipeline Distribution"):
        status_counts = cases_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.bar(
            status_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map={
                "NEW": "#06b6d4",
                "UNDER_REVIEW": "#f59e0b",
                "ESCALATED": "#ef4444",
                "RESOLVED": "#10b981",
                "FALSE_POSITIVE": "#64748b",
            },
        )
        apply_chart_theme(fig, height=260)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Apply filters
filtered_cases = cases_df[
    (cases_df["status"].isin(status_filter))
    & (cases_df["priority"].isin(priority_filter))
    & (cases_df["risk_score"] >= min_risk)
].copy()

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 3. Operational Queue Table ───────────────────────────────────────────────
with card_container(f"📋 Triage Worklist ({len(filtered_cases)} Matching Cases)"):
    display_cols = [
        "case_id",
        "claim_id",
        "risk_score",
        "risk_band",
        "priority",
        "status",
        "assigned_to",
        "claim_amount",
        "claim_type",
        "updated_at",
    ]
    available_cols = [c for c in display_cols if c in filtered_cases.columns]
    tbl = filtered_cases[available_cols].copy()
    tbl = tbl.sort_values("risk_score", ascending=False)

    format_dict = {"risk_score": "{:.4f}"}
    if "claim_amount" in tbl.columns:
        format_dict["claim_amount"] = "${:,.2f}"

    st.dataframe(
        tbl.style.format(format_dict).background_gradient(subset=["risk_score"], cmap="YlOrRd"),
        use_container_width=True,
        height=380,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 4. Quick Action to Investigate ───────────────────────────────────────────
with card_container("⚡ Quick Action — Launch 360° Forensic Dossier"):
    c_sel, c_btn = st.columns([3, 1])
    with c_sel:
        selected_jump_claim = st.selectbox(
            "Select Claim ID to inspect in deep-dive dossier:",
            options=filtered_cases["claim_id"].tolist() if not filtered_cases.empty else [],
            label_visibility="collapsed",
        )
    with c_btn:
        if st.button("🔎 Open Dossier", use_container_width=True):
            if selected_jump_claim:
                st.session_state["investigate_claim_id"] = selected_jump_claim
                st.success(f"Claim `{selected_jump_claim}` loaded into session! Navigate to **Investigation** tab.")
