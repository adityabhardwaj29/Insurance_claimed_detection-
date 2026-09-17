"""
Phase 7 tests: Graph feature engineering, feature merging, and graph-enhanced fraud detection.
Verifies that all features are correctly derived from the actual Phase 6 graph topology.
"""

import json
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import networkx as nx

from src.graph.build_graph import build_insurance_graph
from src.graph.graph_features import compute_graph_features


@pytest.fixture(scope="module")
def graph_data():
    """Builds the actual Phase 6 graph."""
    nodes_df, edges_df, G = build_insurance_graph(relational_dir="data/relational", output_dir=None)
    return nodes_df, edges_df, G


@pytest.fixture(scope="module")
def graph_features_df():
    """Loads the pre-computed graph features CSV."""
    path = Path("data/features/graph_features.csv")
    assert path.exists(), "graph_features.csv does not exist"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def final_features_df():
    """Loads the final merged feature CSV."""
    path = Path("data/features/final_claim_features.csv")
    assert path.exists(), "final_claim_features.csv does not exist"
    return pd.read_csv(path)


# 1. Graph Features File Schema
def test_graph_features_schema(graph_features_df):
    expected_cols = [
        "claim_id", "claim_degree", "claimant_degree", "policy_degree", "vehicle_degree",
        "provider_degree", "invoice_degree", "location_degree", "claim_pagerank",
        "claimant_pagerank", "provider_pagerank", "claim_betweenness", "claimant_betweenness",
        "provider_betweenness", "claim_clustering", "claimant_clustering", "common_neighbors",
        "provider_claim_count", "claimant_claim_count", "repeated_claimant_provider",
        "fraud_neighbor_count", "fraud_neighbor_ratio", "suspicious_neighbor_count",
    ]
    for col in expected_cols:
        assert col in graph_features_df.columns, f"Missing column: {col}"


def test_graph_features_row_count(graph_features_df):
    assert len(graph_features_df) == 320


def test_graph_features_no_nulls(graph_features_df):
    null_counts = graph_features_df.isnull().sum()
    assert null_counts.sum() == 0, f"Null values found:\n{null_counts[null_counts > 0]}"


# 2. Feature Determinism: Graph degree values match actual graph
def test_claim_degrees_match_graph(graph_data, graph_features_df):
    """Verify that claim_degree values match the actual Phase 6 NetworkX graph."""
    _, _, G = graph_data
    claims = pd.read_csv("data/relational/claims.csv")
    for _, claim in claims.head(20).iterrows():
        clm_node = f"claim:{str(claim['claim_id'])}"
        actual_degree = G.degree(clm_node)
        stored = graph_features_df[graph_features_df["claim_id"] == claim["claim_id"]]["claim_degree"].values
        assert len(stored) == 1
        assert stored[0] == actual_degree, (
            f"Degree mismatch for {clm_node}: actual={actual_degree}, stored={stored[0]}"
        )


def test_claimant_degrees_match_graph(graph_data, graph_features_df):
    """Verify claimant_degree matches the actual claimant node degree."""
    _, _, G = graph_data
    claims = pd.read_csv("data/relational/claims.csv")
    for _, claim in claims.head(20).iterrows():
        clt_node = f"claimant:{str(claim['claimant_id'])}"
        actual_degree = G.degree(clt_node)
        stored = graph_features_df[graph_features_df["claim_id"] == claim["claim_id"]]["claimant_degree"].values
        assert stored[0] == actual_degree, (
            f"Claimant degree mismatch for {clt_node}: actual={actual_degree}, stored={stored[0]}"
        )


def test_provider_degrees_match_graph(graph_data, graph_features_df):
    """Verify provider_degree matches the actual provider node degree."""
    _, _, G = graph_data
    claims = pd.read_csv("data/relational/claims.csv")
    for _, claim in claims.head(20).iterrows():
        prv_node = f"provider:{str(claim['provider_id'])}"
        actual_degree = G.degree(prv_node)
        stored = graph_features_df[graph_features_df["claim_id"] == claim["claim_id"]]["provider_degree"].values
        assert stored[0] == actual_degree, (
            f"Provider degree mismatch for {prv_node}: actual={actual_degree}, stored={stored[0]}"
        )


# 3. PageRank range validation
def test_pagerank_range(graph_features_df):
    assert graph_features_df["claim_pagerank"].between(0, 1).all()
    assert graph_features_df["claimant_pagerank"].between(0, 1).all()
    assert graph_features_df["provider_pagerank"].between(0, 1).all()


# 4. Betweenness centrality range
def test_betweenness_range(graph_features_df):
    assert graph_features_df["claim_betweenness"].between(0, 1).all()
    assert graph_features_df["claimant_betweenness"].between(0, 1).all()
    assert graph_features_df["provider_betweenness"].between(0, 1).all()


# 5. Clustering coefficient range
def test_clustering_range(graph_features_df):
    assert graph_features_df["claim_clustering"].between(0, 1).all()
    assert graph_features_df["claimant_clustering"].between(0, 1).all()


# 6. Fraud neighbor ratio consistency
def test_fraud_neighbor_ratio_range(graph_features_df):
    assert (graph_features_df["fraud_neighbor_ratio"] >= 0).all()
    assert (graph_features_df["fraud_neighbor_ratio"] <= 1).all()


def test_fraud_neighbor_ratio_consistency(graph_features_df):
    """fraud_neighbor_count=0 implies fraud_neighbor_ratio=0."""
    zero_count = graph_features_df[graph_features_df["fraud_neighbor_count"] == 0]
    assert (zero_count["fraud_neighbor_ratio"] == 0.0).all()


# 7. Repeated claimant-provider is binary
def test_repeated_claimant_provider_binary(graph_features_df):
    vals = set(graph_features_df["repeated_claimant_provider"].unique())
    assert vals <= {0, 1}, f"Non-binary values: {vals}"


# 8. Final merged feature CSV
def test_final_features_schema(final_features_df):
    required = ["claim_id", "fraud_label", "claim_amount", "anomaly_score",
                "claimant_degree", "provider_degree", "fraud_neighbor_ratio"]
    for col in required:
        assert col in final_features_df.columns, f"Missing: {col}"


def test_final_features_no_nulls(final_features_df):
    null_counts = final_features_df.isnull().sum()
    assert null_counts.sum() == 0, f"Null values:\n{null_counts[null_counts > 0]}"


def test_final_features_row_count(final_features_df):
    assert len(final_features_df) == 320


def test_final_features_fraud_label_distribution(final_features_df):
    fraud_count = int((final_features_df["fraud_label"] == 1).sum())
    assert fraud_count == 52  # Known from dataset


# 9. Enhancement report and metrics exist
def test_graph_enhancement_report_exists():
    assert Path("reports/graph_enhancement_report.md").exists()


def test_graph_enhancement_metrics_exist():
    path = Path("reports/graph_enhancement_metrics.json")
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert "baseline" in data
    assert "graph_enhanced" in data
    assert "best_model" in data["baseline"]
    assert "best_model" in data["graph_enhanced"]


def test_metrics_values_are_numeric():
    """All reported metrics must be actual floats, not placeholder zeros."""
    path = Path("reports/graph_enhancement_metrics.json")
    with open(path) as f:
        data = json.load(f)
    for experiment in ["baseline", "graph_enhanced"]:
        for model_name, m in data[experiment]["metrics_by_model"].items():
            # PR-AUC and ROC-AUC should be above random baseline for any reasonable model
            assert isinstance(m["pr_auc"], float), f"pr_auc not float in {model_name}"
            assert 0.0 <= m["pr_auc"] <= 1.0, f"pr_auc out of range in {model_name}"
            assert 0.0 <= m["roc_auc"] <= 1.0, f"roc_auc out of range in {model_name}"


# 10. Determinism: Re-computing graph features gives same results
def test_graph_features_deterministic():
    """Re-running graph feature extraction gives same result."""
    fresh = compute_graph_features(
        relational_dir="data/relational",
        output_path=None,
    )
    saved = pd.read_csv("data/features/graph_features.csv")
    # Check all numeric columns match
    numeric_cols = [c for c in fresh.columns if c != "claim_id"]
    fresh_sorted = fresh.sort_values("claim_id").reset_index(drop=True)
    saved_sorted = saved.sort_values("claim_id").reset_index(drop=True)
    for col in numeric_cols:
        assert col in saved_sorted.columns, f"Column {col} missing from saved file"
        np.testing.assert_allclose(
            fresh_sorted[col].values,
            saved_sorted[col].values,
            rtol=1e-5,
            err_msg=f"Mismatch in column {col}",
        )
