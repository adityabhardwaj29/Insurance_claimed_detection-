"""
dashboard/pages/claims.py
-------------------------
Claims Data Explorer.
Provides an interactive search, filter, and export interface
across all 320 claims enriched with risk scores and relational links.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.empty_states import render_empty_state
from dashboard.utils.data_loader import load_all_claims_data
from dashboard.utils.filters import render_sidebar_filters

st.set_page_config(
    page_title="Claims Explorer | Fraud Intelligence",
    page_icon="📑",
    layout="wide",
)

# Inject design tokens
inject_theme()

# Top Header Bar
render_header(
    title="Claims Explorer & Relational Browser",
    subtitle="Interactive search, multi-dimensional filtering, and data export across all 320 active claims.",
    tag="DATA EXPLORATION",
    badge_text="DATABASE BROWSER",
)

raw_df = load_all_claims_data()
if raw_df.empty:
    render_empty_state(
        title="No Claims Records",
        description="Database appears empty or database/fraud_detection.db is missing.",
        icon="📁",
    )
    st.stop()

# Sidebar filters
filtered_df = render_sidebar_filters(raw_df)

# Top Filter & Search Controls
search_col, sort_col, order_col = st.columns([3, 1, 1])

with search_col:
    search_term = st.text_input(
        "🔍 Search Claims (ID, Claimant, Provider, City, or Type):",
        placeholder="e.g. CLM00001, Accident, Mumbai, PRV013...",
    )

with sort_col:
    sort_field = st.selectbox(
        "Sort Field:",
        options=["final_risk_score", "claim_amount", "claim_date", "fraud_probability", "claim_id"],
        index=0,
    )

with order_col:
    ascending = st.selectbox(
        "Order Direction:",
        options=["Descending", "Ascending"],
        index=0,
    ) == "Ascending"

# Apply Search
if search_term.strip():
    t = search_term.lower()
    filtered_df = filtered_df[
        filtered_df["claim_id"].astype(str).str.lower().str.contains(t)
        | filtered_df["claimant_name"].astype(str).str.lower().str.contains(t)
        | filtered_df["provider_name"].astype(str).str.lower().str.contains(t)
        | filtered_df["claimant_city"].astype(str).str.lower().str.contains(t)
        | filtered_df["claim_type"].astype(str).str.lower().str.contains(t)
    ]

# Display Meta
st.markdown(
    f"<div style='margin-bottom: 12px; font-size: 0.88rem; color: var(--text-secondary);'>"
    f"Showing <strong>{len(filtered_df):,}</strong> of <strong>{len(raw_df):,}</strong> claims"
    f"</div>",
    unsafe_allow_html=True,
)

if filtered_df.empty:
    render_empty_state(
        title="No Matching Claims",
        description="Try relaxing your search terms or sidebar filters to see claims.",
        icon="🔍",
    )
    st.stop()

# Prepare table columns
cols_to_show = [
    "claim_id",
    "claim_date",
    "claim_amount",
    "claim_type",
    "risk_band",
    "final_risk_score",
    "fraud_probability",
    "anomaly_score",
    "claimant_name",
    "provider_name",
    "claimant_city",
    "case_status",
]
available_cols = [c for c in cols_to_show if c in filtered_df.columns]
display_df = filtered_df[available_cols].sort_values(sort_field, ascending=ascending)

# Formatted Data Table
st.dataframe(
    display_df.style.format({
        "claim_amount": "${:,.2f}",
        "final_risk_score": "{:.4f}",
        "fraud_probability": "{:.4f}",
        "anomaly_score": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
    height=540,
)

# Export Toolbar
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Filtered Claims (CSV)",
    data=csv_data,
    file_name="filtered_claims_export.csv",
    mime="text/csv",
)
