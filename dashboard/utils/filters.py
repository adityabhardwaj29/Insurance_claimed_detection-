"""
dashboard/utils/filters.py
--------------------------
Sidebar filters shared across dashboard pages.
Enables multi-dimensional filtering across risk band, amount, date,
provider, location, fraud probability, anomaly score, and investigation status.
"""

from __future__ import annotations

from typing import Tuple
import pandas as pd
import streamlit as st

from dashboard.utils.live_sync import render_live_sync_controller


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders standard sidebar filters and returns the filtered DataFrame.
    Includes real-time live sync controller for polling SQLite & FastAPI.
    """
    render_live_sync_controller(total_records=len(df))

    st.sidebar.markdown("### 🔍 Global Claim Filters")

    if df.empty:
        return df

    filtered_df = df.copy()

    # 1. Risk Band Filter
    available_bands = sorted(list(df["risk_band"].unique()))
    selected_bands = st.sidebar.multiselect(
        "Risk Band",
        options=available_bands,
        default=available_bands,
        help="Operational risk categories from Phase 8 risk engine",
    )
    if selected_bands:
        filtered_df = filtered_df[filtered_df["risk_band"].isin(selected_bands)]

    # 2. Claim Amount Range Slider
    min_amt = float(df["claim_amount"].min())
    max_amt = float(df["claim_amount"].max())
    selected_amount = st.sidebar.slider(
        "Claim Amount ($)",
        min_value=min_amt,
        max_value=max_amt,
        value=(min_amt, max_amt),
        step=500.0,
        format="$%.0f",
    )
    filtered_df = filtered_df[
        (filtered_df["claim_amount"] >= selected_amount[0])
        & (filtered_df["claim_amount"] <= selected_amount[1])
    ]

    # 3. Date Range Filter
    valid_dates = df["claim_date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        if min_date < max_date:
            date_range = st.sidebar.date_input(
                "Claim Filing Date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df["claim_date"].dt.date >= date_range[0])
                    & (filtered_df["claim_date"].dt.date <= date_range[1])
                ]

    # 4. Provider Filter
    providers = ["All Providers"] + sorted(
        [p for p in df["provider_name"].dropna().unique() if str(p).strip()]
    )
    selected_provider = st.sidebar.selectbox("Provider", options=providers)
    if selected_provider != "All Providers":
        filtered_df = filtered_df[filtered_df["provider_name"] == selected_provider]

    # 5. Location / City Filter
    cities = ["All Locations"] + sorted(
        [c for c in df["claimant_city"].dropna().unique() if str(c).strip()]
    )
    selected_city = st.sidebar.selectbox("Location (City)", options=cities)
    if selected_city != "All Locations":
        filtered_df = filtered_df[filtered_df["claimant_city"] == selected_city]

    # 6. Supervised Fraud Probability Slider
    min_fp = float(df["fraud_probability"].min())
    max_fp = float(df["fraud_probability"].max())
    selected_fp = st.sidebar.slider(
        "Min Fraud Probability (XGBoost)",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
    )
    filtered_df = filtered_df[filtered_df["fraud_probability"] >= selected_fp]

    # 7. Anomaly Score Slider
    selected_an = st.sidebar.slider(
        "Min Anomaly Score (Isolation Forest)",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
    )
    filtered_df = filtered_df[filtered_df["anomaly_score"] >= selected_an]

    # 8. Investigation Status Filter
    statuses = ["All Statuses"] + sorted(
        [s for s in df["case_status"].dropna().unique() if str(s).strip()]
    )
    selected_status = st.sidebar.selectbox("Investigation Case Status", options=statuses)
    if selected_status != "All Statuses":
        filtered_df = filtered_df[filtered_df["case_status"] == selected_status]

    st.sidebar.markdown(f"**Filtered Claims:** `{len(filtered_df)} / {len(df)}`")
    st.sidebar.markdown("---")

    return filtered_df
