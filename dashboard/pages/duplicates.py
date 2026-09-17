"""
dashboard/pages/duplicates.py
-----------------------------
Duplicate Claim Analysis page.
Visualizes pairwise similarity scores, duplicate cluster types,
and side-by-side attribute matching from Phase 3.
"""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.metrics import render_kpi_card
from dashboard.components.charts import apply_chart_theme
from dashboard.components.empty_states import render_empty_state
from dashboard.utils.data_loader import load_all_claims_data, load_duplicate_records

st.set_page_config(
    page_title="Duplicate Claims | Fraud Intelligence",
    page_icon="📑",
    layout="wide",
)

# Inject design tokens
inject_theme()

# Top Header Bar
render_header(
    title="Duplicate & Similar Claim Analysis",
    subtitle="Detects opportunistic and organized duplicate claims using exact and fuzzy matching across invoice amounts, vehicle pairings, and descriptions.",
    tag="NLP & SIMILARITY ENGINE",
    badge_text="TF-IDF COSINE MATCHING",
)

dup_df = load_duplicate_records()
if dup_df.empty:
    render_empty_state(
        title="Duplicate Features Not Found",
        description="Verify that data/features/duplicate_features.csv exists or execute python run.py --pipeline.",
        icon="📑",
    )
    st.stop()

# ── 1. Summary KPIs ──────────────────────────────────────────────────────────
sim_col = "duplicate_similarity_score" if "duplicate_similarity_score" in dup_df.columns else "dup_similarity_score"
high_sim_count = int((dup_df[sim_col] >= 0.50).sum())
avg_sim = float(dup_df[sim_col].mean())
flagged_dups = int((dup_df.get("is_duplicate_flag", 0) == 1).sum())

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        label="Scanned Claims",
        value=f"{len(dup_df):,}",
        subtitle="Pairwise comparison matrix",
        icon="📁",
        variant="default",
    )
with c2:
    render_kpi_card(
        label="Elevated Match (≥0.50)",
        value=f"{high_sim_count:,}",
        subtitle="Suspected duplication",
        icon="⚠️",
        variant="high",
    )
with c3:
    render_kpi_card(
        label="Flagged Duplicates",
        value=f"{flagged_dups:,}",
        subtitle="Threshold triggers",
        icon="🚨",
        variant="critical",
    )
with c4:
    render_kpi_card(
        label="Mean Similarity",
        value=f"{avg_sim:.4f}",
        subtitle="Cosine score [0.0 - 1.0]",
        icon="📊",
        variant="low",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 2. Distribution Visualizations ───────────────────────────────────────────
st.markdown("### 📊 Similarity Distributions & Classification Types")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_sim = px.histogram(
        dup_df,
        x=sim_col,
        nbins=25,
        color_discrete_sequence=["#3b82f6"],
        labels={sim_col: "Pairwise Cosine Similarity Score"},
    )
    fig_sim.add_vline(
        x=0.50,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Elevated Risk (0.50)",
        annotation_font_color="#ef4444",
    )
    apply_chart_theme(
        fig_sim,
        height=360,
        title="Pairwise Duplicate Similarity Score Distribution",
    )
    st.plotly_chart(fig_sim, use_container_width=True)

with chart_col2:
    type_col = "duplicate_type" if "duplicate_type" in dup_df.columns else "dup_type"
    if type_col in dup_df.columns:
        counts = dup_df[type_col].value_counts().reset_index()
        counts.columns = ["Duplicate Category", "Count"]
        fig_pie = px.pie(
            counts,
            names="Duplicate Category",
            values="Count",
            hole=0.45,
            color_discrete_sequence=["#3b82f6", "#8b5cf6", "#f59e0b", "#10b981"],
        )
        apply_chart_theme(
            fig_pie,
            height=360,
            title="Distribution by Duplicate Classification Cluster",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 3. Side-by-Side Duplicate Inspector ─────────────────────────────────────
st.markdown("### 🔍 Side-by-Side Duplicate Inspector")

claims_all = load_all_claims_data()
top_dups = dup_df.sort_values(sim_col, ascending=False).head(50)

selected_cid = st.selectbox(
    "Select Claim to Inspect Duplication Signals (Top 50 Pairs):",
    options=top_dups["claim_id"].tolist(),
    format_func=lambda x: f"{x} — Cosine Similarity: {top_dups.loc[top_dups['claim_id'] == x, sim_col].values[0]:.4f}",
)

if selected_cid:
    target_row = top_dups[top_dups["claim_id"] == selected_cid].iloc[0]
    matched_id = str(target_row.get("matched_claim_id", "")).strip()

    st.markdown(
        f"""
        <div class="saas-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.1rem; font-weight: 700; color: var(--text-white);">
                    Subject Claim: {selected_cid} ↔ Matched Claim: {matched_id if matched_id else 'None'}
                </span>
                <span class="saas-badge {'critical' if target_row[sim_col] >= 0.50 else 'info'}">
                    Similarity: {target_row[sim_col]:.4f} ({target_row.get(type_col, 'N/A')})
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    target_details = claims_all[claims_all["claim_id"] == selected_cid]
    matched_details = claims_all[claims_all["claim_id"] == matched_id] if matched_id else None

    if not target_details.empty and matched_details is not None and not matched_details.empty:
        t = target_details.iloc[0]
        m = matched_details.iloc[0]

        comp_data = {
            "Entity Attribute": [
                "Claim Amount",
                "Claim Type",
                "Claim Incident Date",
                "Claimant Identifier",
                "Repair Provider Identifier",
                "Vehicle Identifier",
                "Composite Risk Score",
                "Ground Truth Fraud Status",
            ],
            f"Subject Claim ({selected_cid})": [
                f"${t.get('claim_amount', 0):,.2f}",
                t.get("claim_type", "N/A"),
                str(t.get("claim_date", ""))[:10],
                t.get("claimant_id", "N/A"),
                t.get("provider_id", "N/A"),
                t.get("vehicle_id", "N/A"),
                f"{t.get('final_risk_score', 0.0):.4f}",
                "Fraud" if t.get("fraud_label") == 1 else "Legitimate",
            ],
            f"Matched Pair ({matched_id})": [
                f"${m.get('claim_amount', 0):,.2f}",
                m.get("claim_type", "N/A"),
                str(m.get("claim_date", ""))[:10],
                m.get("claimant_id", "N/A"),
                m.get("provider_id", "N/A"),
                m.get("vehicle_id", "N/A"),
                f"{m.get('final_risk_score', 0.0):.4f}",
                "Fraud" if m.get("fraud_label") == 1 else "Legitimate",
            ],
        }
        st.table(comp_data)
    else:
        st.info("No matching claim paired with this record in the top threshold tier.")
