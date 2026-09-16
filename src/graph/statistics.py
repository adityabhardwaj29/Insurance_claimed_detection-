"""
Insurance Claim Graph Statistics Module.
Computes comprehensive structural metrics, degree distributions,
connected components, and entity/relationship breakdowns.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import networkx as nx


def compute_graph_statistics(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    G: Optional[nx.Graph] = None,
) -> Dict[str, Any]:
    """
    Computes rigorous topological and semantic statistics for the insurance graph.
    """
    if G is None:
        G = nx.Graph()
        for _, r in nodes_df.iterrows():
            G.add_node(r["node_id"], node_type=r["node_type"])
        for _, r in edges_df.iterrows():
            G.add_edge(r["source"], r["target"], relationship=r["relationship"], weight=float(r["weight"]))

    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()

    # 1. Node type breakdown
    nodes_by_type = nodes_df["node_type"].value_counts().to_dict()

    # 2. Relationship breakdown
    edges_by_rel = edges_df["relationship"].value_counts().to_dict()

    # 3. Degrees and Degree Distribution
    degrees = dict(G.degree())
    deg_values = list(degrees.values())
    
    deg_array = np.array(deg_values)
    mean_deg = float(np.mean(deg_array)) if len(deg_array) > 0 else 0.0
    median_deg = float(np.median(deg_array)) if len(deg_array) > 0 else 0.0
    std_deg = float(np.std(deg_array)) if len(deg_array) > 0 else 0.0
    min_deg = int(np.min(deg_array)) if len(deg_array) > 0 else 0
    max_deg = int(np.max(deg_array)) if len(deg_array) > 0 else 0
    p25_deg = float(np.percentile(deg_array, 25)) if len(deg_array) > 0 else 0.0
    p75_deg = float(np.percentile(deg_array, 75)) if len(deg_array) > 0 else 0.0

    # Top degree nodes
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    node_type_map = dict(zip(nodes_df["node_id"], nodes_df["node_type"]))
    top_degree_nodes = [
        {
            "node_id": node,
            "node_type": node_type_map.get(node, "Unknown"),
            "degree": deg,
        }
        for node, deg in sorted_nodes[:15]
    ]

    # Degree statistics by entity type
    degrees_by_type = {}
    for ntype in nodes_by_type.keys():
        type_nodes = nodes_df[nodes_df["node_type"] == ntype]["node_id"]
        type_degs = [degrees.get(nid, 0) for nid in type_nodes]
        if type_degs:
            degrees_by_type[ntype] = {
                "count": len(type_degs),
                "mean_degree": round(float(np.mean(type_degs)), 2),
                "median_degree": round(float(np.median(type_degs)), 2),
                "min_degree": int(np.min(type_degs)),
                "max_degree": int(np.max(type_degs)),
            }

    # 4. Connected Components
    components = list(nx.connected_components(G))
    comp_sizes = [len(c) for c in sorted(components, key=len, reverse=True)]
    num_components = len(components)
    largest_comp_size = comp_sizes[0] if comp_sizes else 0
    largest_comp_ratio = round(largest_comp_size / total_nodes, 4) if total_nodes > 0 else 0.0

    # 5. Density and Clustering
    density = float(nx.density(G))
    isolates_count = len(list(nx.isolates(G)))

    stats = {
        "graph_overview": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "density": round(density, 6),
            "isolated_nodes_count": isolates_count,
        },
        "nodes_by_type": nodes_by_type,
        "edges_by_relationship": edges_by_rel,
        "degree_distribution": {
            "min": min_deg,
            "max": max_deg,
            "mean": round(mean_deg, 2),
            "median": round(median_deg, 2),
            "std": round(std_deg, 2),
            "p25": round(p25_deg, 2),
            "p75": round(p75_deg, 2),
            "top_degree_nodes": top_degree_nodes,
            "degree_by_node_type": degrees_by_type,
        },
        "connected_components": {
            "number_of_components": num_components,
            "largest_component_size": largest_comp_size,
            "largest_component_ratio": largest_comp_ratio,
            "component_sizes_top10": comp_sizes[:10],
        },
    }
    return stats


def generate_graph_statistics_report(
    nodes_path: str = "data/graph/nodes.csv",
    edges_path: str = "data/graph/edges.csv",
    output_path: Optional[str] = "reports/graph_statistics.json",
) -> Dict[str, Any]:
    """Loads graph CSVs, computes graph statistics, and saves output to JSON report."""
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)
    stats = compute_graph_statistics(nodes_df, edges_df)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    return stats


if __name__ == "__main__":
    print("Computing graph statistics...")
    stats = generate_graph_statistics_report()
    print("Graph Overview:")
    for k, v in stats["graph_overview"].items():
        print(f"  {k}: {v}")
    print("\nNodes by Type:")
    for k, v in stats["nodes_by_type"].items():
        print(f"  {k}: {v}")
    print("\nEdges by Relationship:")
    for k, v in stats["edges_by_relationship"].items():
        print(f"  {k}: {v}")
    print("\nDegree Distribution Summary:")
    for k, v in stats["degree_distribution"].items():
        if k not in ["top_degree_nodes", "degree_by_node_type"]:
            print(f"  {k}: {v}")
    print("\nConnected Components:")
    for k, v in stats["connected_components"].items():
        print(f"  {k}: {v}")
