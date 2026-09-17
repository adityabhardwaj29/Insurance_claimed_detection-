"""
dashboard/pages/investigation.py
--------------------------------
Full 360-Degree Claim Investigation Dossier & Case Management Interface.
Presents unified view of:
- Claim, Policy, Claimant, Vehicle, Provider, Invoice records
- Multi-signal risk decomposition radar/bar chart
- Explainable risk reasons
- Duplicate claim comparison & pairwise similarity
- Graph topological context (community, centrality, fraud neighbors)
- Interactive case triage: status updates, investigator assignments, notes, audit timeline
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.data_loader import (
    create_or_update_case,
    load_all_claims_data,
    load_claim_investigation_dossier,
)

st.set_page_config(page_title="Claim Investigation Dossier", layout="wide")

st.title("🔎 360° Claim Investigation Dossier")
st.markdown(
    "Unified evidence dossier for SIU (Special Investigation Unit) and claims fraud adjusters. "
    "Synthesizes relational entity data, multi-signal risk models, and case audit history."
)
st.caption(
    "Human-in-the-loop decision platform. Investigator actions are recorded in the immutable audit log."
)

claims_df = load_all_claims_data()
if claims_df.empty:
    st.warning("No claims data available. Ensure database/fraud_detection.db exists.")
    st.stop()

# ── 1. Claim Selector ────────────────────────────────────────────────────────
# Sort claims: high risk first
sorted_claims = claims_df.sort_values("final_risk_score", ascending=False)
claim_ids = sorted_claims["claim_id"].tolist()

# Support query params or session state for navigation from overview or cases
default_idx = 0
if "investigate_claim_id" in st.session_state and st.session_state["investigate_claim_id"] in claim_ids:
    default_idx = claim_ids.index(st.session_state["investigate_claim_id"])

col_search, col_stats = st.columns([2, 1])
with col_search:
    selected_cid = st.selectbox(
        "Select Claim ID to Investigate:",
        options=claim_ids,
        index=default_idx,
        format_func=lambda cid: (
            f"{cid} | Risk: {sorted_claims.loc[sorted_claims['claim_id'] == cid, 'final_risk_score'].values[0]:.4f} "
            f"| Band: {sorted_claims.loc[sorted_claims['claim_id'] == cid, 'risk_band'].values[0]} "
            f"| ${sorted_claims.loc[sorted_claims['claim_id'] == cid, 'claim_amount'].values[0]:,.0f}"
        ),
    )

# Load full dossier
dossier = load_claim_investigation_dossier(selected_cid)
if not dossier["found"]:
    st.error(f"Claim record '{selected_cid}' not found in database.")
    st.stop()

claim = dossier["claim"]
claimant = dossier["claimant"]
policy = dossier["policy"]
vehicle = dossier["vehicle"]
provider = dossier["provider"]
invoice = dossier["invoice"]
risk = dossier["risk_breakdown"]
dup = dossier["duplicate_info"]
graph_info = dossier["graph_info"]
case = dossier["case"]
notes = dossier["notes"]
events = dossier["events"]

# ── 2. Top Header Risk Banner ────────────────────────────────────────────────
final_score = risk.get("final_risk_score", 0.0)
risk_band = risk.get("risk_band", "LOW")

band_colors = {
    "CRITICAL": "#d90429",
    "HIGH": "#f77f00",
    "MEDIUM": "#fcbf49",
    "LOW": "#2a9d8f",
}
badge_color = band_colors.get(risk_band, "#2a9d8f")

st.markdown(
    f"""
    <div style="background-color: {badge_color}18; border-left: 6px solid {badge_color}; padding: 14px 20px; border-radius: 6px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 22px; font-weight: 700; color: #111;">Claim: {selected_cid}</span>
                <span style="margin-left: 14px; padding: 4px 12px; background: {badge_color}; color: white; border-radius: 12px; font-weight: 600; font-size: 13px;">
                    {risk_band} RISK ({final_score:.4f})
                </span>
                <span style="margin-left: 10px; font-size: 14px; color: #555;">
                    Claim Type: <b>{claim.get('claim_type', 'N/A')}</b> | Amount: <b>${claim.get('claim_amount', 0):,.2f}</b> | Date: <b>{str(claim.get('claim_date', ''))[:10]}</b>
                </span>
            </div>
            <div>
                <span style="font-size: 13px; color: #666;">Ground Truth Label:</span>
                <span style="font-weight: 700; color: {'#d90429' if claim.get('fraud_label') == 1 else '#2a9d8f'}; font-size: 14px;">
                    {'🚨 CONFIRMED FRAUD' if claim.get('fraud_label') == 1 else '✅ LEGITIMATE'}
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 3. Multi-Signal Risk Breakdown ───────────────────────────────────────────
st.subheader("📊 Multi-Signal Risk Decomposition")
col_gauge, col_reasons = st.columns([1, 1])

with col_gauge:
    signals = {
        "Supervised ML (XGBoost)": risk.get("fraud_probability", 0.0),
        "Unsupervised Anomaly (Isolation Forest)": risk.get("anomaly_score", 0.0),
        "Duplicate Similarity": risk.get("duplicate_score", 0.0),
        "Graph Topology Risk": risk.get("graph_risk_score", 0.0),
        "Final Composite Risk": risk.get("final_risk_score", 0.0),
    }

    fig_bar = go.Figure(
        go.Bar(
            x=list(signals.values()),
            y=list(signals.keys()),
            orientation="h",
            marker=dict(
                color=["#457b9d", "#6a4c93", "#e76f51", "#2a9d8f", badge_color],
            ),
            text=[f"{v:.4f}" for v in signals.values()],
            textposition="auto",
        )
    )
    fig_bar.update_layout(
        xaxis=dict(range=[0, 1.05], title="Score [0.0 - 1.0]"),
        height=260,
        margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_reasons:
    st.markdown("#### **Explainable Risk Reasons**")
    reasons = risk.get("risk_reasons", [])
    if reasons:
        for r in reasons:
            st.markdown(f"- ⚠️ **{r}**")
    else:
        st.success("No elevated risk indicators or fraud triggers detected for this claim.")

    # Graph context metrics
    st.markdown("#### **Graph Topological Context**")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.metric("Community ID", f"{graph_info.get('community_id', 'N/A')}")
    with gc2:
        st.metric("Fraud Neighbors", f"{graph_info.get('fraud_neighbor_count', 0)}")
    with gc3:
        st.metric("Degree Centrality", f"{graph_info.get('degree_centrality', 0.0):.4f}")

st.markdown("---")

# ── 4. Relational 360° Entity Profiles ──────────────────────────────────────
st.subheader("📑 Relational Entity Profiles")

tab_claim, tab_claimant, tab_policy, tab_vehicle, tab_provider, tab_invoice = st.tabs([
    "1. Claim Facts",
    "2. Claimant",
    "3. Policy",
    "4. Vehicle",
    "5. Provider",
    "6. Invoice Audit",
])

with tab_claim:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Claim ID:** `{claim.get('claim_id')}`")
        st.markdown(f"**Incident Date:** {str(claim.get('claim_date'))[:10]}")
        st.markdown(f"**Claim Amount:** ${claim.get('claim_amount', 0):,.2f}")
    with c2:
        st.markdown(f"**Claim Type:** {claim.get('claim_type')}")
        st.markdown(f"**Claim Status:** `{claim.get('status')}`")
        st.markdown(f"**Policy ID:** `{claim.get('policy_id')}`")
    with c3:
        st.markdown(f"**Provider ID:** `{claim.get('provider_id')}`")
        st.markdown(f"**Claimant ID:** `{claim.get('claimant_id')}`")
        st.markdown(f"**Vehicle ID:** `{claim.get('vehicle_id')}`")
    st.markdown(f"**Description:** *{claim.get('description', 'N/A')}*")

with tab_claimant:
    if claimant:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Claimant ID:** `{claimant.get('claimant_id')}`")
            st.markdown(f"**Name:** {claimant.get('name')}")
        with c2:
            st.markdown(f"**Age:** {claimant.get('age')}")
            st.markdown(f"**Gender:** {claimant.get('gender')}")
        with c3:
            st.markdown(f"**City:** {claimant.get('city')}")
            st.markdown(f"**Phone:** `{claimant.get('phone', 'N/A')}`")
    else:
        st.info("No claimant record attached.")

with tab_policy:
    if policy:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Policy ID:** `{policy.get('policy_id')}`")
            st.markdown(f"**Type:** {policy.get('policy_type')}")
        with c2:
            st.markdown(f"**Annual Premium:** ${policy.get('premium', 0):,.2f}")
            st.markdown(f"**Coverage Start:** {str(policy.get('start_date'))[:10]}")
        with c3:
            st.markdown(f"**Coverage End:** {str(policy.get('end_date'))[:10]}")
            st.markdown(f"**Date Order Invalid:** {'⚠️ YES' if policy.get('date_order_invalid') else '✅ Valid'}")
    else:
        st.info("No policy record attached.")

with tab_vehicle:
    if vehicle:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Vehicle ID:** `{vehicle.get('vehicle_id')}`")
            st.markdown(f"**Make:** {vehicle.get('make')}")
        with c2:
            st.markdown(f"**Model Year:** {vehicle.get('model_year')}")
            st.markdown(f"**Vehicle Type:** {vehicle.get('vehicle_type')}")
        with c3:
            st.markdown(f"**Registration No:** `{vehicle.get('registration_no')}`")
    else:
        st.info("No vehicle record attached.")

with tab_provider:
    if provider:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Provider ID:** `{provider.get('provider_id')}`")
            st.markdown(f"**Name:** {provider.get('provider_name')}")
        with c2:
            st.markdown(f"**Type:** {provider.get('provider_type')}")
            st.markdown(f"**City:** {provider.get('city')}")
        with c3:
            st.markdown(f"**Rating:** {provider.get('rating', 0):.1f} / 5.0")
    else:
        st.info("No provider record attached.")

with tab_invoice:
    if invoice:
        c1, c2, c3 = st.columns(3)
        inv_amt = float(invoice.get("invoice_amount", 0.0))
        clm_amt = float(claim.get("claim_amount", 0.0))
        discrepancy = abs(inv_amt - clm_amt)

        with c1:
            st.markdown(f"**Invoice ID:** `{invoice.get('invoice_id')}`")
            st.markdown(f"**Invoice Date:** {str(invoice.get('invoice_date'))[:10]}")
        with c2:
            st.markdown(f"**Invoice Amount:** ${inv_amt:,.2f}")
            st.markdown(f"**Claim Amount:** ${clm_amt:,.2f}")
        with c3:
            st.markdown(f"**Amount Match:** {'✅ MATCH' if discrepancy < 0.01 else f'⚠️ DISCREPANCY (${discrepancy:,.2f})'}")
    else:
        st.info("No invoice record attached.")

# ── 5. Duplicate Claim Comparison ────────────────────────────────────────────
if dup and dup.get("matched_claim_id") != "N/A":
    st.markdown("---")
    st.subheader("🔍 Duplicate Match Analysis")
    st.markdown(
        f"**Matched Pair:** `{selected_cid}` ↔ `{dup.get('matched_claim_id')}` | "
        f"**Similarity Score:** `{dup.get('duplicate_similarity_score', 0.0):.4f}` | "
        f"**Category:** `{dup.get('duplicate_type', 'N/A')}`"
    )

    # Fetch matched claim for side-by-side comparison
    match_row = claims_df[claims_df["claim_id"] == dup.get("matched_claim_id")]
    if not match_row.empty:
        m = match_row.iloc[0]
        comp_data = {
            "Attribute": ["Claim Amount", "Claim Type", "Claim Date", "Claimant ID", "Provider ID", "Final Risk Score", "Ground Truth Fraud"],
            f"Subject Claim ({selected_cid})": [
                f"${claim.get('claim_amount', 0):,.2f}",
                claim.get("claim_type", "N/A"),
                str(claim.get("claim_date", ""))[:10],
                claim.get("claimant_id", "N/A"),
                claim.get("provider_id", "N/A"),
                f"{final_score:.4f}",
                "Fraud" if claim.get("fraud_label") == 1 else "Legitimate",
            ],
            f"Matched Claim ({dup.get('matched_claim_id')})": [
                f"${m.get('claim_amount', 0):,.2f}",
                m.get("claim_type", "N/A"),
                str(m.get("claim_date", ""))[:10],
                m.get("claimant_id", "N/A"),
                m.get("provider_id", "N/A"),
                f"{m.get('final_risk_score', 0.0):.4f}",
                "Fraud" if m.get("fraud_label") == 1 else "Legitimate",
            ],
        }
        st.table(comp_data)

st.markdown("---")

# ── 6. Interactive Case Management Workflow ──────────────────────────────────
st.subheader("📋 SIU Case Management & Audit Trail")

col_case_info, col_case_action = st.columns([1, 1])

current_status = case.get("status", "NEW") if case else "UNASSIGNED"
current_priority = case.get("priority", "MEDIUM") if case else "MEDIUM"
current_assigned = case.get("assigned_to", "Unassigned") if case else "Unassigned"

with col_case_info:
    st.markdown("#### Active Case Details")
    if case:
        st.markdown(f"- **Case ID:** `{case.get('case_id')}`")
        st.markdown(f"- **Current Status:** `{current_status}`")
        st.markdown(f"- **Priority:** `{current_priority}`")
        st.markdown(f"- **Assigned Investigator:** **{current_assigned}**")
        st.markdown(f"- **Created At:** {case.get('created_at', 'N/A')}")
        st.markdown(f"- **Last Updated:** {case.get('updated_at', 'N/A')}")
    else:
        st.info("No active case exists for this claim yet. You can create one below.")

with col_case_action:
    st.markdown("#### Update Case & Record Note")
    with st.form(key=f"case_action_form_{selected_cid}"):
        status_options = ["NEW", "UNDER_REVIEW", "ESCALATED", "RESOLVED", "FALSE_POSITIVE"]
        status_idx = status_options.index(current_status) if current_status in status_options else 0
        new_status = st.selectbox("Status:", options=status_options, index=status_idx)

        priority_options = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        priority_idx = priority_options.index(current_priority) if current_priority in priority_options else 1
        new_priority = st.selectbox("Priority:", options=priority_options, index=priority_idx)

        investigators = ["Unassigned", "Sarah Chen (SIU Lead)", "David Miller (Investigator)", "Elena Rostova (Forensics)", "James Wilson (Adjuster)"]
        assign_idx = investigators.index(current_assigned) if current_assigned in investigators else 0
        new_assigned = st.selectbox("Assign Investigator:", options=investigators, index=assign_idx)

        actor_name = st.text_input("Your Name / Actor ID:", value="SIU_Investigator_1")
        new_note = st.text_area("Add Investigation Note / Evidence Summary:", placeholder="Enter findings, interview notes, or evidence summary...")

        submit = st.form_submit_button("💾 Save Changes & Record Audit Event")
        if submit:
            res = create_or_update_case(
                claim_id=selected_cid,
                status=new_status,
                priority=new_priority,
                assigned_to=new_assigned,
                actor=actor_name,
                note=new_note,
            )
            st.success(f"Case successfully updated! Case ID: `{res.get('case_id')}`")
            st.rerun()

# ── 7. Audit Trail Timeline ──────────────────────────────────────────────────
st.markdown("#### 📜 Chronological Case Audit Trail")
if events or notes:
    tab_events, tab_notes = st.tabs(["State Transitions & Events", "Investigator Notes"])
    with tab_events:
        if events:
            for ev in reversed(events):
                st.markdown(
                    f"⏱️ **{ev.get('timestamp', '')[:19]}** | "
                    f"**{ev.get('event_type')}** by `{ev.get('actor')}`: "
                    f"`{ev.get('old_value')}` ➔ `{ev.get('new_value')}` "
                    f"*(Details: {ev.get('details', '')})*"
                )
        else:
            st.info("No events logged.")

    with tab_notes:
        if notes:
            for n in reversed(notes):
                st.markdown(
                    f"📝 **{n.get('created_at', '')[:19]}** by **{n.get('author')}**:<br>"
                    f"> *{n.get('note_text')}*",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No investigator notes recorded.")
else:
    st.info("No past audit events or notes recorded for this claim.")
