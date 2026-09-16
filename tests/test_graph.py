"""
Unit and Integration Tests for Phase 6: Graph Construction, Validation, and Statistics.
Verifies academic reproducibility, referential integrity, zero orphans, zero self-loops,
relationship semantics, and network topological properties.
"""

import json
from pathlib import Path
import pytest
import pandas as pd
import networkx as nx

from src.graph.build_graph import build_insurance_graph, extract_nodes, extract_edges
from src.graph.validate_graph import validate_graph, validate_graph_files, EXPECTED_NODE_COLUMNS, EXPECTED_EDGE_COLUMNS
from src.graph.statistics import compute_graph_statistics, generate_graph_statistics_report


@pytest.fixture(scope="module")
def graph_data():
    """Loads nodes and edges from data/graph/."""
    nodes_path = Path("data/graph/nodes.csv")
    edges_path = Path("data/graph/edges.csv")
    assert nodes_path.exists(), "nodes.csv does not exist"
    assert edges_path.exists(), "edges.csv does not exist"

    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)
    return nodes_df, edges_df


# 1. Schema and File Integrity Tests
def test_nodes_file_schema(graph_data):
    nodes_df, _ = graph_data
    assert list(nodes_df.columns) == EXPECTED_NODE_COLUMNS
    assert len(nodes_df) > 0
    assert not nodes_df["node_id"].isnull().any()
    assert not nodes_df["node_type"].isnull().any()
    assert not nodes_df["source_id"].isnull().any()


def test_edges_file_schema(graph_data):
    _, edges_df = graph_data
    assert list(edges_df.columns) == EXPECTED_EDGE_COLUMNS
    assert len(edges_df) > 0
    assert not edges_df["source"].isnull().any()
    assert not edges_df["target"].isnull().any()
    assert not edges_df["relationship"].isnull().any()
    assert not edges_df["weight"].isnull().any()


# 2. Entity Counts and Types
def test_node_types_and_counts(graph_data):
    nodes_df, _ = graph_data
    type_counts = nodes_df["node_type"].value_counts().to_dict()
    assert type_counts.get("Claim") == 320
    assert type_counts.get("Invoice") == 220
    assert type_counts.get("Policy") == 140
    assert type_counts.get("Vehicle") == 130
    assert type_counts.get("Claimant") == 120
    assert type_counts.get("Location") == 65
    assert type_counts.get("Provider") == 25
    assert len(nodes_df) == 1020


def test_unique_node_ids(graph_data):
    nodes_df, _ = graph_data
    assert nodes_df["node_id"].is_unique, "Duplicate node_id values found in nodes.csv"


# 3. Referential Integrity & No Orphan Edges
def test_no_orphan_edges(graph_data):
    nodes_df, edges_df = graph_data
    node_ids = set(nodes_df["node_id"])

    invalid_sources = [s for s in edges_df["source"] if s not in node_ids]
    invalid_targets = [t for t in edges_df["target"] if t not in node_ids]

    assert len(invalid_sources) == 0, f"Found orphan sources: {invalid_sources[:5]}"
    assert len(invalid_targets) == 0, f"Found orphan targets: {invalid_targets[:5]}"


# 4. No Accidental Self-Loops
def test_no_accidental_self_loops(graph_data):
    _, edges_df = graph_data
    self_loops = edges_df[edges_df["source"] == edges_df["target"]]
    assert len(self_loops) == 0, f"Found accidental self-loops: {self_loops.to_dict(orient='records')}"


# 5. Relationship Type Consistency
def test_relationship_consistency(graph_data):
    nodes_df, edges_df = graph_data
    node_type_map = dict(zip(nodes_df["node_id"], nodes_df["node_type"]))

    for _, r in edges_df.iterrows():
        rel = r["relationship"]
        src_type = node_type_map[r["source"]]
        tgt_type = node_type_map[r["target"]]

        if rel == "FILED":
            assert (src_type, tgt_type) == ("Claimant", "Claim")
        elif rel == "COVERED_BY":
            assert (src_type, tgt_type) == ("Claim", "Policy")
        elif rel == "ASSOCIATED_WITH":
            assert (src_type, tgt_type) == ("Claim", "Vehicle")
        elif rel == "INVOLVES":
            assert (src_type, tgt_type) == ("Claim", "Provider")
        elif rel == "HAS":
            assert (src_type, tgt_type) == ("Claim", "Invoice")
        elif rel == "OCCURRED_AT":
            assert (src_type, tgt_type) == ("Claim", "Location")
        elif rel == "OWNS":
            assert src_type == "Claimant" and tgt_type in ("Policy", "Vehicle")
        elif rel == "ISSUED_BY":
            assert (src_type, tgt_type) == ("Invoice", "Provider")
        elif rel == "LOCATED_AT":
            assert src_type in ("Claimant", "Provider") and tgt_type == "Location"
        elif rel == "WITHIN_TERRITORY":
            assert (src_type, tgt_type) == ("Location", "Location")
        else:
            pytest.fail(f"Unrecognized relationship: {rel}")


# 6. Valid JSON Attributes
def test_node_attributes_valid_json(graph_data):
    nodes_df, _ = graph_data
    for _, r in nodes_df.iterrows():
        attrs = json.loads(r["attributes"])
        assert isinstance(attrs, dict)


# 7. Validation Module Checks
def test_validation_module_clean(graph_data):
    nodes_df, edges_df = graph_data
    res = validate_graph(nodes_df, edges_df)
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0
    assert all(chk["passed"] for chk in res["checks"].values())


def test_validation_module_flags_corrupted():
    bad_nodes = pd.DataFrame([
        {"node_id": "claim:1", "node_type": "Claim", "source_id": "1", "attributes": "{bad_json"},
    ])
    bad_edges = pd.DataFrame([
        {"source": "claim:1", "target": "claim:999", "relationship": "FILED", "weight": 1.0},
    ])
    res = validate_graph(bad_nodes, bad_edges)
    assert res["is_valid"] is False
    assert res["checks"]["referential_integrity"]["passed"] is False
    assert res["checks"]["attribute_json_validity"]["passed"] is False


# 8. Graph Topological Properties & Statistics Module
def test_graph_statistics_and_connectivity(graph_data):
    nodes_df, edges_df = graph_data
    stats = compute_graph_statistics(nodes_df, edges_df)

    assert stats["graph_overview"]["total_nodes"] == 1020
    assert stats["graph_overview"]["total_edges"] == 2615
    assert stats["graph_overview"]["isolated_nodes_count"] == 0
    assert stats["connected_components"]["number_of_components"] == 1
    assert stats["connected_components"]["largest_component_size"] == 1020
    assert stats["degree_distribution"]["min"] >= 1
    assert stats["degree_distribution"]["max"] > 100


# 9. End-to-End Build Graph Determinism
def test_build_insurance_graph_determinism():
    n_df, e_df, G = build_insurance_graph(relational_dir="data/relational", output_dir=None)
    assert len(n_df) == 1020
    assert len(e_df) == 2615
    assert G.number_of_nodes() == 1020
    assert G.number_of_edges() == 2615
    assert nx.number_connected_components(G) == 1
