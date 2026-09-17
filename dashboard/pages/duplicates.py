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

from dashboard.utils.data_loader import load_all_claims_data, load_duplicate_records

st.set_page_config(page_title="Duplicate Claim Analysis", layout="wide")

st.title("📑 Duplicate & Similar Claim Analysis")
st.markdown(
    "Detects opportunistic and organized duplicate claims using exact and fuzzy matching "
    "across invoice amounts, claimant histories, vehicles, and provider locations."
)

dup_df = load_duplicate_records()
if dup_df.empty:
    st.warning("Duplicate features file not found. Please verify data/features/duplicate_features.csv exists.")
    st.stop()

# ── 1. Summary Metrics ───────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
sim_col = "duplicate_similarity_score" if "duplicate_similarity_score" in dup_df.columns else "dup_similarity_score"
high_sim_count = int((dup_df[sim_col] >= 0.50).sum())
avg_sim = float(dup_df[sim_col].mean())
flagged_dups = int((dup_df.get("is_duplicate_flag", 0) == 1).sum())
clusters_count = len(dup_df["duplicate_type"].unique()) if "duplicate_type" in dup_df.columns else 3

with col1:
    st.metric("Total Scanned Claims", f"{len(dup_df):,}")
with col2:
    st.metric("Elevated Similarity (≥0.50)", f"{high_sim_count:,}")
with col3:
    st.metric("Flagged Duplicates", f"{flagged_dups:,}")
with col4:
    st.metric("Mean Similarity Score", f"{avg_sim:.4f}")

st.markdown("---")

# ── 2. Charts Row ────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Similarity Score Distribution")
    fig_sim = px.histogram(
        dup_df,
        x=sim_col,
        nbins=25,
        color_discrete_sequence=["#3a86ff"],
        title="Pairwise Duplicate Similarity Distribution (Min: 0.33, Max: 0.63)",
        labels={sim_col: "Pairwise Similarity Score"},
    )
    fig_sim.add_vline(x=0.50, line_dash="dash", line_color="red", annotation_text="Elevated Risk Threshold (0.50)")
    st.plotly_chart(fig_sim, use_container_width=True)

with c2:
    st.subheader("Duplicate Detection Clusters")
    type_col = "duplicate_type" if "duplicate_type" in dup_df.columns else "dup_type"
    if type_col in dup_df.columns:
        counts = dup_df[type_col].value_counts().reset_index()
        counts.columns = ["Duplicate Category", "Count"]
        fig_pie = px.pie(
            counts,
            names="Duplicate Category",
            values="Count",
            title="Distribution by Duplicate Classification Type",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ── 3. Pairwise Comparison Inspector ─────────────────────────────────────────
st.subheader("🔍 Side-by-Side Duplicate Inspector")
claims_all = load_all_claims_data()

top_dups = dup_df.sort_values(sim_col, ascending=False).head(50)
selected_cid = st.selectbox(
    "Select Claim to Inspect Duplication Signals",
    options=top_dups["claim_id"].tolist(),
    format_func=lambda x: f"{x} — Similarity: {top_dups.loc[top_dups['claim_id'] == x, sim_col].values[0]:.4f}",
)

if selected_cid:
    target_row = top_dups[top_dups["claim_id"] == selected_cid].iloc[0]
    matched_id = str(target_row.get("matched_claim_id", "")).strip()

    st.markdown(f"### Claim: `{selected_cid}` (Similarity: `{target_row[sim_col]:.4f}`)")
    st.write(f"**Classification:** `{target_row.get(type_col, 'N/A')}`")

    target_details = claims_all[claims_all["claim_id"] == selected_cid]
    matched_details = claims_all[claims_all["claim_id"] == matched_id] if matched_id else pd.DataFrame()

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown(f"#### Primary Claim: `{selected_cid}`")
        if not target_details.empty:
            t = target_details.iloc[0]
            st.json({
                "Claim ID": t["claim_id"],
                "Amount": f"${t['claim_amount']:,.2f}",
                "Claim Type": t["claim_type"],
                "Claim Date": str(t["claim_date"].date()) if pd.notna(t["claim_date"]) else "N/A",
                "Claimant": f"{t['claimant_name']} ({t['claimant_id']})",
                "City": t["claimant_city"],
                "Provider": f"{t['provider_name']} ({t['provider_id']})",
                "Vehicle": f"{t['vehicle_make']} ({t['vehicle_type']})",
            })

    with c_right:
        st.markdown(f"#### Matched Candidate: `{matched_id if matched_id else 'None'}`")
        if not matched_details.empty:
            m = matched_details.iloc[0]
            st.json({
                "Claim ID": m["claim_id"],
                "Amount": f"${m['claim_amount']:,.2f}",
                "Claim Type": m["claim_type"],
                "Claim Date": str(m["claim_date"].date()) if pd.notna(m["claim_date"]) else "N/A",
                "Claimant": f"{m['claimant_name']} ({m['claimant_id']})",
                "City": m["claimant_city"],
                "Provider": f"{m['provider_name']} ({m['provider_id']})",
                "Vehicle": f"{m['vehicle_make']} ({m['vehicle_type']})",
            })
        else:
            st.info("No single 1-to-1 matched claim pair; similarity score is derived from multi-attribute centroid matching.")
