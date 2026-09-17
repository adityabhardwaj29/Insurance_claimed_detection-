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
from typing import Any, Dict, List

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.data_loader import (
    build_claim_network_graph,
    load_all_claims_data,
    load_experiment_reports,
)

st.set_page_config(page_title="Network Analysis | Fraud Graph", layout="wide")

st.title("🕸️ Graph Relationship & Network Analysis")
st.markdown(
    "Explores the heterogeneous insurance knowledge graph (Phase 6 & 7) linking "
    "**Claims**, **Claimants**, **Policies**, **Vehicles**, **Providers**, and **Locations**."
)
st.caption(
    "Topological signals (PageRank, Degree Centrality, Community IDs) reveal hidden "
    "syndicate structures and shared-entity collusion patterns."
)

claims_df = load_all_claims_data()
if claims_df.empty:
    st.warning("Claims database not loaded. Ensure database/fraud_detection.db exists.")
    st.stop()

# ── 1. Graph Statistics Bar ──────────────────────────────────────────────────
reports = load_experiment_reports()
g_stats = reports.get("graph_statistics", {})

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Graph Nodes", f"{g_stats.get('total_nodes', 1022):,}")
with c2:
    st.metric("Total Graph Edges", f"{g_stats.get('total_edges', 2617):,}")
with c3:
    st.metric("Entity Types", f"{len(g_stats.get('node_types', {})) or 6}")
with c4:
    st.metric("Detected Communities", f"{g_stats.get('num_communities', 34)}")

st.markdown("---")

# ── 2. View Mode & Claim Selector ────────────────────────────────────────────
col_sel, col_mode = st.columns([2, 1])

# Order claims by risk score descending for easy investigation
sorted_claims = claims_df.sort_values("final_risk_score", ascending=False)
claim_options = sorted_claims["claim_id"].tolist()
claim_labels = {
    row["claim_id"]: f"{row['claim_id']} | Risk: {row['final_risk_score']:.2f} | ${row['claim_amount']:,.0f} | {'🚨 Fraud' if row['fraud_label'] == 1 else '✅ Legitimate'}"
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

# Define Entity Color Palette
ENTITY_COLORS = {
    "Claim": "#d90429",          # Red / Crimson
    "ConnectedClaim": "#f77f00", # Amber
    "Claimant": "#3a86ff",       # Blue
    "Policy": "#2a9d8f",         # Teal
    "Vehicle": "#8338ec",        # Purple
    "Provider": "#ffb703",       # Gold
    "Location": "#6c757d",       # Gray
}

# ── 4. Build Interactive Plotly Graph ────────────────────────────────────────
# Edge Traces
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
    line=dict(width=1.5, color="#ced4da"),
    hoverinfo="none",
    mode="lines",
    showlegend=False,
)

# Edge text middle trace
edge_label_trace = go.Scatter(
    x=edge_labels_x,
    y=edge_labels_y,
    mode="text",
    text=edge_texts,
    textposition="middle center",
    textfont=dict(size=9, color="#6c757d"),
    hoverinfo="none",
    showlegend=False,
)

# Node Traces by Entity Type for Legend Support
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
        # Short label
        nx_labels.append(n)

    size = 28 if entity_type == "Claim" else 22

    trace = go.Scatter(
        x=nx_x,
        y=nx_y,
        mode="markers+text",
        text=nx_labels,
        textposition="top center",
        textfont=dict(size=10, color="#212529"),
        hoverinfo="text",
        hovertext=nx_hover,
        marker=dict(
            size=size,
            color=color,
            line=dict(width=2, color="#ffffff"),
            opacity=0.95,
        ),
        name=entity_type,
    )
    node_traces.append(trace)

fig = go.Figure(
    data=[edge_trace, edge_label_trace, *node_traces],
    layout=go.Layout(
        title=f"Knowledge Subgraph for Claim: {selected_claim_id} ({len(G.nodes)} Nodes, {len(G.edges)} Edges)",
        titlefont=dict(size=16),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=50),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#f8f9fa",
        height=620,
    ),
)

# ── 5. Render Layout: Graph (Left) and Node Details (Right) ──────────────────
graph_col, detail_col = st.columns([3, 1])

with graph_col:
    st.plotly_chart(fig, use_container_width=True)

with detail_col:
    st.subheader("🔍 Node Inspector")
    st.caption("Inspect attributes of any node in this subgraph:")

    node_options = list(G.nodes)
    inspected_node = st.selectbox(
        "Select Node:",
        options=node_options,
        index=0 if selected_claim_id in node_options else 0,
    )

    info = node_details.get(inspected_node, {})
    if info:
        st.markdown(f"### **{info.get('Entity', 'Node')}**")
        for k, v in info.items():
            st.markdown(f"**{k}:** {v}")

    # Connected Neighbors
    st.markdown("---")
    st.markdown("#### Connected Neighbors")
    neighbors = list(G.neighbors(inspected_node))
    for neighbor in neighbors:
        edge_data = G.get_edge_data(inspected_node, neighbor) or {}
        relation = edge_data.get("relation", "CONNECTED_TO")
        st.markdown(f"- `{neighbor}` *(via {relation})*")

    st.markdown("---")
    st.info(f"💡 Subgraph Density: **{nx.density(G):.3f}**")

# ── 6. Provider Collusion & Multi-Claim Hubs ────────────────────────────────
st.markdown("---")
st.subheader("🏢 Provider Hubs with Multiple Claims")
st.markdown(
    "Providers connected to multiple claims indicate potential repair shop rings "
    "or billing collusion hot-spots."
)

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
    }).background_gradient(subset=["avg_risk_score"], cmap="YlOrRd"),
    use_container_width=True,
    height=300,
)
