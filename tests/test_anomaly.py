"""
tests/test_anomaly.py
---------------------
Comprehensive tests for Phase 5 Unsupervised Anomaly Detection.

Covers:
  - Feature extraction without target leakage
  - Score calibration mapping into [0.0, 1.0]
  - Isolation Forest, LOF, and One-Class SVM model building and consensus
  - Automated reason generation for anomalies
  - Output CSV validation (data/features/anomaly_features.csv)
  - Clear separation of fraud_probability and anomaly_score
  - Anomaly detection report verification
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

from src.models.anomaly.anomaly_detector import AnomalyDetector
from src.models.anomaly.features import ANOMALY_FEATURE_COLS, extract_anomaly_features
from src.models.anomaly.models import (
    build_isolation_forest,
    build_local_outlier_factor,
    build_one_class_svm,
    calibrate_anomaly_score,
)

FEATURES_DIR = ROOT / "data" / "features"
REPORTS_DIR = ROOT / "reports"
RELATIONAL_DIR = ROOT / "data" / "relational"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Feature Extraction Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_extract_anomaly_features_shape():
    features_df, raw_df = extract_anomaly_features()
    assert len(features_df) == 320
    assert len(raw_df) == 320
    assert "claim_id" in features_df.columns
    for col in ANOMALY_FEATURE_COLS:
        assert col in features_df.columns, f"Missing anomaly feature column: {col}"


def test_extract_anomaly_features_no_nan():
    features_df, _ = extract_anomaly_features()
    feature_matrix = features_df[ANOMALY_FEATURE_COLS]
    assert feature_matrix.isna().sum().sum() == 0, "Feature matrix contains unexpected NaNs"


def test_no_target_in_anomaly_features():
    features_df, _ = extract_anomaly_features()
    assert "fraud_label" not in features_df.columns, "Target label leaked into unsupervised feature matrix"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Calibration & Model Builder Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_calibrate_anomaly_score_inversion():
    # In scikit-learn anomaly detection, -1.0 is anomalous and +1.0 is normal.
    raw_scores = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
    calibrated = calibrate_anomaly_score(raw_scores, invert=True)

    # Inverted: -1.0 -> 1.0 (most anomalous), 1.0 -> 0.0 (least anomalous)
    assert calibrated[0] == 1.0
    assert calibrated[-1] == 0.0
    assert (calibrated >= 0.0).all() and (calibrated <= 1.0).all()
    # Monotonically decreasing
    assert (np.diff(calibrated) <= 0).all()


def test_model_builders():
    iso = build_isolation_forest()
    assert iso.contamination == 0.10

    lof = build_local_outlier_factor()
    assert lof.novelty is True

    ocsvm = build_one_class_svm()
    assert ocsvm.kernel == "rbf"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Anomaly Detector Engine & Reason Generation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_anomaly_detector_execution():
    features_df, _ = extract_anomaly_features()
    detector = AnomalyDetector(contamination=0.10, random_state=42)
    result_df = detector.fit_predict(features_df)

    assert len(result_df) == 320
    assert "claim_id" in result_df.columns
    assert "anomaly_score" in result_df.columns
    assert "anomaly_flag" in result_df.columns
    assert "anomaly_reason" in result_df.columns

    # Check score bounds
    scores = result_df["anomaly_score"]
    assert (scores >= 0.0).all() and (scores <= 1.0).all()

    # Check flag counts match contamination (10% of 320 = 32)
    flags = result_df["anomaly_flag"]
    assert flags.sum() == 32
    assert set(flags.unique()).issubset({0, 1})


def test_anomaly_reasons_populated():
    features_df, _ = extract_anomaly_features()
    detector = AnomalyDetector(contamination=0.10, random_state=42)
    result_df = detector.fit_predict(features_df)

    # Anomalous claims must have explanatory text
    anom_rows = result_df[result_df["anomaly_flag"] == 1]
    for _, r in anom_rows.iterrows():
        reason = r["anomaly_reason"]
        assert isinstance(reason, str) and len(reason.strip()) > 5
        assert "Normal range" not in reason, f"Anomalous claim {r['claim_id']} labeled as Normal range"

    # Non-anomalous claims have default text
    normal_rows = result_df[result_df["anomaly_flag"] == 0]
    assert (normal_rows["anomaly_reason"].str.len() > 0).all()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Artifact & CSV Validation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_anomaly_features_csv_exists_and_valid():
    csv_path = FEATURES_DIR / "anomaly_features.csv"
    assert csv_path.exists(), "anomaly_features.csv not found"

    df = pd.read_csv(csv_path)
    assert len(df) == 320
    required_cols = ["claim_id", "anomaly_score", "anomaly_flag", "anomaly_reason"]
    for col in required_cols:
        assert col in df.columns, f"Required column missing from CSV: {col}"

    assert df["claim_id"].is_unique
    assert (df["anomaly_score"] >= 0.0).all() and (df["anomaly_score"] <= 1.0).all()
    assert set(df["anomaly_flag"].unique()).issubset({0, 1})


def test_separation_of_anomaly_and_fraud_signals():
    """
    Ensure fraud_probability is NOT present in anomaly_features.csv,
    confirming the two signals remain independent.
    """
    csv_path = FEATURES_DIR / "anomaly_features.csv"
    df = pd.read_csv(csv_path)
    assert "fraud_probability" not in df.columns
    assert "fraud_label" not in df.columns


def test_anomaly_report_exists_and_valid():
    report_path = REPORTS_DIR / "anomaly_detection_report.json"
    assert report_path.exists(), "anomaly_detection_report.json not found"

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_claims_analyzed"] == 320
    assert data["anomalous_claims_count"] == 32
    assert "model_agreement" in data
    assert data["model_agreement"]["corr_iso_vs_lof"] > 0.50
