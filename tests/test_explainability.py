"""
tests/test_explainability.py
----------------------------
Unit and integration test suite for Phase 12 Explainable Fraud Detection.
Validates:
- SHAP TreeExplainer calculation on supervised XGBoost pipeline
- Directional factor separation (risk_increasing vs risk_decreasing)
- Graph topological evidence extraction (suspicious connections, high degree hubs, repeated links, flagged neighbors)
- Unified ClaimExplainer JSON schema conformity
- Precomputed batch explanations dataset integrity across all 320 claims
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import pandas as pd

from src.explainability.shap_explainer import ShapExplainer
from src.explainability.graph_explainer import GraphExplainer
from src.explainability.claim_explainer import ClaimExplainer, explain_claim

ROOT = Path(__file__).resolve().parents[1]
EXPLANATIONS_JSON = ROOT / "data" / "features" / "claim_explanations.json"


class TestShapExplainer:
    """Tests local and global SHAP computation."""

    @pytest.fixture
    def explainer(self):
        return ShapExplainer()

    def test_explainer_initialization(self, explainer):
        assert explainer.pipeline is not None
        assert len(explainer.feature_names_in) == 18
        assert len(explainer.transformed_names) == 38
        assert explainer.explainer is not None

    def test_explain_instance_structure_and_bounds(self, explainer):
        sample_row = {
            "claim_id": "CLM00001",
            "claim_amount": 132760.0,
            "claim_age_days": 15,
            "days_since_policy_start": 6,
            "amount_to_premium_ratio": 1.88,
            "invoice_to_claim_ratio": 1.0,
            "claimant_claim_frequency": 1,
            "provider_claim_volume": 2,
            "vehicle_age": 8,
            "claimant_age": 50,
            "provider_rating": 4.1,
            "duplicate_similarity_score": 0.49,
            "duplicate_flag": 0,
            "claim_type": "Theft",
            "policy_type": "Third Party",
            "vehicle_type": "Sedan",
            "vehicle_make": "Tata",
            "provider_type": "Dealer",
            "claimant_city": "Ahmedabad",
        }

        res = explainer.explain_instance(sample_row, top_k=5, claim_id="CLM00001")

        assert res["claim_id"] == "CLM00001"
        assert 0.0 <= res["fraud_probability"] <= 1.0
        assert "base_value" in res
        assert len(res["top_factors"]) <= 5
        assert len(res["top_positive_factors"]) <= 5
        assert len(res["top_negative_factors"]) <= 5

        # Validate factor schema
        for f in res["top_factors"]:
            assert "feature" in f
            assert "impact" in f
            assert f["direction"] in ["risk_increasing", "risk_decreasing"]
            if f["direction"] == "risk_increasing":
                assert f["impact"] > 0
            else:
                assert f["impact"] < 0

        # Validate positive factors are strictly positive
        for pf in res["top_positive_factors"]:
            assert pf["direction"] == "risk_increasing"
            assert pf["impact"] > 0

        # Validate negative factors are strictly negative
        for nf in res["top_negative_factors"]:
            assert nf["direction"] == "risk_decreasing"
            assert nf["impact"] < 0


class TestGraphExplainer:
    """Tests graph evidence extraction from topological artifacts."""

    @pytest.fixture
    def graph_explainer(self):
        return GraphExplainer()

    def test_explain_claim_graph_known_claim(self, graph_explainer):
        res = graph_explainer.explain_claim_graph("CLM00001")

        assert res["claim_id"] == "CLM00001"
        assert "suspicious_connections" in res
        assert "high_degree_entities" in res
        assert "repeated_relationships" in res
        assert "neighboring_flagged_claims" in res

        # Check that high degree entities include expected entity types if present
        for h in res["high_degree_entities"]:
            assert h["entity_type"] in ["Provider", "Claimant", "Vehicle", "Location"]
            assert h["degree"] > 0

        # Check neighboring flagged claims formatting
        for nc in res["neighboring_flagged_claims"]:
            assert "claim_id" in nc
            assert "shared_relationship" in nc
            assert "confirmed_fraud" in nc
            assert "final_risk_score" in nc

    def test_explain_claim_graph_nonexistent(self, graph_explainer):
        res = graph_explainer.explain_claim_graph("NON_EXISTENT_CLAIM_999")
        assert res["claim_id"] == "NON_EXISTENT_CLAIM_999"
        assert len(res["suspicious_connections"]) == 0
        assert len(res["high_degree_entities"]) == 0
        assert len(res["neighboring_flagged_claims"]) == 0


class TestClaimExplainer:
    """Tests unified multimodal explainer and narrative synthesis."""

    def test_explain_claim_unified_schema(self):
        exp = explain_claim("CLM00001")

        # Required fields check
        assert exp["claim_id"] == "CLM00001"
        assert "fraud_probability" in exp
        assert "top_factors" in exp
        assert "top_positive_factors" in exp
        assert "top_negative_factors" in exp
        assert "graph_explanation" in exp
        assert "summary_text" in exp

        # Narrative text contains relevant keywords
        assert len(exp["summary_text"]) > 20
        assert "CLM00001" not in exp["summary_text"] or "Claim" in exp["summary_text"]

    def test_precomputed_batch_explanations_file(self):
        assert EXPLANATIONS_JSON.exists(), "Precomputed claim_explanations.json must exist"

        with open(EXPLANATIONS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Dataset has 320 claims
        assert len(data) == 320
        assert "CLM00001" in data
        assert "CLM00320" in data

        # Check random claim integrity
        for cid in ["CLM00001", "CLM00050", "CLM00100"]:
            entry = data[cid]
            assert entry["claim_id"] == cid
            assert 0.0 <= entry["fraud_probability"] <= 1.0
            assert isinstance(entry["top_factors"], list)
            assert "graph_explanation" in entry
