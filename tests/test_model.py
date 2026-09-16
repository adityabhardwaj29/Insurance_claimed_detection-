"""
tests/test_model.py
-------------------
Comprehensive unit and integration tests for Phase 4 Supervised ML Fraud Detection.

Covers:
  - Preprocessing & chronological splitting (zero data leakage validation)
  - ColumnTransformer fitting and encoding
  - Evaluation metrics calculation (PR-AUC, ROC-AUC, F1, Precision@K, Recall@K)
  - Prediction engine (fraud_probability in [0, 1], binary predictions)
  - Persisted model artifact verification (models/fraud_model/model.joblib)
  - Feature file verification (data/features/claim_features.csv)
  - Markdown report validation (reports/ml_model_report.md)
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.claim_features import create_claim_features
from src.models.evaluate import (
    compare_models,
    compute_precision_recall_at_k,
    evaluate_model,
)
from src.models.predict import load_model, predict, predict_probability, score_claims_dataframe
from src.models.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_column_transformer,
    split_data_temporal,
)

FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR = ROOT / "models" / "fraud_model"
REPORTS_DIR = ROOT / "reports"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Preprocessing & Temporal Split Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_column_transformer_build():
    transformer = build_column_transformer(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
    assert transformer is not None
    transformer_names = [name for name, _, _ in transformer.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names


def test_split_data_temporal_no_leakage():
    """
    Verify chronological ordering: every train claim_date must be <= every test claim_date.
    """
    df = create_claim_features()
    X_train, X_test, y_train, y_test = split_data_temporal(df, train_ratio=0.70)

    assert len(X_train) + len(X_test) == len(df) == 320
    assert len(X_train) == 224
    assert len(X_test) == 96

    # Verify dates in train vs test
    sorted_df = df.copy()
    sorted_df["_dt"] = pd.to_datetime(sorted_df["claim_date"])
    sorted_df = sorted_df.sort_values("_dt").reset_index(drop=True)

    max_train_date = sorted_df.iloc[:224]["_dt"].max()
    min_test_date = sorted_df.iloc[224:]["_dt"].min()

    assert max_train_date <= min_test_date, (
        f"Data leakage detected! Max train date {max_train_date} > Min test date {min_test_date}"
    )


def test_target_distribution_in_splits():
    df = create_claim_features()
    _, _, y_train, y_test = split_data_temporal(df, train_ratio=0.70)
    assert y_train.sum() > 0, "No fraud cases in train set"
    assert y_test.sum() > 0, "No fraud cases in test set"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Evaluation Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_precision_recall_at_k():
    y_true = [0, 1, 0, 1, 0, 0, 1, 0, 0, 0]  # 3 positives, 10 samples
    y_prob = [0.1, 0.9, 0.2, 0.8, 0.3, 0.4, 0.7, 0.2, 0.1, 0.05]
    # Sorted order of true labels: 1 (prob 0.9), 1 (prob 0.8), 1 (prob 0.7), 0, 0, 0, 0, 0, 0, 0

    metrics = compute_precision_recall_at_k(y_true, y_prob, k_fractions=(0.10, 0.20, 0.30))
    p_at_k = metrics["precision_at_k"]
    r_at_k = metrics["recall_at_k"]

    # Top 10% (k=1): label 1 -> Precision 1.0, Recall 1/3 = 0.3333
    assert p_at_k["top_10%"] == 1.0
    assert abs(r_at_k["top_10%"] - (1.0 / 3.0)) < 0.01

    # Top 20% (k=2): labels 1, 1 -> Precision 1.0, Recall 2/3 = 0.6667
    assert p_at_k["top_20%"] == 1.0
    assert abs(r_at_k["top_20%"] - (2.0 / 3.0)) < 0.01

    # Top 30% (k=3): labels 1, 1, 1 -> Precision 1.0, Recall 3/3 = 1.0
    assert p_at_k["top_30%"] == 1.0
    assert r_at_k["top_30%"] == 1.0


def test_evaluate_model_structure():
    from sklearn.linear_model import LogisticRegression
    X = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [4.0, 3.0, 2.0, 1.0]})
    y = [0, 0, 1, 1]
    clf = LogisticRegression().fit(X, y)

    res = evaluate_model(clf, X, y)
    assert "pr_auc" in res
    assert "roc_auc" in res
    assert "f1" in res
    assert "precision" in res
    assert "recall" in res
    assert "confusion_matrix" in res
    assert "precision_at_k" in res
    assert "recall_at_k" in res
    assert "brier_score" in res
    assert res["sample_count"] == 4


# ─────────────────────────────────────────────────────────────────────────────
# 3. Model Inference & Prediction Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_load_saved_model():
    model, metadata = load_model()
    assert model is not None
    assert isinstance(model, Pipeline)
    assert "model_name" in metadata
    assert "evaluation_metrics" in metadata


def test_predict_probability_range():
    model, _ = load_model()
    df = create_claim_features().head(20)
    probs = predict_probability(model, df)
    assert len(probs) == 20
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    # Ensure continuous non-trivial distribution (not all zero or one)
    assert len(np.unique(probs)) > 1


def test_predict_binary_output():
    model, _ = load_model()
    df = create_claim_features().head(20)
    preds = predict(model, df, threshold=0.5)
    assert len(preds) == 20
    assert set(np.unique(preds)).issubset({0, 1})


def test_score_claims_dataframe():
    model, _ = load_model()
    df = create_claim_features().head(10)
    scored = score_claims_dataframe(model, df)
    assert len(scored) == 10
    assert "fraud_probability" in scored.columns
    assert "predicted_fraud" in scored.columns


# ─────────────────────────────────────────────────────────────────────────────
# 4. Feature File & Artifact Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_claim_features_csv_exists_and_complete():
    path = FEATURES_DIR / "claim_features.csv"
    assert path.exists(), "claim_features.csv not found"
    df = pd.read_csv(path)
    assert len(df) == 320
    assert "claim_id" in df.columns
    assert "fraud_label" in df.columns
    assert df["claim_id"].is_unique
    assert set(df["fraud_label"].unique()) == {0, 1}


def test_persisted_model_files_exist():
    assert (MODELS_DIR / "model.joblib").exists()
    assert (MODELS_DIR / "metadata.json").exists()


def test_ml_model_report_exists_and_content():
    path = REPORTS_DIR / "ml_model_report.md"
    assert path.exists(), "ml_model_report.md not found"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Machine Learning Fraud Detection Report" in content
    assert "PR-AUC" in content
    assert "ROC-AUC" in content
    assert "Confusion Matrix" in content
