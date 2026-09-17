"""
dashboard/pages/network.py
--------------------------
Interactive Knowledge Graph Visualizer.
Visualizes multi-entity relational networks:
Claim <-> Claimant <-> Policy <-> Vehicle <-> Provider <-> Location
with node inspection, edge relationship labels, and provider collusion subgraphs.
"""

from __future__ import annotations

import math
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.metrics import render_kpi_card
from dashboard.utils.data_loader import (
    build_claim_network_graph,
    load_all_claims_data,
    load_experiment_reports,
)

st.set_page_config(
    page_title="Network Analysis | Fraud Intelligence",
    page_icon="🕸️",
    layout="wide",
)

# Inject design tokens
inject_theme()

# Top Header Bar
render_header(
    title="Knowledge Graph & Collusion Hubs",
    subtitle="Explores the heterogeneous insurance network connecting Claims, Claimants, Policies, Vehicles, Providers, and Invoices to expose fraud syndicates.",
    tag="GRAPH TOPOLOGY & SYNDICATES",
    badge_text="NETWORKX SUBGRAPH",
)

claims_df = load_all_claims_data()
if claims_df.empty:
    st.error("Claims database not loaded. Ensure database/fraud_detection.db exists.")
    st.stop()

# ── 1. Graph Statistics Ribbon ───────────────────────────────────────────────
reports = load_experiment_reports()
g_stats = reports.get("graph_statistics", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        label="Total Graph Nodes",
        value=f"{g_stats.get('total_nodes', 1022):,}",
        subtitle="7 Heterogeneous entity tiers",
        icon="⚪",
        variant="default",
    )
with c2:
    render_kpi_card(
        label="Total Graph Edges",
        value=f"{g_stats.get('total_edges', 2617):,}",
        subtitle="10 Relational relationship types",
        icon="🔗",
        variant="default",
    )
with c3:
    render_kpi_card(
        label="Entity Tiers",
        value=f"{len(g_stats.get('node_types', {})) or 7}",
        subtitle="Ontological categories",
        icon="🏷️",
        variant="low",
    )
with c4:
    render_kpi_card(
        label="Graph Density",
        value=f"{g_stats.get('graph_overview', {}).get('density', 0.0050):.4f}",
        subtitle="Network sparsity ratio",
        icon="🌐",
        variant="high",
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ── 2. View Mode & Claim Selector ────────────────────────────────────────────
col_sel, col_mode = st.columns([3, 2])

sorted_claims = claims_df.sort_values("final_risk_score", ascending=False)
claim_options = sorted_claims["claim_id"].tolist()
claim_labels = {
    row["claim_id"]: f"{row['claim_id']} | Risk: {row['final_risk_score']:.2f} | ${row['claim_amount']:,.0f} | {'🚨 Fraud' if row['fraud_label'] == 1 else '✅ Legit'}"
    for _, row in sorted_claims.iterrows()
}

with col_sel:
    selected_claim_id = st.selectbox(
        "Select Claim to Visualize Ego-Network:",
        options=claim_options,
        index=0,
        format_func=lambda cid: claim_labels.get(cid, cid),
    )

with col_mode:
    view_mode = st.radio(
        "Graph Layout Algorithm:",
        options=["Spring Layout (Force-Directed)", "Circular Layout", "Kamada-Kawai Layout"],
        horizontal=True,
    )

# ── 3. Graph Construction ────────────────────────────────────────────────────
G, node_details = build_claim_network_graph(selected_claim_id)

if len(G.nodes) == 0:
    st.error(f"No graph structure found for Claim '{selected_claim_id}'.")
    st.stop()

# Compute coordinates based on chosen layout
if "Circular" in view_mode:
    pos = nx.circular_layout(G)
elif "Kamada" in view_mode:
    pos = nx.kamada_kawai_layout(G)
else:
    pos = nx.spring_layout(G, seed=42, k=1.2 / math.sqrt(max(1, len(G.nodes))))

# Enterprise Color Palette
ENTITY_COLORS = {
    "Claim": "#ef4444",          # Red
    "ConnectedClaim": "#f59e0b", # Amber
    "Claimant": "#3b82f6",       # Blue
    "Policy": "#10b981",         # Green
    "Vehicle": "#8b5cf6",        # Purple
    "Provider": "#f97316",       # Orange
    "Location": "#64748b",       # Slate
    "Invoice": "#06b6d4",        # Cyan
}

# ── 4. Build Interactive Plotly Graph ────────────────────────────────────────
edge_x = []
edge_y = []
edge_labels_x = []
edge_labels_y = []
edge_texts = []

for u, v, d in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_labels_x.append((x0 + x1) / 2)
    edge_labels_y.append((y0 + y1) / 2)
    edge_texts.append(d.get("relation", "CONNECTED"))

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=1.5, color="#334155"),
    hoverinfo="none",
    mode="lines",
    showlegend=False,
)

edge_label_trace = go.Scatter(
    x=edge_labels_x,
    y=edge_labels_y,
    mode="text",
    text=edge_texts,
    textposition="middle center",
    textfont=dict(size=9, color="#94a3b8"),
    hoverinfo="none",
    showlegend=False,
)

node_traces = []
for entity_type, color in ENTITY_COLORS.items():
    nx_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == entity_type]
    if not nx_nodes:
        continue

    nx_x = [pos[n][0] for n in nx_nodes]
    nx_y = [pos[n][1] for n in nx_nodes]
    nx_hover = []
    nx_labels = []

    for n in nx_nodes:
        details = node_details.get(n, {})
        hover_str = f"<b>{n}</b> ({entity_type})<br>"
        for k, v in details.items():
            hover_str += f"{k}: {v}<br>"
        nx_hover.append(hover_str)
        nx_labels.append(n)

    size = 28 if entity_type == "Claim" else 20

    trace = go.Scatter(
        x=nx_x,
        y=nx_y,
        mode="markers+text",
        text=nx_labels,
        textposition="top center",
        textfont=dict(size=10, color="#f8fafc", family="Inter, sans-serif"),
        hoverinfo="text",
        hovertext=nx_hover,
        marker=dict(
            size=size,
            color=color,
            line=dict(width=2, color="#0f172a"),
            opacity=0.95,
        ),
        name=entity_type,
    )
    node_traces.append(trace)

fig = go.Figure(
    data=[edge_trace, edge_label_trace, *node_traces],
    layout=go.Layout(
        title=dict(
            text=f"Ego Subgraph for Claim {selected_claim_id} ({len(G.nodes)} Nodes, {len(G.edges)} Edges)",
            font=dict(size=15, color="#f8fafc", family="Inter, sans-serif"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1120",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#f8fafc", size=11),
        ),
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=50),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=620,
    ),
)

# ── 5. Graph Render & Node Inspector ─────────────────────────────────────────
graph_col, detail_col = st.columns([3, 1])

with graph_col:
    st.plotly_chart(fig, use_container_width=True)

with detail_col:
    st.markdown(
        """
        <div class="saas-card-header">
            <h4 class="saas-card-title">🔍 Node Inspector</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    node_options = list(G.nodes)
    inspected_node = st.selectbox(
        "Select Node to Inspect:",
        options=node_options,
        index=0 if selected_claim_id in node_options else 0,
    )

    info = node_details.get(inspected_node, {})
    if info:
        st.markdown(f"**Entity Category:** `{info.get('Entity', 'Node')}`")
        for k, v in info.items():
            if k != "Entity":
                st.markdown(f"- **{k}:** {v}")

    # Connected Neighbors
    st.markdown("---")
    st.markdown("##### **Direct Relationships**")
    neighbors = list(G.neighbors(inspected_node))
    for neighbor in neighbors:
        edge_data = G.get_edge_data(inspected_node, neighbor) or {}
        relation = edge_data.get("relation", "CONNECTED_TO")
        st.markdown(f"- `{neighbor}` *(via {relation})*")

    st.markdown("---")
    st.caption(f"Local Subgraph Density: **{nx.density(G):.3f}**")

# ── 6. Provider Collusion & Multi-Claim Hubs ────────────────────────────────
st.markdown("---")
st.markdown("### 🏢 High-Throughput Provider Collusion Hubs")
st.caption("Repair providers handling multiple claims can indicate systematic billing inflation or collusion rings.")

provider_counts = claims_df.groupby(["provider_id", "provider_name", "provider_city", "provider_type"]).agg(
    total_claims=("claim_id", "count"),
    fraud_claims=("fraud_label", lambda s: int((s == 1).sum())),
    avg_risk_score=("final_risk_score", "mean"),
    total_billed=("claim_amount", "sum"),
).reset_index()

provider_counts["fraud_percentage"] = (provider_counts["fraud_claims"] / provider_counts["total_claims"]) * 100.0
multi_providers = provider_counts[provider_counts["total_claims"] > 1].sort_values("total_claims", ascending=False)

st.dataframe(
    multi_providers.style.format({
        "avg_risk_score": "{:.4f}",
        "total_billed": "${:,.2f}",
        "fraud_percentage": "{:.1f}%",
    }),
    use_container_width=True,
    height=320,
    hide_index=True,
)
