"""
tests/test_features.py
-----------------------
Unit and validation test suite for Claim Feature Engineering (src/features/claim_features.py).
Verifies:
  - Feature table schema and row count (320 rows)
  - Zero null values in computed features
  - Financial ratios validity (positive amounts, non-negative days)
  - Strict temporal causality of cumulative frequencies (no future data leakage)
  - Target leakage prevention (no trivial correlation or leakage from fraud_label)
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.claim_features import build_claim_features, create_claim_features

FEATURES_CSV = ROOT / "data" / "features" / "claim_features.csv"


@pytest.fixture(scope="module")
def claim_features_df() -> pd.DataFrame:
    if FEATURES_CSV.exists():
        return pd.read_csv(FEATURES_CSV)
    return build_claim_features()


def test_claim_features_file_exists():
    assert FEATURES_CSV.exists(), f"Feature file {FEATURES_CSV} must exist on disk"


def test_claim_features_row_count(claim_features_df):
    assert len(claim_features_df) == 320, f"Expected 320 claims, got {len(claim_features_df)}"


def test_claim_features_schema(claim_features_df):
    expected_cols = [
        "claim_id",
        "claim_date",
        "claim_amount",
        "claim_age_days",
        "days_since_policy_start",
        "amount_to_premium_ratio",
        "invoice_to_claim_ratio",
        "claimant_claim_frequency",
        "provider_claim_volume",
        "vehicle_age",
        "claimant_age",
        "provider_rating",
        "duplicate_similarity_score",
        "duplicate_flag",
        "claim_type",
        "policy_type",
        "vehicle_type",
        "vehicle_make",
        "provider_type",
        "claimant_city",
        "fraud_label",
    ]
    for col in expected_cols:
        assert col in claim_features_df.columns, f"Missing expected column: {col}"


def test_claim_features_no_nulls(claim_features_df):
    null_counts = claim_features_df.isnull().sum()
    assert null_counts.sum() == 0, f"Columns contain nulls: {null_counts[null_counts > 0].to_dict()}"


def test_claim_features_claim_ids_unique(claim_features_df):
    assert claim_features_df["claim_id"].nunique() == len(claim_features_df), "Claim IDs must be unique"


def test_claim_amount_positive(claim_features_df):
    assert (claim_features_df["claim_amount"] > 0).all(), "All claim amounts must be strictly positive"


def test_ratios_non_negative(claim_features_df):
    assert (claim_features_df["amount_to_premium_ratio"] >= 0).all(), "amount_to_premium_ratio must be >= 0"
    assert (claim_features_df["invoice_to_claim_ratio"] >= 0).all(), "invoice_to_claim_ratio must be >= 0"


def test_days_since_policy_start_non_negative(claim_features_df):
    assert (claim_features_df["days_since_policy_start"] >= 0).all(), "days_since_policy_start must be >= 0"


def test_vehicle_age_valid_range(claim_features_df):
    assert (claim_features_df["vehicle_age"] >= 0).all(), "vehicle_age must be >= 0"
    assert (claim_features_df["vehicle_age"] <= 40).all(), "vehicle_age exceeds realistic vehicle lifetime"


def test_provider_rating_range(claim_features_df):
    assert (claim_features_df["provider_rating"] >= 1.0).all(), "provider_rating must be >= 1.0"
    assert (claim_features_df["provider_rating"] <= 5.0).all(), "provider_rating must be <= 5.0"


def test_duplicate_similarity_score_range(claim_features_df):
    assert (claim_features_df["duplicate_similarity_score"] >= 0.0).all()
    assert (claim_features_df["duplicate_similarity_score"] <= 1.0).all()


def test_duplicate_flag_binary(claim_features_df):
    unique_flags = set(claim_features_df["duplicate_flag"].unique())
    assert unique_flags.issubset({0, 1}), f"duplicate_flag must be 0 or 1, got {unique_flags}"


def test_temporal_causality_claimant_frequency():
    """
    Verifies that claimant_claim_frequency is causal and cumulative:
    claims filed earlier in time have smaller or equal cumulative frequency compared
    to claims filed later by the same claimant.
    """
    df = pd.read_csv(FEATURES_CSV)
    df["_dt"] = pd.to_datetime(df["claim_date"])
    claims_raw = pd.read_csv(ROOT / "data" / "relational" / "claims.csv")
    merged = df.merge(claims_raw[["claim_id", "claimant_id"]], on="claim_id")

    for claimant_id, group in merged.groupby("claimant_id"):
        if len(group) > 1:
            group_sorted = group.sort_values("_dt")
            freqs = group_sorted["claimant_claim_frequency"].tolist()
            # Cumulative frequency must be non-decreasing over time
            assert freqs == sorted(freqs), f"Claimant {claimant_id} frequencies not non-decreasing over time: {freqs}"


def test_no_target_leakage_in_features(claim_features_df):
    """
    Verifies that no derived feature is trivially identical to fraud_label or has perfect correlation.
    """
    numeric_features = [
        "claim_amount",
        "claim_age_days",
        "days_since_policy_start",
        "amount_to_premium_ratio",
        "invoice_to_claim_ratio",
        "claimant_claim_frequency",
        "provider_claim_volume",
        "vehicle_age",
        "claimant_age",
        "provider_rating",
        "duplicate_similarity_score",
        "duplicate_flag",
    ]
    for feat in numeric_features:
        corr = claim_features_df[feat].corr(claim_features_df["fraud_label"])
        assert not np.isnan(corr), f"Correlation of {feat} with fraud_label is NaN"
        # No single feature should have correlation >= 0.90 (which would indicate trivial target leakage)
        assert abs(corr) < 0.90, f"Potential target leakage: {feat} has correlation {corr:.4f} with fraud_label"


def test_build_claim_features_function_returns_dataframe():
    df = build_claim_features()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 320


def test_create_claim_features_wrapper():
    df = create_claim_features()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 320
