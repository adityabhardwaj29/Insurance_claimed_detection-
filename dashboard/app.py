"""
dashboard/app.py
----------------
Main Entry Portal for the Multi-Signal Graph-Enhanced Insurance Fraud Analytics Dashboard.
Coordinates multi-page navigation, executive summary, and academic research disclosure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from dashboard.components.layout import inject_theme, render_sidebar_officer_session
from dashboard.components.header import render_header
from dashboard.components.metrics import render_kpi_card
from dashboard.utils.data_loader import compute_executive_kpis, load_all_claims_data
from dashboard.utils.live_sync import render_live_sync_controller

st.set_page_config(
    page_title="Fraud Intelligence | Graph-Enhanced Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject centralized design tokens and component styling
inject_theme()

# Render Officer Session Widget in Sidebar
render_sidebar_officer_session()

# Top Header Bar
render_header(
    title="Insurance Fraud Intelligence Platform",
    subtitle="Enterprise Multi-Signal Decision Support: Supervised ML, Isolation Forest, Heterogeneous Knowledge Graphs & SIU Triage",
    tag="DECISION INTELLIGENCE PORTAL",
    badge_text="ENTERPRISE SAAS",
)

# Academic Integrity Callout
st.markdown(
    """
    <div class="saas-callout">
        <div class="saas-callout-text">
            <strong>Academic Research & Decision Support:</strong> All metrics, model inferences, and graph properties
            are computed from active SQLite database records (320 claims) and deterministic algorithms.
            Zero synthetic or random numbers are generated for dashboard KPIs.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Executive KPI Ribbon ─────────────────────────────────────────────────────
df = load_all_claims_data()
render_live_sync_controller(total_records=len(df))
kpis = compute_executive_kpis(df)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    render_kpi_card(
        label="Total Claims",
        value=f"{kpis['total_claims']:,}",
        subtitle="Active relational records",
        icon="📁",
        variant="default",
    )
with col2:
    render_kpi_card(
        label="Flagged Claims",
        value=f"{kpis['flagged_claims']:,}",
        subtitle="High / Critical risk bands",
        icon="⚠️",
        variant="high",
    )
with col3:
    render_kpi_card(
        label="Critical Claims",
        value=f"{kpis['critical_risk_claims'] if 'critical_risk_claims' in kpis else kpis['high_risk_claims']:,}",
        subtitle="Priority SIU investigation",
        icon="🚨",
        variant="critical",
    )
with col4:
    render_kpi_card(
        label="Active Cases",
        value=f"{kpis['investigation_cases']:,}",
        subtitle="Assigned to review queue",
        icon="📋",
        variant="medium",
    )
with col5:
    render_kpi_card(
        label="Fraud Prevalence",
        value=f"{kpis['fraud_rate']:.2f}%",
        subtitle="Synthetic ground truth",
        icon="🎯",
        variant="critical",
    )
with col6:
    render_kpi_card(
        label="Mean Risk Score",
        value=f"{kpis['average_risk_score']:.4f}",
        subtitle="Normalized composite [0, 1]",
        icon="📊",
        variant="low",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── Navigation Modules ───────────────────────────────────────────────────────
st.markdown("### 🧭 Platform Subsystems & Analytical Modules")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.markdown(
        """
        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">📊 Executive Overview & Triage</h4>
                <span class="saas-badge info">EXECUTIVE</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Comprehensive operational summary covering risk band distributions, supervised fraud probabilities,
                Isolation Forest outlier densities, and priority triage worklists.
            </p>
            <a href="overview" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                Open Executive Overview →
            </a>
        </div>

        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">🔎 360° Claim Investigation Dossier</h4>
                <span class="saas-badge critical">CORE SIU</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Deep-dive investigation workspace combining relational entity facts, SHAP local feature attributions,
                subnetwork graph evidence, interactive note recording, and audited status updates.
            </p>
            <a href="investigation" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                Launch Investigation Workspace →
            </a>
        </div>

        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">🕸️ Knowledge Graph & Collusion Rings</h4>
                <span class="saas-badge medium">NETWORK</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Multi-entity graph visualizer linking Claims, Claimants, Policies, Vehicles, Providers, and Invoices.
                Detects shared repair facility collusion, serial filers, and high-degree fraud hubs.
            </p>
            <a href="network" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                Explore Knowledge Graph →
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col2:
    st.markdown(
        """
        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">📁 Investigation Case Management</h4>
                <span class="saas-badge high">WORKFLOW</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Enterprise SIU case management queue with audited lifecycle transitions (NEW → UNDER_REVIEW →
                ESCALATED → RESOLVED / FALSE_POSITIVE) without mutating ground-truth labels.
            </p>
            <a href="cases" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                View Case Management Queue →
            </a>
        </div>

        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">📑 Duplicate Claim Detection</h4>
                <span class="saas-badge neutral">NLP / SIMILARITY</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Pairwise TF-IDF cosine similarity matrix and cluster breakdown identifying identical or modified
                claim submissions across policies, repair shops, and vehicles.
            </p>
            <a href="duplicates" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                Inspect Duplicate Claims →
            </a>
        </div>

        <div class="saas-card">
            <div class="saas-card-header">
                <h4 class="saas-card-title">📈 ML Performance & System Health</h4>
                <span class="saas-badge low">MONITORING</span>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">
                Benchmarking supervised classifiers (XGBoost, Random Forest, HistGradientBoosting) with PR-AUC,
                ROC-AUC, Precision@K, plus real-time system monitoring and immutable audit logs.
            </p>
            <a href="model_performance" target="_self" style="font-size: 0.84rem; font-weight: 600; color: var(--brand-primary); text-decoration: none;">
                View Models & Benchmarks →
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── End-to-End Pipeline Flow ─────────────────────────────────────────────────
st.markdown("### 🏗️ End-to-End Multi-Signal Analytical Architecture")

st.markdown(
    """
    <div class="saas-card">
        <div style="font-family: var(--font-mono); font-size: 0.82rem; color: #1E3A8A; background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 1.25rem; border-radius: 8px; overflow-x: auto; line-height: 1.6; font-weight: 500;">
[1. RAW CSVs] ──> [2. 3NF NORMALIZATION (SQLite)] ──> [3. CAUSAL FEATURE ENGINEERING]
                           |                                        |
                           +──────────────────+─────────────────────+
                                              |
               ┌──────────────────────────────┼──────────────────────────────┐
               │                              │                              │
               v                              v                              v
    [4. SUPERVISED XGBOOST]        [5. ISOLATION FOREST]         [6. KNOWLEDGE GRAPH]
       P(Fraud) Inferences            Anomaly Deviation             Network Topology
               │                              │                              │
               └──────────────────────────────┼──────────────────────────────┘
                                              |
                                              v
                              [7. HYBRID MULTI-SIGNAL ENGINE]
                                  Composite Score [0, 1]
                                  4 Operational Risk Bands
                                              |
                                              v
                              [8. SIU INVESTIGATION WORKSPACE]
                                  SHAP Attributions + Network Subgraphs
                                  Audited Lifecycle Management
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
