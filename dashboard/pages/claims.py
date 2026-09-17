"""
dashboard/pages/claims.py
-------------------------
Claims Data Explorer.
Provides an interactive search, filter, and export interface
across all 320 claims enriched with risk scores and relational links.
"""

from __future__ import annotations

import streamlit as st

from dashboard.utils.data_loader import load_all_claims_data
from dashboard.utils.filters import render_sidebar_filters

st.set_page_config(page_title="Claims Explorer | Fraud Analytics", layout="wide")

st.title("📑 Claims Explorer & Data Browser")
st.markdown("Search, inspect, and export all 320 claims across relational entities and risk dimensions.")

raw_df = load_all_claims_data()
if raw_df.empty:
    st.warning("No claims data available. Ensure database/fraud_detection.db exists.")
    st.stop()

# Sidebar filters
filtered_df = render_sidebar_filters(raw_df)

# Search bar
search_term = st.text_input("🔍 Search Claims (Claim ID, Claimant Name, Provider Name, City, or Type):", "")

if search_term.strip():
    t = search_term.lower()
    filtered_df = filtered_df[
        filtered_df["claim_id"].astype(str).str.lower().str.contains(t)
        | filtered_df["claimant_name"].astype(str).str.lower().str.contains(t)
        | filtered_df["provider_name"].astype(str).str.lower().str.contains(t)
        | filtered_df["claimant_city"].astype(str).str.lower().str.contains(t)
        | filtered_df["claim_type"].astype(str).str.lower().str.contains(t)
    ]

st.markdown(f"**Showing {len(filtered_df)} of {len(raw_df)} claims**")

# Display columns
cols_to_show = [
    "claim_id",
    "claim_date",
    "claim_amount",
    "claim_type",
    "claim_status",
    "risk_band",
    "final_risk_score",
    "fraud_probability",
    "claimant_name",
    "provider_name",
    "case_status",
]

available = [c for c in cols_to_show if c in filtered_df.columns]
display_df = filtered_df[available].copy()

# Sort
sort_col = st.selectbox("Sort By:", options=["final_risk_score", "claim_amount", "claim_date", "claim_id"], index=0)
ascending = st.checkbox("Ascending order", value=False)
display_df = display_df.sort_values(sort_col, ascending=ascending)

st.dataframe(
    display_df.style.format({
        "claim_amount": "${:,.2f}",
        "final_risk_score": "{:.4f}",
        "fraud_probability": "{:.4f}",
    }).background_gradient(subset=["final_risk_score"], cmap="YlOrRd"),
    use_container_width=True,
    height=500,
)

# Export button
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Filtered Claims to CSV",
    data=csv_data,
    file_name="filtered_claims_export.csv",
    mime="text/csv",
)
