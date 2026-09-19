"""
tests/test_enterprise_platform.py
---------------------------------
Automated tests for the new enterprise platform endpoints:
Auth, Customers, Policies, Claims Wizard & Analysis, Decisions, Reports, Audit Logs, and Health.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verifies that the /api/health endpoint returns detailed component readiness."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api"] == "ok"
    assert "database" in data
    assert "models" in data
    assert data["database"]["status"] == "connected"


def test_auth_flow():
    """Tests login with demo credentials and profile inspection."""
    # Successful login
    login_resp = client.post("/api/auth/login", json={
        "email": "claims.officer@insurance.com",
        "password": "claims123"
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["user"]["role_id"] == "CLAIMS_OFFICER"

    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Profile check
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "claims.officer@insurance.com"

    # Invalid password
    bad_resp = client.post("/api/auth/login", json={
        "email": "claims.officer@insurance.com",
        "password": "wrongpassword"
    })
    assert bad_resp.status_code == 401


def test_customers_endpoints():
    """Tests customer directory search, creation, and 360-degree risk view."""
    # List/search
    search_resp = client.get("/api/customers?limit=10")
    assert search_resp.status_code == 200
    customers = search_resp.json()
    assert len(customers) > 0
    first_id = customers[0]["claimant_id"]

    # Customer 360
    c360_resp = client.get(f"/api/customers/{first_id}")
    assert c360_resp.status_code == 200
    data = c360_resp.json()
    assert "customer" in data
    assert "policies" in data
    assert "claims" in data
    assert "total_claims_count" in data


def test_policies_endpoints():
    """Tests policy listing and automated underwriting coverage verification."""
    # List policies
    pol_resp = client.get("/api/policies?limit=5")
    assert pol_resp.status_code == 200
    policies = pol_resp.json()
    assert len(policies) > 0
    pid = policies[0]["policy_id"]

    # Coverage verification
    verify_resp = client.post("/api/policies/verify", json={
        "policy_id": pid,
        "incident_date": "2023-05-15",
        "claim_amount": 25000.0
    })
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["policy_id"] == pid
    assert "is_valid" in v_data
    assert "coverage_amount" in v_data


def test_providers_endpoints():
    """Tests provider directory and collusion network metrics."""
    resp = client.get("/api/providers?limit=5")
    assert resp.status_code == 200
    provs = resp.json()
    assert len(provs) > 0
    prv_id = provs[0]["provider_id"]

    profile_resp = client.get(f"/api/providers/{prv_id}")
    assert profile_resp.status_code == 200
    p_data = profile_resp.json()
    assert "provider" in p_data
    assert "total_claims" in p_data
    assert "total_invoiced_amount" in p_data


def test_claim_creation_and_fraud_analysis():
    """
    Tests end-to-end operational claim lifecycle:
    Creation -> Submission -> Multi-signal Automated Analysis -> Human Decision.
    """
    # 1. Create Claim
    create_resp = client.post("/claims", json={
        "claimant_id": "CLT0001",
        "policy_id": "POL0001",
        "vehicle_id": "VEH0001",
        "provider_id": "PRV001",
        "claim_date": "2023-06-20",
        "claim_amount": 48500.0,
        "claim_type": "Accident",
        "description": "Front collision on highway",
        "severity": "Medium"
    })
    assert create_resp.status_code == 201
    claim = create_resp.json()
    claim_id = claim["claim_id"]
    assert claim_id.startswith("CLM")
    assert claim["status"] in ("Open", "Submitted")

    try:
        # 2. Run Automated Fraud Analysis Pipeline
        analyze_resp = client.post(f"/claims/{claim_id}/analyze")
        assert analyze_resp.status_code == 200
        analysis = analyze_resp.json()
        assert analysis["claim_id"] == claim_id
        assert "final_risk_score" in analysis
        assert "risk_band" in analysis
        assert "sub_signals" in analysis
        assert "fraud_probability" in analysis["sub_signals"]
        assert "anomaly_score" in analysis["sub_signals"]
        assert "duplicate_similarity" in analysis["sub_signals"]
        assert "graph_risk_score" in analysis["sub_signals"]
        assert "shap_attributions" in analysis

        # 3. Fetch Full Analysis Dossier
        dossier_resp = client.get(f"/claims/{claim_id}/analysis")
        assert dossier_resp.status_code == 200
        dossier = dossier_resp.json()
        assert "claim" in dossier
        assert "risk" in dossier
        assert "explanation" in dossier

        # 4. Human Officer Decision
        dec_resp = client.post(f"/claims/{claim_id}/decision", json={
            "decision": "Approve",
            "reason": "Vehicle damage inspected and verified consistent with police report."
        })
        assert dec_resp.status_code == 200
        dec_data = dec_resp.json()
        assert dec_data["decision"] == "Approve"
        assert dec_data["status"] == "Approved"
    finally:
        # Clean up created claim so legacy tests expecting exactly 320 rows pass
        from api.db import db
        db.execute("DELETE FROM case_events WHERE case_id = ?", (f"CASE-{claim_id}",))
        db.execute("DELETE FROM investigation_cases WHERE claim_id = ?", (claim_id,))
        db.execute("DELETE FROM risk_scores WHERE claim_id = ?", (claim_id,))
        db.execute("DELETE FROM claims WHERE claim_id = ?", (claim_id,))


def test_reports_and_audit_logs():
    """Tests investigation report compilation and chronological audit trail querying."""
    # Reports
    rep_resp = client.get("/api/reports/claim/CLM00001")
    assert rep_resp.status_code == 200
    report = rep_resp.json()
    assert "report_id" in report
    assert "claim" in report
    assert "risk_assessment" in report
    assert "audit_timeline" in report

    # Audit logs
    audit_resp = client.get("/api/audit-logs?limit=20")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert isinstance(logs, list)
