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

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import plotly.graph_objects as go
import streamlit as st

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.badges import risk_badge, status_badge
from dashboard.components.charts import apply_chart_theme
from dashboard.utils.data_loader import (
    create_or_update_case,
    load_all_claims_data,
    load_claim_investigation_dossier,
    load_claim_explanation,
)

st.set_page_config(
    page_title="Investigation Dossier | Fraud Intelligence",
    page_icon="🔎",
    layout="wide",
)

# Inject design tokens
inject_theme()

# Top Header Bar
render_header(
    title="360° Forensic Claim Dossier",
    subtitle="Unified investigative workspace synthesizing relational contracts, multi-signal predictive scores, SHAP attributions, and audited case lifecycle.",
    tag="SIU INVESTIGATION WORKSPACE",
    badge_text="FORENSIC AUDIT",
)

claims_df = load_all_claims_data()
if claims_df.empty:
    st.error("No claims data available. Ensure database/fraud_detection.db exists.")
    st.stop()

# ── 1. Claim Selector ────────────────────────────────────────────────────────
sorted_claims = claims_df.sort_values("final_risk_score", ascending=False)
claim_ids = sorted_claims["claim_id"].tolist()

default_idx = 0
if "investigate_claim_id" in st.session_state and st.session_state["investigate_claim_id"] in claim_ids:
    default_idx = claim_ids.index(st.session_state["investigate_claim_id"])

col_sel, col_quick_kpi = st.columns([3, 2])
with col_sel:
    selected_cid = st.selectbox(
        "Select Claim ID to Investigate (Ranked by Risk):",
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

final_score = risk.get("final_risk_score", 0.0)
risk_band_val = risk.get("risk_band", "LOW")

with col_quick_kpi:
    st.markdown(
        f"""
        <div style="display: flex; gap: 12px; align-items: center; justify-content: flex-end; padding-top: 24px;">
            {risk_badge(risk_band_val)}
            <span class="saas-badge neutral">Status: {claim.get('status', 'Open')}</span>
            <span class="saas-badge {'critical' if claim.get('fraud_label') == 1 else 'low'}">
                {'🚨 Confirmed Fraud' if claim.get('fraud_label') == 1 else '✅ Legitimate'}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ── 2. Top Summary Banner ────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="saas-card" style="border-left: 4px solid var(--risk-{risk_band_val.lower()}); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <span style="font-size: 1.4rem; font-weight: 700; color: var(--text-white);">
                    Claim ID: {selected_cid}
                </span>
                <span style="margin-left: 12px; font-size: 0.92rem; color: var(--text-secondary);">
                    Type: <strong style="color: var(--text-primary);">{claim.get('claim_type', 'N/A')}</strong> |
                    Amount: <strong style="color: var(--text-primary);">${claim.get('claim_amount', 0):,.2f}</strong> |
                    Date: <strong style="color: var(--text-primary);">{str(claim.get('claim_date', ''))[:10]}</strong>
                </span>
            </div>
            <div>
                <span style="font-size: 0.85rem; color: var(--text-muted);">Composite Risk Score:</span>
                <span style="font-size: 1.25rem; font-weight: 800; color: var(--text-white); margin-left: 6px;">
                    {final_score:.4f}
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 3. Multi-Signal Risk Breakdown & Explainable Reasons ─────────────────────
st.markdown("### 📊 Multi-Signal Risk Decomposition & Rule Triggers")

col_gauge, col_reasons = st.columns([1, 1])

with col_gauge:
    signals = {
        "Supervised ML (XGBoost)": risk.get("fraud_probability", 0.0),
        "Anomaly (Isolation Forest)": risk.get("anomaly_score", 0.0),
        "Duplicate Similarity": risk.get("duplicate_score", 0.0),
        "Graph Topology Risk": risk.get("graph_risk_score", 0.0),
        "Final Hybrid Score": risk.get("final_risk_score", 0.0),
    }

    colors_map = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f59e0b",
        "MEDIUM": "#eab308",
        "LOW": "#10b981",
    }
    bar_color = colors_map.get(risk_band_val, "#3b82f6")

    fig_bar = go.Figure(
        go.Bar(
            x=list(signals.values()),
            y=list(signals.keys()),
            orientation="h",
            marker=dict(
                color=["#3b82f6", "#8b5cf6", "#f97316", "#06b6d4", bar_color],
            ),
            text=[f"{v:.4f}" for v in signals.values()],
            textposition="auto",
        )
    )
    apply_chart_theme(
        fig_bar,
        height=280,
        title="Multi-Signal Calibration (0.0 to 1.0)",
    )
    fig_bar.update_layout(xaxis=dict(range=[0, 1.05]))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_reasons:
    st.markdown("#### **Codified Reason Triggers**")
    reasons = risk.get("risk_reasons", [])
    if reasons:
        for r in reasons:
            st.markdown(f"- ⚠️ <span style='font-size: 0.88rem; color: var(--text-primary);'>{r}</span>", unsafe_allow_html=True)
    else:
        st.success("No elevated risk indicators or fraud triggers detected for this claim.")

    st.markdown("#### **Graph Topological Properties**")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.metric("Community ID", f"{graph_info.get('community_id', 'N/A')}")
    with gc2:
        st.metric("Fraud Neighbors", f"{graph_info.get('fraud_neighbor_count', 0)}")
    with gc3:
        st.metric("Degree Centrality", f"{graph_info.get('degree_centrality', 0.0):.4f}")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 4. Explainable AI: SHAP Waterfall & Graph Evidence ───────────────────────
st.markdown("### 🧠 Explainable AI: Local SHAP Factors & Graph Evidence")

exp_data = load_claim_explanation(selected_cid)
if exp_data.get("summary_text"):
    st.markdown(
        f"""
        <div class="saas-callout">
            <div class="saas-callout-text">
                <strong>Investigator Evidence Synthesis:</strong> {exp_data['summary_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

tab_shap, tab_graph_ev = st.tabs(["1. Supervised ML SHAP Factor Impact", "2. Knowledge Graph Topological Evidence"])

with tab_shap:
    c_sh1, c_sh2 = st.columns([1, 1])
    top_factors = exp_data.get("top_factors", [])
    if top_factors:
        f_names = [f["feature"] for f in reversed(top_factors)]
        f_impacts = [f["impact"] for f in reversed(top_factors)]
        f_colors = ["#ef4444" if f["direction"] == "risk_increasing" else "#10b981" for f in reversed(top_factors)]

        fig_shap = go.Figure(
            go.Bar(
                x=f_impacts,
                y=f_names,
                orientation="h",
                marker=dict(color=f_colors),
                text=[f"{val:+.4f}" for val in f_impacts],
                textposition="auto",
            )
        )
        apply_chart_theme(
            fig_shap,
            height=300,
            title="Local SHAP Feature Attributions (Red = Increases Risk, Green = Mitigating)",
        )
        fig_shap.update_layout(xaxis=dict(title="Marginal Shapley Contribution"))
        with c_sh1:
            st.plotly_chart(fig_shap, use_container_width=True)

    with c_sh2:
        st.markdown("##### 🚨 **Top Risk-Increasing Factors**")
        pos_f = exp_data.get("top_positive_factors", [])
        if pos_f:
            for pf in pos_f:
                st.markdown(f"- **{pf['feature']}**: `+{pf['impact']:.4f}`")
        else:
            st.caption("No significant risk-increasing factors.")

        st.markdown("##### 🛡️ **Top Risk-Mitigating Factors**")
        neg_f = exp_data.get("top_negative_factors", [])
        if neg_f:
            for nf in neg_f:
                st.markdown(f"- **{nf['feature']}**: `{nf['impact']:.4f}`")
        else:
            st.caption("No significant mitigating factors.")

with tab_graph_ev:
    g_exp = exp_data.get("graph_explanation", {})
    gev1, gev2 = st.columns(2)
    with gev1:
        st.markdown("##### 🚨 **Suspicious Topological Connections**")
        sc = g_exp.get("suspicious_connections", [])
        if sc:
            for s in sc:
                st.markdown(f"- **{s.get('type')}**: {s.get('description')}")
        else:
            st.success("No suspicious topological connections detected.")

        st.markdown("##### 🌐 **High-Degree Entity Hubs**")
        hde = g_exp.get("high_degree_entities", [])
        if hde:
            for h in hde:
                st.markdown(f"- **{h.get('entity_type')}** (`{h.get('entity_id')}`): {h.get('description')}")
        else:
            st.info("No unusual high-degree entity hubs in ego-network.")

    with gev2:
        st.markdown("##### 🔁 **Repeated Interactions**")
        rr = g_exp.get("repeated_relationships", [])
        if rr:
            for r in rr:
                st.markdown(f"- **{r.get('relationship_type')}**: {r.get('description')}")
        else:
            st.success("No repeated claimant-provider or vehicle pairings.")

        st.markdown("##### ⚠️ **Flagged Ego-Network Neighbors**")
        nfc = g_exp.get("neighboring_flagged_claims", [])
        if nfc:
            for n in nfc:
                st.markdown(f"- 🚩 **{n.get('claim_id')}** (${n.get('claim_amount', 0):,.2f}): {n.get('description')}")
        else:
            st.success("No confirmed fraud or high-risk claims in immediate ego-network.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 5. Relational 360° Entity Profiles ──────────────────────────────────────
st.markdown("### 📑 Relational Entity Profiles (SQLite 3NF)")

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
        st.markdown(f"**Status:** `{claim.get('status')}`")
        st.markdown(f"**Policy ID:** `{claim.get('policy_id')}`")
    with c3:
        st.markdown(f"**Provider ID:** `{claim.get('provider_id')}`")
        st.markdown(f"**Claimant ID:** `{claim.get('claimant_id')}`")
        st.markdown(f"**Vehicle ID:** `{claim.get('vehicle_id')}`")
    st.markdown(f"**Incident Narrative:** *{claim.get('description', 'N/A')}*")

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
            st.markdown(f"**Marital Status:** {claimant.get('marital_status', 'N/A')}")
    else:
        st.info("No claimant record attached.")

with tab_policy:
    if policy:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Policy ID:** `{policy.get('policy_id')}`")
            st.markdown(f"**Policy Type:** {policy.get('policy_type')}")
        with c2:
            st.markdown(f"**Annual Premium:** ${policy.get('premium', 0):,.2f}")
            st.markdown(f"**Coverage Inception:** {str(policy.get('start_date'))[:10]}")
        with c3:
            st.markdown(f"**Coverage Expiry:** {str(policy.get('end_date'))[:10]}")
            st.markdown(f"**Date Order Integrity:** {'⚠️ Flagged' if policy.get('date_order_invalid') else '✅ Valid'}")
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
            st.markdown(f"**Body Style:** {vehicle.get('vehicle_type')}")
        with c3:
            st.markdown(f"**Vehicle Age:** {2026 - int(vehicle.get('model_year', 2020))} years")
    else:
        st.info("No vehicle record attached.")

with tab_provider:
    if provider:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Provider ID:** `{provider.get('provider_id')}`")
            st.markdown(f"**Facility Name:** {provider.get('provider_name')}")
        with c2:
            st.markdown(f"**Facility Type:** {provider.get('provider_type')}")
            st.markdown(f"**Operating City:** {provider.get('city')}")
        with c3:
            st.markdown(f"**Quality Rating:** {provider.get('rating', 0):.1f} / 5.0")
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

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 6. Duplicate Match Analysis ──────────────────────────────────────────────
if dup and dup.get("matched_claim_id") != "N/A":
    st.markdown("### 🔍 Duplicate Claim Pair Comparison")
    st.markdown(
        f"**Matched Pair:** `{selected_cid}` ↔ `{dup.get('matched_claim_id')}` | "
        f"**Similarity Score:** `{dup.get('duplicate_similarity_score', 0.0):.4f}` | "
        f"**Classification:** `{dup.get('duplicate_type', 'N/A')}`"
    )

    match_row = claims_df[claims_df["claim_id"] == dup.get("matched_claim_id")]
    if not match_row.empty:
        m = match_row.iloc[0]
        comp_data = {
            "Attribute": ["Claim Amount", "Claim Type", "Claim Date", "Claimant ID", "Provider ID", "Final Risk Score", "Ground Truth Label"],
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

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ── 7. Interactive Case Management Workflow ──────────────────────────────────
st.markdown("### 📋 SIU Case Management & Audit Actions")

col_case_info, col_case_action = st.columns([1, 1])

current_status = case.get("status", "NEW") if case else "UNASSIGNED"
current_priority = case.get("priority", "MEDIUM") if case else "MEDIUM"
current_assigned = case.get("assigned_to", "Unassigned") if case else "Unassigned"

with col_case_info:
    st.markdown(
        f"""
        <div class="saas-card">
            <h4 class="saas-card-title">Case Metadata</h4>
            <div style="margin-top: 12px; line-height: 1.8; font-size: 0.88rem;">
                <div>Case ID: <strong>{case.get('case_id', 'N/A')}</strong></div>
                <div>Status: {status_badge(current_status)}</div>
                <div>Priority: <strong>{current_priority}</strong></div>
                <div>Investigator: <strong>{current_assigned}</strong></div>
                <div>Created: {case.get('created_at', 'N/A')}</div>
                <div>Last Updated: {case.get('updated_at', 'N/A')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_case_action:
    st.markdown("#### Update Case & Record Note")
    with st.form(key=f"case_action_form_{selected_cid}"):
        status_options = ["NEW", "UNDER_REVIEW", "ESCALATED", "RESOLVED", "FALSE_POSITIVE"]
        status_idx = status_options.index(current_status) if current_status in status_options else 0
        new_status = st.selectbox("Status Transition:", options=status_options, index=status_idx)

        priority_options = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        priority_idx = priority_options.index(current_priority) if current_priority in priority_options else 1
        new_priority = st.selectbox("Triage Priority:", options=priority_options, index=priority_idx)

        investigators = [
            "Unassigned",
            "Sarah Chen (SIU Lead)",
            "David Miller (Investigator)",
            "Elena Rostova (Forensics)",
            "James Wilson (Adjuster)",
        ]
        assign_idx = investigators.index(current_assigned) if current_assigned in investigators else 0
        new_assigned = st.selectbox("Assign Investigator:", options=investigators, index=assign_idx)

        actor_name = st.text_input("Your Name / Actor ID:", value="SIU_Investigator_1")
        new_note = st.text_area("Add Investigation Note / Evidence Summary:", placeholder="Record interview notes, forensic findings, or rationale...")

        submit = st.form_submit_button("💾 Save Changes & Record Audit Event", type="primary")
        if submit:
            res = create_or_update_case(
                claim_id=selected_cid,
                status=new_status,
                priority=new_priority,
                assigned_to=new_assigned,
                actor=actor_name,
                note=new_note,
            )
            st.success(f"Case successfully updated! Case ID: {res.get('case_id')}")
            st.rerun()

# ── 8. Audit Trail Timeline ──────────────────────────────────────────────────
st.markdown("#### 📜 Chronological Case Audit Trail")
if events or notes:
    tab_events, tab_notes = st.tabs(["Lifecycle Events", "Investigator Notes"])
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
