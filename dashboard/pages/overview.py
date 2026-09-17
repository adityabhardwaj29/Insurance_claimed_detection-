"""
dashboard/pages/overview.py
---------------------------
Executive Overview page for Fraud Analytics Dashboard.
Displays exact executive KPIs, multi-signal score distributions,
and operational high-risk claims triage table.
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.data_loader import compute_executive_kpis, load_all_claims_data
from dashboard.utils.filters import render_sidebar_filters

st.set_page_config(page_title="Executive Overview | Fraud Analytics", layout="wide")

st.title("🛡️ Fraud Analytics Executive Overview")
st.markdown(
    "**Academic Research Demonstration** | Grounded in 320 claims, "
    "multi-signal risk scoring (Phase 8), and active investigation cases."
)
st.caption("All metrics are computed live from active database records and model artifacts. Zero simulated KPIs.")

# Load data and apply filters
raw_df = load_all_claims_data()
filtered_df = render_sidebar_filters(raw_df)

# ── 1. Executive KPIs ────────────────────────────────────────────────────────
kpis = compute_executive_kpis(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric(label="Total Claims", value=f"{kpis['total_claims']:,}")
with c2:
    st.metric(label="Flagged Claims", value=f"{kpis['flagged_claims']:,}", help="Claims classified in HIGH or CRITICAL risk bands")
with c3:
    st.metric(label="High Risk Claims", value=f"{kpis['high_risk_claims']:,}", help="Claims with Final Risk Score >= 0.50")
with c4:
    st.metric(label="Investigation Cases", value=f"{kpis['investigation_cases']:,}", help="Open cases in triage workflow (NEW, UNDER_REVIEW, ESCALATED)")
with c5:
    st.metric(label="Fraud Rate", value=f"{kpis['fraud_rate']:.2f}%", help="Ground-truth confirmed fraud prevalence in dataset")
with c6:
    st.metric(label="Average Risk Score", value=f"{kpis['average_risk_score']:.4f}", help="Mean composite risk score across claims [0.0, 1.0]")

st.markdown("---")

# ── 2. Distributions Row ─────────────────────────────────────────────────────
st.subheader("📊 Multi-Signal Risk & Model Distributions")

tab1, tab2, tab3 = st.tabs([
    "1. Composite Risk Distribution",
    "2. Supervised Fraud Probability (XGBoost)",
    "3. Anomaly Distribution (Isolation Forest)",
])

band_colors = {
    "CRITICAL": "#d90429",
    "HIGH": "#f77f00",
    "MEDIUM": "#fcbf49",
    "LOW": "#2a9d8f",
}

with tab1:
    fig_risk = px.histogram(
        filtered_df,
        x="final_risk_score",
        color="risk_band",
        color_discrete_map=band_colors,
        nbins=30,
        marginal="box",
        title="Composite Risk Score Distribution by Operational Risk Band",
        labels={"final_risk_score": "Composite Risk Score (0-1)", "risk_band": "Risk Band"},
    )
    fig_risk.update_layout(bargap=0.08, height=420)
    st.plotly_chart(fig_risk, use_container_width=True)

with tab2:
    fig_fraud = px.histogram(
        filtered_df,
        x="fraud_probability",
        color="fraud_label",
        color_discrete_map={0: "#457b9d", 1: "#e63946"},
        nbins=25,
        marginal="violin",
        title="Supervised Fraud Probability Distribution by Actual Ground Truth (0=Legitimate, 1=Fraud)",
        labels={"fraud_probability": "Model Predicted Fraud Probability", "fraud_label": "Actual Fraud Label"},
    )
    fig_fraud.update_layout(bargap=0.08, height=420)
    st.plotly_chart(fig_fraud, use_container_width=True)

with tab3:
    fig_anom = px.histogram(
        filtered_df,
        x="anomaly_score",
        nbins=25,
        color_discrete_sequence=["#6a4c93"],
        marginal="box",
        title="Calibrated Isolation Forest + LOF Unsupervised Anomaly Distribution",
        labels={"anomaly_score": "Calibrated Anomaly Score [0, 1]"},
    )
    fig_anom.update_layout(bargap=0.08, height=420)
    st.plotly_chart(fig_anom, use_container_width=True)

st.markdown("---")

# ── 3. High-Risk Claims Table ────────────────────────────────────────────────
st.subheader("🚨 High-Risk Claims Triage Queue")
st.markdown("Claims sorted by highest **Final Risk Score**. Columns required for triage review:")

display_cols = [
    "claim_id",
    "claim_amount",
    "fraud_probability",
    "anomaly_score",
    "graph_risk_score",
    "final_risk_score",
    "risk_band",
    "claim_status",
    "case_status",
]

# Filter to high priority claims or sort by risk
table_df = filtered_df[display_cols].copy()
table_df.columns = [
    "Claim ID",
    "Claim Amount ($)",
    "Fraud Probability",
    "Anomaly Score",
    "Graph Risk",
    "Final Risk",
    "Risk Band",
    "Claim Status",
    "Case Status",
]
table_df = table_df.sort_values("Final Risk", ascending=False)

st.dataframe(
    table_df.style.format({
        "Claim Amount ($)": "${:,.2f}",
        "Fraud Probability": "{:.4f}",
        "Anomaly Score": "{:.4f}",
        "Graph Risk": "{:.4f}",
        "Final Risk": "{:.4f}",
    }).background_gradient(
        subset=["Final Risk"], cmap="YlOrRd"
    ),
    use_container_width=True,
    height=450,
)

# Navigation helper
st.info("💡 To investigate any claim in depth, select **'Investigation'** in the sidebar or search for the Claim ID.")
