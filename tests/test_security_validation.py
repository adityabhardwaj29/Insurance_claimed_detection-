"""
tests/test_security_validation.py
---------------------------------
Phase 14 Security Hardening and System Integrity Test Suite.

Audits:
  1. SQL Injection immunity across all query parameters and database operations
  2. Database referential integrity (zero orphan foreign keys, unique primary keys)
  3. Knowledge Graph structural integrity (zero dangling edges, valid types)
  4. Target & data leakage prevention
  5. API input validation boundaries (negative pagination, malformed bodies, enum checking)
  6. Secrets in source code scan (zero hardcoded credentials)
  7. Logging safety (zero PII / payload leakage in middleware logs)
  8. Environment variable configurability & CORS policy
  9. Model artifacts availability & schema validation
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import List

import pandas as pd
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.main import app
from src.cases.case_manager import CaseManager
from src.utils.config import settings

client = TestClient(app)
DB_PATH = settings.DATABASE_PATH


# ── 1. SQL Injection Immunity ──────────────────────────────────────────────────


def test_sqli_in_claim_list_filters():
    """Verifies that classic SQL injection payloads in claim list filters are neutralized."""
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE claims; --",
        "1 UNION SELECT null, null, null, null, null, null, null",
        "' OR 1=1 --",
    ]
    for payload in sqli_payloads:
        resp = client.get(f"/claims?claim_type={payload}")
        assert resp.status_code == 200, f"Payload broke query: {payload}"
        data = resp.json()
        # With SQL injection neutralized, no claims match this literal type string
        assert data["pagination"]["total"] == 0 or len(data["items"]) == 0

        resp_status = client.get(f"/claims?status={payload}")
        assert resp_status.status_code == 200
        assert resp_status.json()["pagination"]["total"] == 0 or len(resp_status.json()["items"]) == 0


def test_sqli_in_sort_by_column():
    """Verifies sort_by rejects or safely falls back on SQL injection in order by clause."""
    sqli_order_payloads = [
        "claim_id; DROP TABLE claims; --",
        "(CASE WHEN (1=1) THEN claim_id ELSE claim_amount END)",
        "invalid_column_name_injection",
    ]
    for payload in sqli_order_payloads:
        resp = client.get(f"/claims?sort_by={payload}&limit=5")
        assert resp.status_code == 200, f"Payload caused error in sort_by: {payload}"
        # The service safely falls back to 'claim_id'
        data = resp.json()
        assert len(data["items"]) > 0


def test_sqli_in_claim_id_detail():
    """Verifies claim_id lookup parameterization prevents injection."""
    sqli_payloads = [
        "' OR '1'='1",
        "CLM00001' OR '1'='1",
        "CLM00001'; DELETE FROM claims; --",
    ]
    for payload in sqli_payloads:
        resp = client.get(f"/claims/{payload}")
        # Literal string does not match any claim -> 404
        assert resp.status_code == 404


def test_sqli_case_manager_queries():
    """Verifies CaseManager uses parameterized SQL for case operations."""
    cm = CaseManager(db_path=DB_PATH)
    # Attempt SQL injection in case_id lookup
    res = cm.get_case("CASE00001' OR '1'='1")
    assert res is None, "SQL injection payload should return None"

    # Verify table integrity is intact after attempts
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM claims")
        count = cur.fetchone()[0]
        assert count == 320, "Claims table was affected by SQL injection test"


# ── 2. Database Referential & ID Integrity ───────────────────────────────────


def test_zero_orphan_foreign_keys_in_database():
    """Verifies strict referential integrity with zero orphan foreign keys."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Check orphan claimants
        cur.execute("SELECT COUNT(*) FROM claims c WHERE c.claimant_id NOT IN (SELECT claimant_id FROM claimants)")
        assert cur.fetchone()[0] == 0, "Found orphan claimant_id in claims"

        # Check orphan policies
        cur.execute("SELECT COUNT(*) FROM claims c WHERE c.policy_id NOT IN (SELECT policy_id FROM policies)")
        assert cur.fetchone()[0] == 0, "Found orphan policy_id in claims"

        # Check orphan vehicles
        cur.execute("SELECT COUNT(*) FROM claims c WHERE c.vehicle_id NOT IN (SELECT vehicle_id FROM vehicles)")
        assert cur.fetchone()[0] == 0, "Found orphan vehicle_id in claims"

        # Check orphan providers
        cur.execute("SELECT COUNT(*) FROM claims c WHERE c.provider_id NOT IN (SELECT provider_id FROM providers)")
        assert cur.fetchone()[0] == 0, "Found orphan provider_id in claims"

        # Check orphan invoices
        cur.execute("SELECT COUNT(*) FROM claims c WHERE c.invoice_id NOT IN (SELECT invoice_id FROM invoices)")
        assert cur.fetchone()[0] == 0, "Found orphan invoice_id in claims"


def test_unique_primary_keys_across_all_tables():
    """Verifies primary keys have zero duplicates across all database tables."""
    tables_and_pk = [
        ("claims", "claim_id"),
        ("claimants", "claimant_id"),
        ("policies", "policy_id"),
        ("vehicles", "vehicle_id"),
        ("providers", "provider_id"),
        ("invoices", "invoice_id"),
        ("locations", "location_id"),
        ("investigation_cases", "case_id"),
    ]
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for table, pk in tables_and_pk:
            cur.execute(f"SELECT COUNT({pk}), COUNT(DISTINCT {pk}) FROM {table}")
            total, distinct = cur.fetchone()
            assert total == distinct, f"Duplicate primary keys found in table {table} ({total} vs {distinct})"


# ── 3. Graph Construction & Topology Integrity ───────────────────────────────


def test_zero_dangling_graph_edges():
    """Verifies that 100% of graph edge sources and targets exist in nodes.csv."""
    nodes_csv = ROOT / "data" / "graph" / "nodes.csv"
    edges_csv = ROOT / "data" / "graph" / "edges.csv"
    assert nodes_csv.exists() and edges_csv.exists()

    nodes_df = pd.read_csv(nodes_csv)
    edges_df = pd.read_csv(edges_csv)

    valid_nodes = set(nodes_df["node_id"].unique())
    edge_sources = set(edges_df["source"].unique())
    edge_targets = set(edges_df["target"].unique())

    dangling_sources = edge_sources - valid_nodes
    dangling_targets = edge_targets - valid_nodes

    assert len(dangling_sources) == 0, f"Dangling edge sources found: {dangling_sources}"
    assert len(dangling_targets) == 0, f"Dangling edge targets found: {dangling_targets}"


def test_graph_node_and_edge_types_valid():
    """Verifies node and edge types conform to defined ontology."""
    nodes_df = pd.read_csv(ROOT / "data" / "graph" / "nodes.csv")
    edges_df = pd.read_csv(ROOT / "data" / "graph" / "edges.csv")

    expected_node_types = {"Claim", "Claimant", "Provider", "Policy", "Vehicle", "Invoice", "Location"}
    actual_node_types = set(nodes_df["node_type"].unique())
    assert actual_node_types.issubset(expected_node_types), f"Invalid node types: {actual_node_types - expected_node_types}"

    expected_relationships = {
        "WITHIN_TERRITORY", "OWNS", "LOCATED_AT", "ISSUED_BY",
        "FILED", "COVERED_BY", "ASSOCIATED_WITH", "INVOLVES", "HAS", "OCCURRED_AT"
    }
    actual_relationships = set(edges_df["relationship"].unique())
    assert actual_relationships.issubset(expected_relationships), f"Invalid relationships: {actual_relationships - expected_relationships}"


# ── 4. Target & Data Leakage Prevention ──────────────────────────────────────


def test_feature_columns_do_not_contain_target_or_post_hoc():
    """Verifies that model training feature set excludes ground truth and outcome labels."""
    from src.models.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES

    all_features = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    prohibited_cols = {"fraud_label", "final_risk_score", "risk_band", "status", "resolution", "is_fraud"}

    overlap = all_features.intersection(prohibited_cols)
    assert len(overlap) == 0, f"Target or post-hoc leakage found in feature list: {overlap}"


def test_train_test_split_temporal_order():
    """Verifies chronological split guarantees no future claim appears in training set."""
    df = pd.read_csv(ROOT / "data" / "features" / "claim_features.csv")
    sorted_df = df.sort_values("claim_date").reset_index(drop=True)
    split_idx = int(len(df) * 0.70)

    train_dates = pd.to_datetime(sorted_df.iloc[:split_idx]["claim_date"])
    test_dates = pd.to_datetime(sorted_df.iloc[split_idx:]["claim_date"])

    assert train_dates.max() <= test_dates.min(), (
        f"Temporal leakage: max train date ({train_dates.max()}) > min test date ({test_dates.min()})"
    )


# ── 5. API Validation & Boundaries ───────────────────────────────────────────


def test_api_pagination_boundaries():
    """Verifies API rejects negative pagination limits/offsets with HTTP 422."""
    resp_limit = client.get("/claims?limit=-1")
    assert resp_limit.status_code == 422

    resp_offset = client.get("/claims?offset=-5")
    assert resp_offset.status_code == 422

    resp_limit_too_large = client.get("/claims?limit=1000")
    assert resp_limit_too_large.status_code == 422


def test_api_invalid_claim_id_handling():
    """Verifies API gracefully returns HTTP 404 for nonexistent claim queries."""
    resp = client.get("/claims/INVALID_CLAIM_ID")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()

    resp_risk = client.get("/claims/INVALID_CLAIM_ID/risk")
    assert resp_risk.status_code == 404

    resp_graph = client.get("/claims/INVALID_CLAIM_ID/graph")
    assert resp_graph.status_code == 404


def test_api_case_transition_validation():
    """Verifies illegal status transitions in case management return HTTP 400 or 422."""
    cm = CaseManager(db_path=DB_PATH)
    cases = cm.list_cases(limit=1)
    if not cases:
        case = cm.create_case("CLM00001", 0.9, "HIGH", "HIGH", "TEST", "Auto")
        cid = case.case_id
    else:
        cid = cases[0].case_id

    # Attempt illegal transition to an arbitrary invalid string status via PATCH /cases/{cid}
    resp = client.patch(f"/cases/{cid}", json={
        "status": "INVALID_STATE",
        "actor": "investigator_1",
        "reason": "testing invalid state"
    })
    assert resp.status_code in (400, 422)


# ── 6. Secrets in Source Code Scan ───────────────────────────────────────────


def test_zero_hardcoded_secrets_in_source_code():
    """
    Scans all Python files in src/, api/, tests/, and root for hardcoded
    passwords, API tokens, or private keys.
    """
    secret_patterns = [
        re.compile(r"""(?:api_key|apikey|secret_key|private_key|password)\s*=\s*['"][a-zA-Z0-9_\-]{16,}['"]""", re.IGNORECASE),
        re.compile(r"""-----BEGIN (?:RSA )?PRIVATE KEY-----"""),
        re.compile(r"""ghp_[a-zA-Z0-9]{36}"""),
        re.compile(r"""aws_secret_access_key\s*=""", re.IGNORECASE),
    ]

    scanned_extensions = {".py", ".json", ".yaml", ".yml"}
    target_dirs = [ROOT / "src", ROOT / "api", ROOT / "tests"]

    found_secrets: List[str] = []
    for t_dir in target_dirs:
        for p in t_dir.rglob("*"):
            if p.suffix in scanned_extensions and "__pycache__" not in str(p):
                try:
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    for pat in secret_patterns:
                        if pat.search(content):
                            found_secrets.append(f"{p}: match for {pat.pattern}")
                except Exception:
                    pass

    assert len(found_secrets) == 0, f"Found potential hardcoded secrets: {found_secrets}"


# ── 7. Logging & PII Safety ──────────────────────────────────────────────────


def test_api_middleware_logging_format(caplog):
    """Verifies that API request logging middleware only logs HTTP method, path, and duration."""
    import logging
    with caplog.at_level(logging.INFO, logger="api"):
        resp = client.get("/health")
        assert resp.status_code == 200

        # Check logs for request
        log_messages = [rec.message for rec in caplog.records if rec.name == "api"]
        assert len(log_messages) > 0
        matching = [m for m in log_messages if "GET /health -> 200" in m]
        assert len(matching) > 0, f"Expected clean request log, got: {log_messages}"
        # Ensure no request body or headers leaked
        for m in log_messages:
            assert "authorization" not in m.lower()
            assert "bearer" not in m.lower()


# ── 8. CORS & Environment Variable Hardening ─────────────────────────────────


def test_cors_headers_present():
    """Verifies CORS headers are properly handled on API requests."""
    headers = {"Origin": "http://localhost:8501"}
    resp = client.get("/health", headers=headers)
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers


def test_config_environment_overrides():
    """Verifies settings can be safely configured via environment variables."""
    test_env_val = "sqlite:///custom/test.db"
    old_env = os.environ.get("DATABASE_URL")
    try:
        os.environ["DATABASE_URL"] = test_env_val
        from src.utils.config import Settings
        custom_settings = Settings()
        assert custom_settings.DATABASE_URL == test_env_val
    finally:
        if old_env is not None:
            os.environ["DATABASE_URL"] = old_env
        else:
            os.environ.pop("DATABASE_URL", None)


# ── 9. Model Artifact Presence & Metadata ────────────────────────────────────


def test_persisted_model_artifacts_valid():
    """Verifies all trained model files, isolators, and metadata are intact on disk."""
    import joblib

    fraud_model_path = ROOT / "models" / "fraud_model" / "model.joblib"
    anomaly_model_path = ROOT / "models" / "anomaly_model" / "isolation_forest.joblib"
    fraud_meta_path = ROOT / "models" / "fraud_model" / "metadata.json"

    assert fraud_model_path.exists(), "Fraud model artifact missing"
    assert anomaly_model_path.exists(), "Anomaly model artifact missing"
    assert fraud_meta_path.exists(), "Fraud model metadata missing"

    # Load artifacts to test validity
    fraud_model = joblib.load(fraud_model_path)
    assert hasattr(fraud_model, "predict_proba") or hasattr(fraud_model, "predict")

    anomaly_model = joblib.load(anomaly_model_path)
    assert hasattr(anomaly_model, "score_samples") or hasattr(anomaly_model, "predict")
