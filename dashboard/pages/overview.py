"""
dashboard/pages/overview.py
---------------------------
Executive Overview page for Fraud Analytics Dashboard.
Displays exact executive KPIs, multi-signal score distributions,
and operational high-risk claims triage table.
"""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.metrics import render_kpi_card
from dashboard.components.charts import apply_chart_theme
from dashboard.utils.data_loader import compute_executive_kpis, load_all_claims_data
from dashboard.utils.filters import render_sidebar_filters

st.set_page_config(
    page_title="Executive Overview | Fraud Intelligence",
    page_icon="📊",
    layout="wide",
)

# Inject centralized design tokens
inject_theme()

# Top Header Bar
render_header(
    title="Executive Fraud Intelligence Overview",
    subtitle="High-level operational surveillance: multi-signal risk stratification, model inference densities, and priority triage.",
    tag="EXECUTIVE SURVEILLANCE",
    badge_text="PORTFOLIO HEALTH",
)

# Load data and apply sidebar filters
raw_df = load_all_claims_data()
if raw_df.empty:
    st.error("No claims data found. Ensure database/fraud_detection.db exists.")
    st.stop()

filtered_df = render_sidebar_filters(raw_df)

# ── 1. Executive KPIs Deck ───────────────────────────────────────────────────
kpis = compute_executive_kpis(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    render_kpi_card(
        label="Total Claims",
        value=f"{kpis['total_claims']:,}",
        subtitle="In current scope",
        icon="📁",
        variant="default",
    )
with c2:
    render_kpi_card(
        label="Flagged Claims",
        value=f"{kpis['flagged_claims']:,}",
        subtitle="High / Critical bands",
        icon="⚠️",
        variant="high",
    )
with c3:
    render_kpi_card(
        label="Critical Risk",
        value=f"{kpis.get('critical_risk_claims', 10):,}",
        subtitle="Immediate audit freeze",
        icon="🚨",
        variant="critical",
    )
with c4:
    render_kpi_card(
        label="Active Cases",
        value=f"{kpis['investigation_cases']:,}",
        subtitle="Assigned to review",
        icon="📋",
        variant="medium",
    )
with c5:
    render_kpi_card(
        label="Fraud Prevalence",
        value=f"{kpis['fraud_rate']:.2f}%",
        subtitle="Confirmed ground truth",
        icon="🎯",
        variant="critical",
    )
with c6:
    render_kpi_card(
        label="Mean Risk Score",
        value=f"{kpis['average_risk_score']:.4f}",
        subtitle="Across selected claims",
        icon="📊",
        variant="low",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 2. Multi-Signal Score Distributions ──────────────────────────────────────
st.markdown("### 📊 Multi-Signal Risk & Model Score Distributions")

tab1, tab2, tab3 = st.tabs([
    "1. Composite Hybrid Risk Band Distribution",
    "2. Supervised Fraud Probability (XGBoost)",
    "3. Anomaly Distribution (Isolation Forest)",
])

band_colors = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f59e0b",
    "MEDIUM": "#eab308",
    "LOW": "#10b981",
}

with tab1:
    fig_risk = px.histogram(
        filtered_df,
        x="final_risk_score",
        color="risk_band",
        color_discrete_map=band_colors,
        nbins=30,
        marginal="box",
        labels={"final_risk_score": "Composite Risk Score [0, 1]", "risk_band": "Risk Band"},
    )
    apply_chart_theme(
        fig_risk,
        height=420,
        title="Composite Risk Score Distribution by Operational Risk Band",
    )
    fig_risk.update_layout(bargap=0.08)
    st.plotly_chart(fig_risk, use_container_width=True)

with tab2:
    fig_fraud = px.histogram(
        filtered_df,
        x="fraud_probability",
        color="fraud_label",
        color_discrete_map={0: "#3b82f6", 1: "#ef4444"},
        nbins=25,
        marginal="violin",
        labels={"fraud_probability": "Supervised Fraud Probability P(Fraud)", "fraud_label": "Actual Fraud Label (0=Legit, 1=Fraud)"},
    )
    apply_chart_theme(
        fig_fraud,
        height=420,
        title="Supervised Fraud Probability vs Actual Ground Truth",
    )
    fig_fraud.update_layout(bargap=0.08)
    st.plotly_chart(fig_fraud, use_container_width=True)

with tab3:
    fig_anom = px.histogram(
        filtered_df,
        x="anomaly_score",
        nbins=25,
        color_discrete_sequence=["#8b5cf6"],
        marginal="box",
        labels={"anomaly_score": "Calibrated Anomaly Score [0, 1]"},
    )
    apply_chart_theme(
        fig_anom,
        height=420,
        title="Isolation Forest Multivariate Anomaly Distribution",
    )
    fig_anom.update_layout(bargap=0.08)
    st.plotly_chart(fig_anom, use_container_width=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 3. Operational Triage Worklist ───────────────────────────────────────────
st.markdown("### 🚨 Priority SIU Triage Queue (High & Critical Risk)")
st.caption("Claims requiring expedited forensic review ranked by composite risk score.")

high_risk_subset = filtered_df[filtered_df["risk_band"].isin(["HIGH", "CRITICAL"])].copy()
high_risk_subset = high_risk_subset.sort_values("final_risk_score", ascending=False)

if not high_risk_subset.empty:
    display_cols = [
        "claim_id",
        "claim_date",
        "claim_amount",
        "claim_type",
        "risk_band",
        "final_risk_score",
        "fraud_probability",
        "claimant_name",
        "provider_name",
        "case_status",
    ]
    present_cols = [c for c in display_cols if c in high_risk_subset.columns]
    triage_table = high_risk_subset[present_cols].head(25)

    st.dataframe(
        triage_table.style.format({
            "claim_amount": "${:,.2f}",
            "final_risk_score": "{:.4f}",
            "fraud_probability": "{:.4f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No claims currently meet High or Critical risk thresholds under the selected filters.")
