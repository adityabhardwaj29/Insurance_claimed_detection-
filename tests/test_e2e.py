"""
tests/test_e2e.py
-----------------
Phase 13: End-to-End System Integration Test Suite.
Validates:
- Complete single-claim journey through all 9 subsystems
- Existence and non-empty status of all pipeline artifacts
- Consistency across Relational DB, Feature Store, Models, API, and Dashboard
- Human-in-the-loop audit trail preservation
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import app
from dashboard.utils.data_loader import compute_executive_kpis, load_all_claims_data
from src.pipeline import verify_claim_journey

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "fraud_detection.db"
FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"

client = TestClient(app)


class TestEndToEndSystemIntegration:
    """Comprehensive end-to-end integration tests."""

    def test_complete_claim_journey_high_risk(self):
        """Traces and validates high-risk claim CLM00001 across all 9 stages."""
        journey = verify_claim_journey("CLM00001", verbose=False)

        assert journey["verified"] is True
        stages = journey["stages"]

        # Stage 1: Relational Facts
        assert stages["1_relational_facts"]["claim_id"] == "CLM00001"
        assert stages["1_relational_facts"]["amount"] > 0
        assert stages["1_relational_facts"]["ground_truth_fraud"] == "YES (Fraud)"

        # Stage 2: Feature Engineering
        assert stages["2_features"]["features_available"] is True
        assert stages["2_features"]["days_since_policy_start"] is not None

        # Stage 3: Supervised ML Prediction
        assert 0.0 <= stages["3_ml_prediction"]["fraud_probability"] <= 1.0
        assert stages["3_ml_prediction"]["model_name"] == "XGBoost"

        # Stage 4: Unsupervised Anomaly Score
        assert 0.0 <= stages["4_anomaly_score"]["anomaly_score"] <= 1.0

        # Stage 5: Duplicate Detection
        assert 0.0 <= stages["5_duplicate_detection"]["similarity_score"] <= 1.0
        assert stages["5_duplicate_detection"]["duplicate_type"] in ["EXACT_DUPLICATE", "POSSIBLE_DUPLICATE", "SIMILAR", "NO_MATCH"]

        # Stage 6: Graph Relationships
        assert stages["6_graph_relationships"]["claim_degree"] > 0
        assert 0.0 <= stages["6_graph_relationships"]["fraud_neighbor_ratio"] <= 1.0

        # Stage 7: Final Risk Engine
        assert 0.0 <= stages["7_final_risk"]["final_risk_score"] <= 1.0
        assert stages["7_final_risk"]["risk_band"] in ["CRITICAL", "HIGH"]

        # Stage 8: Explainability
        assert len(stages["8_explanation"]["top_positive_factors"]) > 0
        assert len(stages["8_explanation"]["summary"]) > 10

        # Stage 9: Investigation Case
        assert stages["9_investigation_case"]["case_id"] is not None

    def test_complete_claim_journey_low_risk(self):
        """Traces and validates typical low/medium-risk claim CLM00002."""
        journey = verify_claim_journey("CLM00002", verbose=False)

        assert journey["verified"] is True
        stages = journey["stages"]

        assert stages["1_relational_facts"]["claim_id"] == "CLM00002"
        assert stages["1_relational_facts"]["ground_truth_fraud"] == "NO (Legitimate)"
        assert stages["7_final_risk"]["risk_band"] in ["LOW", "MEDIUM"]

    def test_all_pipeline_artifacts_exist_and_populated(self):
        """Verifies that all 9 pipeline data, model, and report artifacts exist on disk."""
        # 1. Database
        assert DB_PATH.exists()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM claims")
            assert cur.fetchone()[0] == 320
            cur.execute("SELECT COUNT(*) FROM claimants")
            assert cur.fetchone()[0] >= 100
            cur.execute("SELECT COUNT(*) FROM providers")
            assert cur.fetchone()[0] >= 20
            cur.execute("SELECT COUNT(*) FROM policies")
            assert cur.fetchone()[0] >= 100
            cur.execute("SELECT COUNT(*) FROM vehicles")
            assert cur.fetchone()[0] >= 100

        # 2. Features CSVs
        for fname in [
            "claim_features.csv",
            "duplicate_features.csv",
            "anomaly_features.csv",
            "graph_features.csv",
            "final_claim_features.csv",
            "final_risk_scores.csv",
        ]:
            fpath = FEATURES_DIR / fname
            assert fpath.exists(), f"Feature file {fname} must exist"
            df = pd.read_csv(fpath)
            assert len(df) == 320, f"{fname} must have 320 claim records"

        # 3. Model Binaries
        assert (MODELS_DIR / "fraud_model" / "model.joblib").exists()
        assert (MODELS_DIR / "anomaly_model" / "isolation_forest.joblib").exists()
        assert (MODELS_DIR / "graph_enhanced_model" / "model.joblib").exists()

        # 4. Explainability JSON Cache
        exp_file = FEATURES_DIR / "claim_explanations.json"
        assert exp_file.exists()
        with open(exp_file, "r", encoding="utf-8") as f:
            exps = json.load(f)
        assert len(exps) == 320

    def test_api_integration_live_responses(self):
        """Verifies FastAPI service returns correct live calculations."""
        # Test claim detail
        r_claim = client.get("/claims/CLM00001")
        assert r_claim.status_code == 200
        assert r_claim.json()["claim_id"] == "CLM00001"

        # Test explanation
        r_exp = client.get("/claims/CLM00001/explanation")
        assert r_exp.status_code == 200
        data_exp = r_exp.json()
        assert data_exp["claim_id"] == "CLM00001"
        assert len(data_exp["top_factors"]) > 0
        assert "graph_explanation" in data_exp

        # Test live model inference
        r_pred = client.post("/predict", json={"claim_id": "CLM00001"})
        assert r_pred.status_code == 200
        assert 0.0 <= r_pred.json()["fraud_probability"] <= 1.0

        # Test summary endpoint
        r_sum = client.get("/dashboard/summary")
        assert r_sum.status_code == 200
        assert r_sum.json()["total_claims"] == 320
        assert r_sum.json()["fraud_rate_pct"] == 16.25

    def test_dashboard_data_loader_and_kpis(self):
        """Verifies Dashboard data loader computes exact ground-truth KPIs."""
        df = load_all_claims_data()
        assert len(df) == 320

        kpis = compute_executive_kpis(df)
        assert kpis["total_claims"] == 320
        assert kpis["fraud_rate"] == 16.25
        assert kpis["flagged_claims"] >= 20
        assert 0.20 <= kpis["average_risk_score"] <= 0.40
