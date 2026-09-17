"""
dashboard/pages/cases.py
------------------------
Operational Case Management & Triage Queue.
Displays active SIU investigation cases, priority levels,
assigned investigators, and triage actions.
"""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.utils.data_loader import load_all_claims_data, load_investigation_cases

st.set_page_config(page_title="Investigation Cases | Triage Board", layout="wide")

st.title("📁 SIU Investigation Cases & Triage Queue")
st.markdown(
    "Operational triage hub for active fraud investigations. "
    "All case lifecycle transitions and investigator notes are preserved with an immutable audit trail."
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
    st.metric("Total Cases", f"{total_cases:,}")
with c2:
    st.metric("New / Unassigned", f"{new_cases:,}")
with c3:
    st.metric("Under Review", f"{under_review:,}")
with c4:
    st.metric("Escalated", f"{escalated:,}")
with c5:
    st.metric("Resolved (Confirmed)", f"{resolved:,}")
with c6:
    st.metric("False Positives", f"{false_positives:,}")

st.markdown("---")

# ── 2. Filters & Breakdown ───────────────────────────────────────────────────
col_filter, col_chart = st.columns([1, 1])

with col_filter:
    st.subheader("Filter Queue")
    status_filter = st.multiselect(
        "Filter by Status:",
        options=sorted(cases_df["status"].unique().tolist()),
        default=sorted(cases_df["status"].unique().tolist()),
    )
    priority_filter = st.multiselect(
        "Filter by Priority:",
        options=sorted(cases_df["priority"].unique().tolist()),
        default=sorted(cases_df["priority"].unique().tolist()),
    )
    min_risk = st.slider("Minimum Risk Score:", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

with col_chart:
    st.subheader("Cases by Priority & Status")
    status_counts = cases_df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.bar(
        status_counts,
        x="Status",
        y="Count",
        color="Status",
        color_discrete_map={
            "NEW": "#3a86ff",
            "UNDER_REVIEW": "#fcbf49",
            "ESCALATED": "#d90429",
            "RESOLVED": "#2a9d8f",
            "FALSE_POSITIVE": "#6c757d",
        },
        height=260,
    )
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# Apply filters
filtered_cases = cases_df[
    (cases_df["status"].isin(status_filter))
    & (cases_df["priority"].isin(priority_filter))
    & (cases_df["risk_score"] >= min_risk)
].copy()

st.markdown("---")

# ── 3. Operational Queue Table ───────────────────────────────────────────────
st.subheader(f"📋 Triage Worklist ({len(filtered_cases)} Matching Cases)")

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
    height=400,
)

# ── 4. Quick Action to Investigate ───────────────────────────────────────────
st.markdown("---")
st.subheader("🚀 Quick Jump to Investigation Dossier")

selected_jump_claim = st.selectbox(
    "Choose a Claim ID to inspect full dossier:",
    options=filtered_cases["claim_id"].tolist() if not filtered_cases.empty else [],
)

if st.button("🔎 Open 360° Investigation Dossier"):
    if selected_jump_claim:
        st.session_state["investigate_claim_id"] = selected_jump_claim
        st.success(f"Selected Claim `{selected_jump_claim}`. Navigate to the 'Investigation' page to inspect the full dossier.")
