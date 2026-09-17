"""
dashboard/app.py
----------------
Main Entry Portal for the Multi-Signal Graph-Enhanced Insurance Fraud Analytics Dashboard.
Coordinates multi-page navigation, executive summary, and academic research disclosure.
"""

from __future__ import annotations

import streamlit as st

from dashboard.utils.data_loader import compute_executive_kpis, load_all_claims_data

st.set_page_config(
    page_title="Graph-Enhanced Insurance Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Title & Research Disclosure ──────────────────────────────────────────────
st.title("🛡️ Graph-Enhanced Insurance Claim Fraud Detection")
st.markdown(
    "### **Multi-Signal Academic Research & Decision Intelligence Platform**\n"
    "Integrating **Supervised Machine Learning**, **Unsupervised Anomaly Detection**, "
    "**Heterogeneous Knowledge Graphs**, and **Human-in-the-Loop Case Management**."
)

st.markdown(
    """
    > **Academic Integrity Statement:** This platform operates on empirical database records (320 claims)
    > and deterministic model outputs. Zero synthetic or random numbers are generated for dashboard KPIs.
    """
)

# ── Quick KPI Snapshot ───────────────────────────────────────────────────────
df = load_all_claims_data()
kpis = compute_executive_kpis(df)

st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Total Claims", f"{kpis['total_claims']:,}")
with c2:
    st.metric("Flagged Claims", f"{kpis['flagged_claims']:,}", help="Claims in High/Critical risk bands")
with c3:
    st.metric("High Risk Claims", f"{kpis['high_risk_claims']:,}", help="Claims with score >= 0.50")
with c4:
    st.metric("Active Cases", f"{kpis['investigation_cases']:,}", help="Cases in review queue")
with c5:
    st.metric("Ground Truth Fraud Rate", f"{kpis['fraud_rate']:.2f}%")
with c6:
    st.metric("Mean Risk Score", f"{kpis['average_risk_score']:.4f}")
st.markdown("---")

# ── Navigation Cards ─────────────────────────────────────────────────────────
st.subheader("🧭 Dashboard Navigation & Modules")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        #### 📊 [Executive Overview](pages/overview.py)
        - 6 Executive KPI summary cards
        - Composite risk distribution by operational band
        - Supervised fraud probability distribution vs actual ground truth
        - Calibrated Isolation Forest anomaly score distribution
        - Interactive high-risk claims triage queue

        #### 📑 [Duplicate Claim Analysis](pages/duplicates.py)
        - Pairwise fuzzy and exact similarity score histograms
        - Duplicate detection category clusters (Opportunistic, Organized, Recycled)
        - Side-by-side attribute matching across invoices, claimants, and vehicles

        #### 🕸️ [Graph Relationship & Network](pages/network.py)
        - Interactive multi-entity knowledge graph visualizer
        - Connects Claim ↔ Claimant ↔ Policy ↔ Vehicle ↔ Provider ↔ Location
        - Node inspector with instant entity attribute lookup
        - Provider collusion hubs and multi-claim concentration tables

        #### 🔎 [360° Claim Investigation Dossier](pages/investigation.py)
        - Full dossier linking claim, policy, claimant, vehicle, provider, invoice
        - Multi-signal radar/bar decomposition with explainable risk reasons
        - Interactive case actions: update status, assign investigator, add notes
        - Immutable chronological case audit trail
        """
    )

with col2:
    st.markdown(
        """
        #### 📁 [Investigation Cases & Triage Queue](pages/cases.py)
        - Operational SIU worklist of all active investigation cases
        - Priority and status filtering
        - Direct deep-links into single-claim investigation dossiers

        #### 📈 [Model Performance & Benchmarks](pages/model_performance.py)
        - Supervised XGBoost metrics: Accuracy, Precision, Recall, F1, PR-AUC, ROC-AUC
        - Full confusion matrix and multi-model benchmark table
        - Unsupervised anomaly calibration and contamination parameters
        - Graph topology metrics: Degree centrality, density, community modularity

        #### 📑 [Claims Explorer](pages/claims.py)
        - Multi-field text search, column sorting, and CSV export across all 320 claims

        #### 📜 [Audit Logs](pages/audit_logs.py) & 🖥️ [Monitoring](pages/monitoring.py)
        - Complete immutable activity log of all state changes
        - System health checks, artifact verification, and database integrity
        """
    )

st.markdown("---")

# ── System Architecture Diagram ──────────────────────────────────────────────
st.subheader("🏗️ Multi-Phase End-to-End System Architecture")

st.markdown(
    """
    ```
    +-----------------------------------------------------------------------------------------------+
    |                                   RELATIONAL DATA CORE (Phases 1 & 2)                         |
    |   [Claimants] <---> [Policies] <---> [Claims] <---> [Invoices] <---> [Providers / Vehicles]  |
    +-----------------------------------------------------------------------------------------------+
                                                    |
          +-----------------------------------------+-----------------------------------------+
          |                                         |                                         |
          v                                         v                                         v
    +-------------------+                 +-------------------+                     +-------------------+
    | Phase 3: Duplicate|                 | Phase 4: XGBoost  |                     | Phase 5: Isolation|
    | Detection Engine  |                 | Supervised Model  |                     | Forest / LOF      |
    +-------------------+                 +-------------------+                     +-------------------+
          |                                         |                                         |
          +-----------------------------------------+-----------------------------------------+
                                                    |
                                                    v
                                    +-------------------------------+
                                    | Phases 6 & 7: Knowledge Graph |
                                    | NetworkX Multi-Entity Network |
                                    +-------------------------------+
                                                    |
                                                    v
                                    +-------------------------------+
                                    | Phase 8: Hybrid Risk Engine   |
                                    | Calibrated Composite Scoring  |
                                    +-------------------------------+
                                                    |
                                                    v
                                    +-------------------------------+
                                    | Phase 9 & 10: Case Management |
                                    | & FastAPI Production Backend  |
                                    +-------------------------------+
                                                    |
                                                    v
                                    +===============================+
                                    | PHASE 11: STREAMLIT DASHBOARD |
                                    +===============================+
    ```
    """
)
