"""
tests/test_duplicate.py
-----------------------
Comprehensive unit and integration tests for the Phase 3 duplicate detection module.

Covers:
  - Similarity functions: numeric, date, categorical, composite
  - Text similarity functions: token, Levenshtein, hybrid, TF-IDF
  - DuplicateDetector pair classification (EXACT, POSSIBLE, SIMILAR, NO_MATCH)
  - Duplicate features CSV validation (exact 320 rows, required columns, value ranges)
  - Candidate pairs CSV validation
  - Duplicate detection evaluation report verification
  - Integration with src.features.duplicate_features
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.duplicate.duplicate_detector import DuplicateDetector, load_claims_context
from src.duplicate.similarity import (
    categorical_similarity,
    composite_similarity,
    date_similarity,
    jaccard_similarity,
    numeric_similarity,
)
from src.duplicate.text_similarity import (
    hybrid_text_similarity,
    levenshtein_similarity,
    token_similarity,
)
from src.features.duplicate_features import create_duplicate_features

ROOT = Path(__file__).resolve().parent.parent
FEATURES_DIR = ROOT / "data" / "features"
REPORTS_DIR = ROOT / "reports"
RELATIONAL_DIR = ROOT / "data" / "relational"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Unit Tests: Similarity Functions
# ─────────────────────────────────────────────────────────────────────────────

def test_numeric_similarity_exact():
    assert numeric_similarity(100.0, 100.0) == 1.0
    assert numeric_similarity(0, 0) == 1.0


def test_numeric_similarity_difference():
    # 90 vs 100 -> diff 10, max 100 -> 0.90
    sim = numeric_similarity(90.0, 100.0)
    assert abs(sim - 0.90) < 1e-4


def test_numeric_similarity_symmetry():
    assert numeric_similarity(150, 200) == numeric_similarity(200, 150)


def test_numeric_similarity_none_handling():
    assert numeric_similarity(None, 100) == 0.0
    assert numeric_similarity(100, None) == 0.0
    assert numeric_similarity(float("nan"), 100) == 0.0


def test_date_similarity_exact():
    sim, diff = date_similarity("2026-03-15", "2026-03-15")
    assert sim == 1.0
    assert diff == 0


def test_date_similarity_decay():
    sim, diff = date_similarity("2026-03-01", "2026-03-31", max_days=60)
    assert diff == 30
    assert abs(sim - 0.50) < 0.01


def test_date_similarity_beyond_max():
    sim, diff = date_similarity("2026-01-01", "2026-06-01", max_days=60)
    assert diff > 60
    assert sim == 0.0


def test_date_similarity_invalid():
    sim, diff = date_similarity("invalid-date", "2026-03-15")
    assert sim == 0.0
    assert diff == 9999


def test_categorical_similarity_matches():
    assert categorical_similarity("Tata", "Tata") == 1.0
    assert categorical_similarity("mumbai", "MUMBAI") == 1.0
    assert categorical_similarity("M", "M") == 1.0


def test_categorical_similarity_mismatches():
    assert categorical_similarity("Tata", "Maruti") == 0.0
    assert categorical_similarity(None, "Mumbai") == 0.0
    assert categorical_similarity("nan", "Pune") == 0.0


def test_jaccard_similarity():
    assert jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard_similarity({"a", "b"}, {"b", "c"}) == 1.0 / 3.0
    assert jaccard_similarity({"a"}, {"b"}) == 0.0
    assert jaccard_similarity(set(), set()) == 1.0


def test_composite_similarity():
    components = {"a": 1.0, "b": 0.5, "c": 0.0}
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    # Expected: (1.0*0.5 + 0.5*0.3 + 0.0*0.2) / 1.0 = 0.65
    assert abs(composite_similarity(components, weights) - 0.65) < 1e-4


# ─────────────────────────────────────────────────────────────────────────────
# 2. Unit Tests: Text Similarity
# ─────────────────────────────────────────────────────────────────────────────

def test_levenshtein_similarity():
    assert levenshtein_similarity("Claim description 1", "Claim description 1") == 1.0
    # Minor difference
    sim = levenshtein_similarity("Accident near highway", "Accident near higway")
    assert sim > 0.90
    # Disjoint strings
    assert levenshtein_similarity("apple", "xyz") == 0.0
    assert levenshtein_similarity("apple", "zebra") < 0.25


def test_token_similarity():
    assert token_similarity("rear bumper dent", "rear bumper dent") == 1.0
    # Word order invariance
    assert token_similarity("front collision car", "car front collision") == 1.0
    # Partial token overlap
    sim = token_similarity("windshield glass scratch", "windshield glass replacement")
    assert 0.4 < sim < 0.8


def test_hybrid_text_similarity():
    sim = hybrid_text_similarity("windshield crack", "windshield crack")
    assert sim == 1.0
    sim_diff = hybrid_text_similarity("theft of vehicle", "fire in engine")
    assert sim_diff < 0.3


# ─────────────────────────────────────────────────────────────────────────────
# 3. Unit Tests: DuplicateDetector Pair Classification
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def detector():
    return DuplicateDetector()


def test_detector_exact_duplicate(detector):
    claim1 = {
        "claim_id": "CLM99901",
        "claimant_id": "CLT0001",
        "name": "Rajesh Sharma",
        "policy_id": "POL0001",
        "policy_type": "Comprehensive",
        "vehicle_id": "VEH0001",
        "registration_no": "MH01AB1234",
        "vehicle_type": "Sedan",
        "claim_date": "2026-03-10",
        "claim_amount": 75000,
        "city": "Mumbai",
        "claim_type": "Accident",
        "description": "Front bumper and headlight damaged in collision",
        "invoice_id": "INV0001",
        "provider_id": "PRV001",
    }
    # Identical twin claim (injected exact duplicate test case)
    claim2 = dict(claim1)
    claim2["claim_id"] = "CLM99902"

    res = detector.compare_claims(claim1, claim2)
    assert res["duplicate_type"] == "EXACT_DUPLICATE"
    assert res["duplicate_flag"] == 1
    assert res["similarity_score"] >= 0.98
    assert "claimant_id" in res["matching_fields"]
    assert "vehicle_id" in res["matching_fields"]
    assert "policy_id" in res["matching_fields"]
    assert "exact_date" in res["matching_fields"]


def test_detector_possible_duplicate(detector):
    # Same vehicle, close date (3 days later), different claim_id
    claim1 = {
        "claim_id": "CLM99911",
        "claimant_id": "CLT0002",
        "name": "Amit Patel",
        "policy_id": "POL0002",
        "policy_type": "Comprehensive",
        "vehicle_id": "VEH0002",
        "registration_no": "MH02CD5678",
        "vehicle_type": "SUV",
        "claim_date": "2026-04-01",
        "claim_amount": 50000,
        "city": "Ahmedabad",
        "claim_type": "Accident",
        "description": "Rear bumper damage",
        "invoice_id": "INV0010",
        "provider_id": "PRV002",
    }
    claim2 = {
        "claim_id": "CLM99912",
        "claimant_id": "CLT0002",
        "name": "Amit Patel",
        "policy_id": "POL0003",
        "policy_type": "Comprehensive",
        "vehicle_id": "VEH0002",  # Same vehicle!
        "registration_no": "MH02CD5678",
        "vehicle_type": "SUV",
        "claim_date": "2026-04-04",  # 3 days later!
        "claim_amount": 52000,
        "city": "Ahmedabad",
        "claim_type": "Accident",
        "description": "Rear bumper and tailgate damage",
        "invoice_id": "INV0011",
        "provider_id": "PRV002",
    }
    res = detector.compare_claims(claim1, claim2)
    assert res["duplicate_type"] == "POSSIBLE_DUPLICATE"
    assert res["duplicate_flag"] == 1


def test_detector_similar_shared_invoice(detector):
    # Different claimants and vehicles, but same invoice_id
    claim1 = {
        "claim_id": "CLM99921",
        "claimant_id": "CLT0010",
        "name": "Suresh Gupta",
        "policy_id": "POL0010",
        "policy_type": "Comprehensive",
        "vehicle_id": "VEH0010",
        "registration_no": "MH03EF9012",
        "vehicle_type": "Hatchback",
        "claim_date": "2026-02-15",
        "claim_amount": 40000,
        "city": "Pune",
        "claim_type": "Theft",
        "description": "Side mirror stolen",
        "invoice_id": "INV0099",  # Shared invoice
        "provider_id": "PRV005",
    }
    claim2 = {
        "claim_id": "CLM99922",
        "claimant_id": "CLT0020",
        "name": "Vikas Rao",
        "policy_id": "POL0020",
        "policy_type": "Third Party",
        "vehicle_id": "VEH0020",
        "registration_no": "MH04GH3456",
        "vehicle_type": "Sedan",
        "claim_date": "2026-05-10",
        "claim_amount": 85000,
        "city": "Mumbai",
        "claim_type": "Glass Damage",
        "description": "Windshield broken",
        "invoice_id": "INV0099",  # Shared invoice
        "provider_id": "PRV005",
    }
    res = detector.compare_claims(claim1, claim2)
    assert res["duplicate_type"] == "SIMILAR"
    assert res["duplicate_flag"] == 1
    assert "invoice_id" in res["matching_fields"]


def test_detector_no_match(detector):
    # Completely disjoint claims
    claim1 = {
        "claim_id": "CLM99931",
        "claimant_id": "CLT0001",
        "name": "Arun Verma",
        "policy_id": "POL0001",
        "policy_type": "Comprehensive",
        "vehicle_id": "VEH0001",
        "registration_no": "MH01AA1111",
        "vehicle_type": "Sedan",
        "claim_date": "2026-01-01",
        "claim_amount": 20000,
        "city": "Delhi",
        "claim_type": "Fire",
        "description": "Engine fire",
        "invoice_id": "INV0001",
        "provider_id": "PRV001",
    }
    claim2 = {
        "claim_id": "CLM99932",
        "claimant_id": "CLT0099",
        "name": "Priya Nair",
        "policy_id": "POL0099",
        "policy_type": "Zero Dep",
        "vehicle_id": "VEH0099",
        "registration_no": "MH02BB2222",
        "vehicle_type": "SUV",
        "claim_date": "2026-08-01",
        "claim_amount": 200000,
        "city": "Surat",
        "claim_type": "Natural Disaster",
        "description": "Flood damage",
        "invoice_id": "INV0099",
        "provider_id": "PRV020",
    }
    claim2["invoice_id"] = "INV0199"  # distinct invoice
    res = detector.compare_claims(claim1, claim2)
    assert res["duplicate_type"] == "NO_MATCH"
    assert res["duplicate_flag"] == 0
    assert res["similarity_score"] < 0.40


# ─────────────────────────────────────────────────────────────────────────────
# 4. Integration Tests: Generated CSV Files and Reports
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def duplicate_features_df():
    path = FEATURES_DIR / "duplicate_features.csv"
    assert path.exists(), "duplicate_features.csv not found. Run detector pipeline first."
    return pd.read_csv(path)


@pytest.fixture
def duplicate_pairs_df():
    path = FEATURES_DIR / "duplicate_pairs.csv"
    assert path.exists(), "duplicate_pairs.csv not found. Run detector pipeline first."
    return pd.read_csv(path)


@pytest.fixture
def claims_df():
    return pd.read_csv(RELATIONAL_DIR / "claims.csv")


def test_duplicate_features_row_count(duplicate_features_df, claims_df):
    """Must cover 100% of claims (320 rows)."""
    assert len(duplicate_features_df) == len(claims_df) == 320


def test_duplicate_features_required_columns(duplicate_features_df):
    required_cols = [
        "claim_id",
        "compared_claim_id",
        "similarity_score",
        "duplicate_type",
        "matching_fields",
        "duplicate_flag",
    ]
    for col in required_cols:
        assert col in duplicate_features_df.columns, f"Missing required column: {col}"


def test_duplicate_features_pks_unique(duplicate_features_df):
    assert duplicate_features_df["claim_id"].is_unique


def test_duplicate_features_no_self_comparison(duplicate_features_df):
    """A claim must never be compared to itself."""
    self_matches = duplicate_features_df[
        duplicate_features_df["claim_id"] == duplicate_features_df["compared_claim_id"]
    ]
    assert len(self_matches) == 0, f"Found self-comparisons: {self_matches}"


def test_duplicate_features_similarity_score_range(duplicate_features_df):
    scores = duplicate_features_df["similarity_score"]
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


def test_duplicate_features_duplicate_types(duplicate_features_df):
    valid_types = {"EXACT_DUPLICATE", "POSSIBLE_DUPLICATE", "SIMILAR", "NO_MATCH"}
    actual_types = set(duplicate_features_df["duplicate_type"].unique())
    assert actual_types.issubset(valid_types)


def test_duplicate_features_flag_binary(duplicate_features_df):
    flags = set(duplicate_features_df["duplicate_flag"].unique())
    assert flags.issubset({0, 1})


def test_duplicate_pairs_validity(duplicate_pairs_df):
    assert not duplicate_pairs_df.empty
    assert "claim_id_1" in duplicate_pairs_df.columns
    assert "claim_id_2" in duplicate_pairs_df.columns
    assert "similarity_score" in duplicate_pairs_df.columns
    # Check no self pairs
    assert (duplicate_pairs_df["claim_id_1"] != duplicate_pairs_df["claim_id_2"]).all()


def test_evaluation_report_exists_and_valid():
    report_path = REPORTS_DIR / "duplicate_detection_report.json"
    assert report_path.exists(), "duplicate_detection_report.json not found"
    with open(report_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_claims_scored"] == 320
    assert "duplicate_type_distribution" in data
    assert "fraud_rates_by_type" in data
    assert "statistics" in data
    assert data["statistics"]["mean_similarity_score"] > 0.0


def test_features_pipeline_integration():
    """Test that src.features.duplicate_features loads or generates correctly."""
    df = create_duplicate_features()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 320
    assert "similarity_score" in df.columns
    assert "duplicate_type" in df.columns
