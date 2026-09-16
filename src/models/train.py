"""
src/models/train.py
-------------------
Supervised fraud detection training pipeline.

Features:
  - Temporal (chronological) train/test split (no future-data leakage)
  - Imbalance-aware training (class_weight='balanced' / scale_pos_weight)
  - Multiple model evaluation:
      1. Logistic Regression (Baseline)
      2. Random Forest
      3. HistGradientBoosting (scikit-learn gradient booster)
      4. XGBoost
  - Full scikit-learn Pipeline (preprocessor + classifier)
  - Automated selection based on PR-AUC on held-out test data
  - Artifact persistence in models/fraud_model/
  - Comprehensive Markdown report generation in reports/ml_model_report.md
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.features.claim_features import create_claim_features
from src.models.evaluate import compare_models, evaluate_model
from src.models.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET_COL,
    build_column_transformer,
    split_data_temporal,
)

ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT / "models" / "fraud_model"
REPORTS_DIR = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def create_model_candidates(scale_pos_weight: float = 5.0) -> dict[str, Any]:
    """
    Instantiates standard classifiers configured for class imbalance.
    """
    return {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            random_state=42,
        ),
        "RandomForest": RandomForestClassifier(
            class_weight="balanced",
            n_estimators=150,
            max_depth=6,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            class_weight="balanced",
            max_iter=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
        ),
        "XGBoost": XGBClassifier(
            scale_pos_weight=scale_pos_weight,
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        ),
    }


def train_and_evaluate_all(
    df: pd.DataFrame | None = None,
    train_ratio: float = 0.70,
) -> tuple[dict[str, Pipeline], pd.DataFrame, dict[str, Any], str]:
    """
    Trains all candidate models on temporal train split and evaluates on temporal test split.
    Selects best model based on PR-AUC.
    """
    if df is None:
        df = create_claim_features()

    logger.info("Splitting dataset temporally (train_ratio=%.2f)...", train_ratio)
    X_train, X_test, y_train, y_test = split_data_temporal(df, train_ratio=train_ratio)

    n_train = len(y_train)
    n_test = len(y_test)
    train_fraud = int(y_train.sum())
    test_fraud = int(y_test.sum())
    logger.info(
        "Train set: %d claims (Fraud: %d, %.2f%%) | Test set: %d claims (Fraud: %d, %.2f%%)",
        n_train,
        train_fraud,
        (train_fraud / n_train) * 100.0,
        n_test,
        test_fraud,
        (test_fraud / n_test) * 100.0,
    )

    scale_pos_weight = float((n_train - train_fraud) / max(1, train_fraud))
    candidates = create_model_candidates(scale_pos_weight=scale_pos_weight)

    trained_pipelines: dict[str, Pipeline] = {}
    evaluation_results: dict[str, Any] = {}

    for name, clf in candidates.items():
        logger.info("Training candidate: %s...", name)
        preprocessor = build_column_transformer(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", clf),
        ])
        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

        metrics = evaluate_model(pipe, X_test, y_test)
        evaluation_results[name] = metrics
        logger.info(
            "  %s -> PR-AUC: %.4f | ROC-AUC: %.4f | F1: %.4f | Prec@20%%: %.4f",
            name,
            metrics["pr_auc"],
            metrics["roc_auc"],
            metrics["f1"],
            metrics["precision_at_k"]["top_20%"],
        )

    # Comparison DataFrame
    comp_df = compare_models(trained_pipelines, X_test, y_test)

    # Select best model: highest PR-AUC on held-out test data
    best_name = str(comp_df.iloc[0]["Model"])
    logger.info("Best model selected by PR-AUC: %s", best_name)

    split_info = {
        "train_size": n_train,
        "test_size": n_test,
        "train_fraud_count": train_fraud,
        "test_fraud_count": test_fraud,
        "train_fraud_rate": round(train_fraud / n_train, 4),
        "test_fraud_rate": round(test_fraud / n_test, 4),
    }

    return trained_pipelines, comp_df, evaluation_results, best_name


def save_best_model(
    pipeline: Pipeline,
    model_name: str,
    comp_df: pd.DataFrame,
    metrics: dict[str, Any],
) -> Path:
    """
    Persists selected pipeline and metadata.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "model.joblib"
    meta_path = MODELS_DIR / "metadata.json"

    joblib.dump(pipeline, model_path)
    logger.info("Saved model artifact -> %s", model_path)

    metadata = {
        "model_name": model_name,
        "created_at": datetime.now().isoformat(),
        "evaluation_metrics": metrics[model_name],
        "all_model_comparison": comp_df.to_dict(orient="records"),
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_col": TARGET_COL,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved model metadata -> %s", meta_path)
    return model_path


def generate_markdown_report(
    comp_df: pd.DataFrame,
    metrics_dict: dict[str, Any],
    best_name: str,
) -> Path:
    """
    Generates reports/ml_model_report.md summarizing model performance.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "ml_model_report.md"

    best_m = metrics_dict[best_name]
    cm = best_m["confusion_matrix"]

    report_lines = [
        "# Machine Learning Fraud Detection Report",
        "## Supervised Baseline & Gradient Boosting Models",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "**Target:** `fraud_label` (Binary: 0 = Legit, 1 = Fraud, ~16.25% prevalence)",
        f"**Selected Model:** `{best_name}` (selected by PR-AUC on held-out temporal test set)",
        "",
        "---",
        "",
        "## 1. Feature Engineering & Preprocessing",
        "",
        "### Numeric Features (StandardScaler)",
        "".join([f"- `{f}`\n" for f in NUMERIC_FEATURES]),
        "",
        "### Categorical Features (OneHotEncoder)",
        "".join([f"- `{f}`\n" for f in CATEGORICAL_FEATURES]),
        "",
        "### Temporal Splitting & Leakage Prevention",
        "- Claims are strictly ordered chronologically by `claim_date`.",
        "- **Training Split:** First 70% of claims (chronological past).",
        "- **Test Split:** Remaining 30% of claims (chronological future).",
        "- Transformers are fitted strictly on the training set and applied to the test set.",
        "",
        "---",
        "",
        "## 2. Model Comparison Table",
        "",
        comp_df.to_markdown(index=False),
        "",
        "---",
        "",
        f"## 3. Selected Model Performance: `{best_name}`",
        "",
        f"- **PR-AUC (Average Precision):** {best_m['pr_auc']:.4f}",
        f"- **ROC-AUC:** {best_m['roc_auc']:.4f}",
        f"- **F1-Score:** {best_m['f1']:.4f}",
        f"- **Precision:** {best_m['precision']:.4f}",
        f"- **Recall:** {best_m['recall']:.4f}",
        f"- **Brier Score (Calibration):** {best_m['brier_score']:.4f}",
        "",
        "### Precision@K and Recall@K (Investigation Efficiency)",
        f"- **Precision@10%:** {best_m['precision_at_k']['top_10%']:.4f} (proportion of top 10% highest-risk claims that are fraud)",
        f"- **Recall@10%:** {best_m['recall_at_k']['top_10%']:.4f} (fraction of all test frauds captured in top 10%)",
        f"- **Precision@20%:** {best_m['precision_at_k']['top_20%']:.4f}",
        f"- **Recall@20%:** {best_m['recall_at_k']['top_20%']:.4f}",
        "",
        "### Confusion Matrix (Test Set, Threshold = 0.50)",
        "| | Predicted Negative (0) | Predicted Positive (1) |",
        "|---|---|---|",
        f"| **Actual Legit (0)** | TN = {cm['tn']} | FP = {cm['fp']} |",
        f"| **Actual Fraud (1)** | FN = {cm['fn']} | TP = {cm['tp']} |",
        "",
        "---",
        "",
        "## 4. Limitations and Next Steps",
        "",
        "1. **Synthetic Data Characteristics:** The dataset is project-generated synthetic data. Metrics reflect pattern discovery in this specific synthetic formulation.",
        "2. **Imbalance Constraints:** With ~16.25% positive prevalence, high decision thresholds reduce recall; risk-based ranking via `fraud_probability` is operationally superior to fixed 0.5 binary cutoffs.",
        "3. **Graph Feature Enhancement (Phase 5):** Integrating network centrality and community risk will provide graph-structural signals to further improve PR-AUC.",
        "",
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("Saved report -> %s", report_path)
    return report_path


def run_pipeline() -> None:
    """Full execution pipeline."""
    trained_pipelines, comp_df, metrics_dict, best_name = train_and_evaluate_all()

    save_best_model(trained_pipelines[best_name], best_name, comp_df, metrics_dict)
    generate_markdown_report(comp_df, metrics_dict, best_name)

    print("\n" + "=" * 65)
    print("PHASE 4 MACHINE LEARNING FRAUD DETECTION - SUMMARY")
    print("=" * 65)
    print(f"Selected Model: {best_name}")
    print("\nModel Comparison on Held-Out Temporal Test Set:")
    print(comp_df.to_string(index=False))
    print("\n" + "=" * 65)


if __name__ == "__main__":
    run_pipeline()
