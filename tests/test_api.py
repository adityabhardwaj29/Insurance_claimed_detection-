"""
tests/test_api.py
-----------------
Comprehensive API test suite covering all 15 endpoints:
Health, Claims, Risk, Graph, Duplicates, Explanations, Cases, Dashboard,
Predict, Anomaly-Score, and Graph-Analysis.
"""

from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


# ── 1. Health & Docs ─────────────────────────────────────────────────────────


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True
    assert data["total_claims"] == 320
    assert "fraud_xgboost" in data["models_ready"]


def test_openapi_schema():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "paths" in spec
    assert "/health" in spec["paths"]
    assert "/claims" in spec["paths"]
    assert "/cases" in spec["paths"]
    assert "/dashboard/summary" in spec["paths"]
    assert "/predict" in spec["paths"]
    assert "/anomaly-score" in spec["paths"]
    assert "/graph-analysis" in spec["paths"]


# ── 2. Claims Endpoints ──────────────────────────────────────────────────────


def test_list_claims_pagination():
    r = client.get("/claims?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) == 10
    assert data["pagination"]["total"] == 320
    assert data["pagination"]["limit"] == 10
    assert data["pagination"]["offset"] == 0


def test_list_claims_filtering_and_sorting():
    # Filter by claim_type
    r = client.get("/claims?claim_type=Accident")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["claim_type"] == "Accident"

    # Filter by fraud_label
    r = client.get("/claims?fraud_label=1")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["fraud_label"] == 1

    # Sorting
    r = client.get("/claims?sort_by=claim_amount&sort_order=desc&limit=5")
    assert r.status_code == 200
    items = r.json()["items"]
    amounts = [it["claim_amount"] for it in items]
    assert amounts == sorted(amounts, reverse=True)


def test_get_claim_detail():
    r = client.get("/claims/CLM00001")
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert "claimant" in data
    assert "provider" in data
    assert "policy" in data
    assert "vehicle" in data
    assert "invoice" in data
    assert data["claimant"]["claimant_id"] == "CLT0099"


def test_get_claim_detail_404():
    r = client.get("/claims/CLM99999")
    assert r.status_code == 404


def test_get_claim_risk():
    r = client.get("/claims/CLM00001/risk")
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert 0.0 <= data["final_risk_score"] <= 1.0
    assert data["risk_band"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert 0.0 <= data["anomaly_score"] <= 1.0
    assert 0.0 <= data["duplicate_score"] <= 1.0
    assert 0.0 <= data["graph_risk_score"] <= 1.0
    assert isinstance(data["risk_reasons"], list)


def test_get_claim_risk_404():
    r = client.get("/claims/CLM99999/risk")
    assert r.status_code == 404


def test_get_claim_graph():
    r = client.get("/claims/CLM00001/graph")
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 5
    assert len(data["edges"]) >= 4
    assert data["claimant_degree"] >= 1
    assert data["provider_claim_count"] >= 1


def test_get_claim_graph_404():
    r = client.get("/claims/CLM99999/graph")
    assert r.status_code == 404


def test_get_claim_duplicates():
    r = client.get("/claims/CLM00001/duplicates")
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert 0.0 <= data["duplicate_similarity_score"] <= 1.0
    assert isinstance(data["matching_attributes"], list)


def test_get_claim_duplicates_404():
    r = client.get("/claims/CLM99999/duplicates")
    assert r.status_code == 404


def test_get_claim_explanation():
    r = client.get("/claims/CLM00001/explanation")
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert "signals" in data
    assert "weights" in data
    assert "summary" in data
    assert "fraud_probability" in data["signals"]
    assert data["weights"]["fraud_probability"] == 0.45


def test_get_claim_explanation_404():
    r = client.get("/claims/CLM99999/explanation")
    assert r.status_code == 404


# ── 3. Case Management Endpoints ─────────────────────────────────────────────


def test_list_cases_endpoint():
    r = client.get("/cases?limit=10")
    assert r.status_code == 200
    cases = r.json()
    assert isinstance(cases, list)
    assert len(cases) <= 10


def test_create_and_patch_case():
    unique_id = f"CASE-API-{uuid.uuid4().hex[:6]}"
    create_payload = {
        "claim_id": "CLM00001",
        "case_id": unique_id,
        "risk_score": 0.75,
        "risk_band": "CRITICAL",
        "priority": "HIGH",
        "reason": "HIGH_FRAUD_PROBABILITY",
        "notes": "Created via test_api",
    }
    r = client.post("/cases", json=create_payload)
    assert r.status_code == 201
    case = r.json()
    assert case["case_id"] == unique_id
    assert case["status"] == "NEW"

    # GET case
    r_get = client.get(f"/cases/{unique_id}")
    assert r_get.status_code == 200
    assert r_get.json()["case_id"] == unique_id

    # PATCH case (assign and update priority)
    patch_payload = {
        "assigned_to": "Inv. Sarah Jenkins",
        "priority": "CRITICAL",
        "notes": "Reviewed damage report and assigned priority",
    }
    r_patch = client.patch(f"/cases/{unique_id}", json=patch_payload)
    assert r_patch.status_code == 200
    patched = r_patch.json()
    assert patched["assigned_to"] == "Inv. Sarah Jenkins"
    assert patched["priority"] == "CRITICAL"
    assert patched["status"] == "UNDER_REVIEW"  # Auto-transitioned on assignment

    # PATCH case to resolve
    patch_resolve = {
        "status": "RESOLVED",
        "resolution": "Confirmed collusion with provider for false billing",
    }
    r_res = client.patch(f"/cases/{unique_id}", json=patch_resolve)
    assert r_res.status_code == 200
    assert r_res.json()["status"] == "RESOLVED"
    assert "Confirmed collusion" in r_res.json()["resolution"]


def test_patch_case_404():
    r = client.patch("/cases/CASE-NONEXISTENT", json={"priority": "LOW"})
    assert r.status_code == 404


# ── 4. Dashboard Summary ─────────────────────────────────────────────────────


def test_dashboard_summary():
    r = client.get("/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_claims"] == 320
    assert data["total_claim_amount"] > 0
    assert data["fraud_claims_count"] == 52
    assert data["fraud_rate_pct"] == 16.25
    assert data["average_risk_score"] > 0.20
    assert data["high_risk_claims_count"] == 27
    assert isinstance(data["cases_by_status"], dict)


# ── 5. Predictive Endpoints ──────────────────────────────────────────────────


def test_predict_with_claim_id():
    payload = {"claim_id": "CLM00001"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["fraud_prediction"] in (0, 1)
    assert data["risk_tier"] in ("LOW", "MEDIUM", "HIGH")


def test_predict_with_feature_dict():
    payload = {
        "claim_amount": 125000.0,
        "claim_type": "Accident",
        "policy_type": "Comprehensive",
        "vehicle_type": "SUV",
        "vehicle_make": "Tata",
        "provider_type": "Garage",
        "claimant_city": "Mumbai",
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["fraud_prediction"] in (0, 1)


def test_anomaly_score_endpoint():
    # With existing claim
    r = client.post("/anomaly-score", json={"claim_id": "CLM00001"})
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["anomaly_score"] <= 1.0
    assert isinstance(data["is_anomaly"], bool)

    # With feature payload
    r_feat = client.post("/anomaly-score", json={"features": {"claim_amount": 150000.0}})
    assert r_feat.status_code == 200
    assert 0.0 <= r_feat.json()["anomaly_score"] <= 1.0


def test_graph_analysis_endpoint():
    payload = {"claim_id": "CLM00001"}
    r = client.post("/graph-analysis", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["claim_id"] == "CLM00001"
    assert 0.0 <= data["graph_risk_score"] <= 1.0
    assert data["claimant_degree"] >= 1
    assert data["provider_claim_count"] >= 1
    assert "network_summary" in data
