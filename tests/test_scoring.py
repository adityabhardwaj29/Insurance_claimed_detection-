"""
Phase 8 tests: Hybrid Fraud Risk Engine.
Verifies scoring, risk bands, reason generation, determinism, and data integrity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import pytest

from src.scoring.thresholds import (
    ComponentWeights,
    NormalizationParams,
    ReasonThresholds,
    RiskBands,
    DEFAULT_WEIGHTS,
    DEFAULT_RISK_BANDS,
    DEFAULT_REASON_THRESHOLDS,
    DEFAULT_NORMALIZATION,
)
from src.scoring.risk_reasons import (
    generate_reasons,
    reasons_to_messages,
    reasons_to_string,
    REASON_CATALOG,
    _safe_float,
    _safe_int,
)
from src.scoring.risk_engine import (
    compute_graph_risk_score,
    compute_duplicate_score,
    compute_risk_scores,
    _minmax_clip,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def risk_scores_df():
    path = Path("data/features/final_risk_scores.csv")
    assert path.exists(), "final_risk_scores.csv must exist"
    return pd.read_csv(path, keep_default_na=False)


@pytest.fixture(scope="module")
def final_features_df():
    return pd.read_csv("data/features/final_claim_features.csv")


# ── 1. Thresholds configuration ───────────────────────────────────────────────


def test_weights_sum_to_one():
    w = DEFAULT_WEIGHTS
    total = (w.fraud_probability + w.anomaly_score
             + w.duplicate_score + w.graph_risk_score)
    assert abs(total - 1.0) < 1e-9


def test_invalid_weights_raise():
    with pytest.raises(ValueError, match="sum to 1.0"):
        ComponentWeights(
            fraud_probability=0.5,
            anomaly_score=0.5,
            duplicate_score=0.5,
            graph_risk_score=0.5,
        )


def test_risk_bands_classify():
    bands = RiskBands()
    assert bands.classify(0.80) == "CRITICAL"
    assert bands.classify(0.75) == "CRITICAL"
    assert bands.classify(0.74) == "HIGH"
    assert bands.classify(0.55) == "HIGH"
    assert bands.classify(0.54) == "MEDIUM"
    assert bands.classify(0.35) == "MEDIUM"
    assert bands.classify(0.34) == "LOW"
    assert bands.classify(0.00) == "LOW"


def test_risk_bands_configurable():
    custom = RiskBands(CRITICAL=0.90, HIGH=0.70, MEDIUM=0.50)
    assert custom.classify(0.89) == "HIGH"
    assert custom.classify(0.91) == "CRITICAL"


# ── 2. minmax normalisation ──────────────────────────────────────────────────


def test_minmax_clip_midpoint():
    assert _minmax_clip(15.0, 7.0, 25.0) == pytest.approx(0.4444, abs=0.001)


def test_minmax_clip_bounds():
    assert _minmax_clip(7.0, 7.0, 25.0) == pytest.approx(0.0)
    assert _minmax_clip(25.0, 7.0, 25.0) == pytest.approx(1.0)


def test_minmax_clip_clamped():
    assert _minmax_clip(-5.0, 0.0, 1.0) == pytest.approx(0.0)
    assert _minmax_clip(5.0, 0.0, 1.0) == pytest.approx(1.0)


def test_minmax_clip_degenerate():
    assert _minmax_clip(5.0, 5.0, 5.0) == 0.0  # lo == hi → 0


# ── 3. Component score functions ─────────────────────────────────────────────


def test_graph_risk_score_range():
    norm = DEFAULT_NORMALIZATION
    row = {
        "fraud_neighbor_ratio": 0.5,
        "claimant_degree": 7.0,
        "provider_claim_count": 15.0,
        "repeated_claimant_provider": 1,
        "suspicious_neighbor_count": 3.0,
    }
    score = compute_graph_risk_score(row, norm)
    assert 0.0 <= score <= 1.0


def test_graph_risk_score_zero_risk():
    norm = DEFAULT_NORMALIZATION
    row = {
        "fraud_neighbor_ratio": 0.0,
        "claimant_degree": 2.0,  # minimum
        "provider_claim_count": 7.0,  # minimum
        "repeated_claimant_provider": 0,
        "suspicious_neighbor_count": 0.0,
    }
    score = compute_graph_risk_score(row, norm)
    assert score == pytest.approx(0.0, abs=0.01)


def test_graph_risk_score_max_risk():
    norm = DEFAULT_NORMALIZATION
    row = {
        "fraud_neighbor_ratio": 1.0,
        "claimant_degree": 11.0,  # maximum
        "provider_claim_count": 25.0,  # maximum
        "repeated_claimant_provider": 1,
        "suspicious_neighbor_count": 6.0,  # maximum
    }
    score = compute_graph_risk_score(row, norm)
    assert score == pytest.approx(1.0, abs=0.01)


def test_duplicate_score_normalised():
    norm = DEFAULT_NORMALIZATION
    # At minimum similarity -> 0
    score_min = compute_duplicate_score({"dup_similarity_score": norm.DUP_SCORE_MIN}, norm)
    assert score_min == pytest.approx(0.0)
    # At maximum similarity -> 1
    score_max = compute_duplicate_score({"dup_similarity_score": norm.DUP_SCORE_MAX}, norm)
    assert score_max == pytest.approx(1.0)


def test_duplicate_score_fallback_key():
    norm = DEFAULT_NORMALIZATION
    # Falls back to duplicate_similarity_score
    score = compute_duplicate_score({"duplicate_similarity_score": 0.50}, norm)
    assert 0.0 <= score <= 1.0


def test_duplicate_score_missing():
    score = compute_duplicate_score({}, DEFAULT_NORMALIZATION)
    assert score == 0.0


# ── 4. Risk reason generation ─────────────────────────────────────────────────


def test_no_reasons_for_low_risk():
    row: Dict[str, Any] = {
        "fraud_probability": 0.10,
        "anomaly_score": 0.10,
        "anomaly_flag": 0,
        "dup_similarity_score": 0.35,
        "dup_type": "NO_MATCH",
        "claim_amount": 10_000.0,
        "amount_to_premium_ratio": 1.0,
        "claimant_degree": 3,
        "provider_claim_count": 8,
        "provider_claim_volume": 3,
        "fraud_neighbor_count": 0,
        "fraud_neighbor_ratio": 0.0,
        "repeated_claimant_provider": 0,
        "suspicious_neighbor_count": 0,
        "claimant_claim_frequency": 1,
    }
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert reasons == []


def test_high_fraud_prob_reason():
    row = {"fraud_probability": 0.85}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "HIGH_FRAUD_PROBABILITY" in reasons


def test_anomaly_flagged_reason():
    row = {"anomaly_flag": 1, "fraud_probability": 0.1}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "ANOMALY_FLAGGED" in reasons


def test_high_anomaly_score_reason():
    row = {"anomaly_score": 0.95, "fraud_probability": 0.1}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "HIGH_ANOMALY_SCORE" in reasons


def test_possible_duplicate_reason():
    row = {"dup_type": "POSSIBLE_DUPLICATE"}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "POSSIBLE_DUPLICATE_CLAIM" in reasons


def test_high_claim_amount_reason():
    row = {"claim_amount": 250_000.0}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "HIGH_CLAIM_AMOUNT" in reasons


def test_fraud_neighbor_reason():
    row = {"fraud_neighbor_count": 2, "fraud_neighbor_ratio": 0.5}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "FRAUD_NEIGHBOR_PRESENT" in reasons


def test_repeated_claimant_provider_reason():
    row = {"repeated_claimant_provider": 1}
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert "REPEATED_CLAIMANT_PROVIDER" in reasons


def test_reasons_deduplicated():
    """Same reason should not appear twice even if multiple triggers."""
    row = {
        "fraud_probability": 0.95,
        "anomaly_flag": 1,
        "anomaly_score": 0.9,
    }
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    assert len(reasons) == len(set(reasons))


def test_all_reason_codes_in_catalog():
    """Every generated reason code must exist in the REASON_CATALOG."""
    row = {
        "fraud_probability": 0.95,
        "anomaly_score": 0.9,
        "anomaly_flag": 1,
        "dup_similarity_score": 0.62,
        "dup_type": "POSSIBLE_DUPLICATE",
        "claim_amount": 250_000.0,
        "amount_to_premium_ratio": 9.0,
        "claimant_degree": 10,
        "provider_claim_count": 20,
        "provider_claim_volume": 15,
        "fraud_neighbor_count": 3,
        "fraud_neighbor_ratio": 0.75,
        "repeated_claimant_provider": 1,
        "suspicious_neighbor_count": 4,
        "claimant_claim_frequency": 5,
    }
    reasons = generate_reasons(row, DEFAULT_REASON_THRESHOLDS)
    for code in reasons:
        assert code in REASON_CATALOG, f"Reason code not in catalog: {code}"


def test_reasons_to_messages():
    msgs = reasons_to_messages(["HIGH_FRAUD_PROBABILITY"])
    assert len(msgs) == 1
    assert "fraud probability" in msgs[0].lower()


def test_reasons_to_string_empty():
    assert reasons_to_string([]) == ""


def test_reasons_to_string_nonempty():
    s = reasons_to_string(["HIGH_FRAUD_PROBABILITY", "ANOMALY_FLAGGED"])
    assert " | " in s


# ── 5. Safe conversion helpers ────────────────────────────────────────────────


def test_safe_float_nan():
    import math
    assert _safe_float(float("nan")) is None


def test_safe_float_string():
    assert _safe_float("abc") is None


def test_safe_float_valid():
    assert _safe_float("3.14") == pytest.approx(3.14)


def test_safe_int_rounds():
    assert _safe_int(2.7) == 3


# ── 6. Output CSV integrity ──────────────────────────────────────────────────


def test_risk_scores_schema(risk_scores_df):
    required = ["claim_id", "fraud_probability", "anomaly_score", "duplicate_score",
                "graph_risk_score", "final_risk_score", "risk_band", "risk_reasons"]
    for col in required:
        assert col in risk_scores_df.columns, f"Missing column: {col}"


def test_risk_scores_row_count(risk_scores_df):
    assert len(risk_scores_df) == 320


def test_risk_scores_no_nulls(risk_scores_df):
    null_counts = risk_scores_df.isnull().sum()
    assert null_counts.sum() == 0, f"Nulls found:\n{null_counts[null_counts > 0]}"


def test_final_risk_score_in_range(risk_scores_df):
    assert risk_scores_df["final_risk_score"].between(0.0, 1.0).all()


def test_fraud_probability_in_range(risk_scores_df):
    assert risk_scores_df["fraud_probability"].between(0.0, 1.0).all()


def test_anomaly_score_in_range(risk_scores_df):
    assert risk_scores_df["anomaly_score"].between(0.0, 1.0).all()


def test_duplicate_score_in_range(risk_scores_df):
    assert risk_scores_df["duplicate_score"].between(0.0, 1.0).all()


def test_graph_risk_score_in_range(risk_scores_df):
    assert risk_scores_df["graph_risk_score"].between(0.0, 1.0).all()


def test_risk_band_values(risk_scores_df):
    valid_bands = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    actual_bands = set(risk_scores_df["risk_band"].unique())
    assert actual_bands <= valid_bands, f"Invalid bands: {actual_bands - valid_bands}"


def test_risk_band_monotonic(risk_scores_df):
    """Claims with higher final_risk_score should have higher or equal risk bands."""
    band_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    bands = DEFAULT_RISK_BANDS
    for _, row in risk_scores_df.iterrows():
        expected = bands.classify(row["final_risk_score"])
        assert row["risk_band"] == expected, (
            f"claim {row['claim_id']}: score={row['final_risk_score']:.4f}, "
            f"expected {expected}, got {row['risk_band']}"
        )


def test_critical_claims_high_risk_score(risk_scores_df):
    critical = risk_scores_df[risk_scores_df["risk_band"] == "CRITICAL"]
    assert (critical["final_risk_score"] >= DEFAULT_RISK_BANDS.CRITICAL).all()


def test_low_claims_low_risk_score(risk_scores_df):
    low = risk_scores_df[risk_scores_df["risk_band"] == "LOW"]
    assert (low["final_risk_score"] < DEFAULT_RISK_BANDS.MEDIUM).all()


def test_fraud_label_correlation(risk_scores_df):
    """Fraud claims should have higher mean final_risk_score than non-fraud claims."""
    claims = pd.read_csv("data/relational/claims.csv")
    merged = claims[["claim_id", "fraud_label"]].merge(risk_scores_df, on="claim_id")
    mean_fraud = merged[merged["fraud_label"] == 1]["final_risk_score"].mean()
    mean_legit = merged[merged["fraud_label"] == 0]["final_risk_score"].mean()
    assert mean_fraud > mean_legit, (
        f"Fraud mean ({mean_fraud:.4f}) should exceed non-fraud mean ({mean_legit:.4f})"
    )


def test_risk_reasons_present_for_high_band(risk_scores_df):
    """HIGH and CRITICAL risk claims must always have at least one reason."""
    high_claims = risk_scores_df[risk_scores_df["risk_band"].isin(["HIGH", "CRITICAL"])]
    missing_reasons = high_claims[high_claims["risk_reasons"].str.len() == 0]
    assert len(missing_reasons) == 0, (
        f"{len(missing_reasons)} HIGH/CRITICAL claims have no risk reasons"
    )


# ── 7. Determinism ────────────────────────────────────────────────────────────


def test_risk_scores_deterministic(risk_scores_df, final_features_df):
    """Re-running compute_risk_scores() must produce identical final_risk_score values."""
    fresh = compute_risk_scores(
        feature_df=final_features_df,
        output_path=None,
    )
    fresh_sorted = fresh.sort_values("claim_id").reset_index(drop=True)
    saved_sorted = risk_scores_df.sort_values("claim_id").reset_index(drop=True)

    np.testing.assert_allclose(
        fresh_sorted["final_risk_score"].values,
        saved_sorted["final_risk_score"].values,
        rtol=1e-5,
        err_msg="final_risk_score values are not deterministic",
    )
    assert (fresh_sorted["risk_band"].values == saved_sorted["risk_band"].values).all()


# ── 8. Module API functions ───────────────────────────────────────────────────


def test_calculate_risk_score_function():
    from src.scoring.risk_score import calculate_risk_score

    score = calculate_risk_score(1.0, 1.0, 1.0, 1.0)
    assert score == 1.0

    score_zero = calculate_risk_score(0.0, 0.0, 0.0, 0.0)
    assert score_zero == 0.0

    # With default weights: 0.45*1 + 0.25*0 + 0.15*0 + 0.15*0 = 0.45
    score_ml = calculate_risk_score(1.0, 0.0, 0.0, 0.0)
    assert score_ml == 0.45


def test_priority_function():
    from src.scoring.priority import priority

    assert priority(0.85) == "CRITICAL"
    assert priority(0.65) == "HIGH"
    assert priority(0.45) == "MEDIUM"
    assert priority(0.15) == "LOW"

