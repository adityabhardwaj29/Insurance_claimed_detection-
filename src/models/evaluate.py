"""
src/models/evaluate.py
----------------------
Evaluation metrics for fraud detection models on imbalanced datasets.

Calculates:
  - Precision, Recall, F1-Score
  - PR-AUC (Average Precision Score)
  - ROC-AUC
  - Confusion Matrix (TN, FP, FN, TP)
  - Precision@K (e.g. Precision@10%, Precision@20%)
  - Recall@K (e.g. Recall@10%, Recall@20%)
  - Brier score loss
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_precision_recall_at_k(
    y_true: Sequence[int],
    y_prob: Sequence[float],
    k_fractions: Sequence[float] = (0.10, 0.20),
) -> dict[str, dict[str, float]]:
    """
    Computes Precision@K and Recall@K where K is a fraction of the total test set.
    """
    y_true_arr = np.asarray(y_true)
    y_prob_arr = np.asarray(y_prob)

    n = len(y_true_arr)
    total_positives = int(np.sum(y_true_arr == 1))
    if total_positives == 0 or n == 0:
        return {
            "precision_at_k": {f"top_{int(k * 100)}%": 0.0 for k in k_fractions},
            "recall_at_k": {f"top_{int(k * 100)}%": 0.0 for k in k_fractions},
        }

    # Sort descending by probability
    order = np.argsort(-y_prob_arr)
    sorted_labels = y_true_arr[order]

    precisions = {}
    recalls = {}
    for frac in k_fractions:
        k = max(1, int(round(n * frac)))
        top_k_labels = sorted_labels[:k]
        tp_k = int(np.sum(top_k_labels == 1))

        prec = float(tp_k / k)
        rec = float(tp_k / total_positives)

        tag = f"top_{int(frac * 100)}%"
        precisions[tag] = round(prec, 4)
        recalls[tag] = round(rec, 4)

    return {
        "precision_at_k": precisions,
        "recall_at_k": recalls,
    }


def evaluate_model(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    y_true: Sequence[int],
    threshold: float = 0.5,
    k_fractions: Sequence[float] = (0.10, 0.20),
) -> dict[str, Any]:
    """
    Evaluates a trained model pipeline on a test or validation dataset.
    """
    y_true_arr = np.asarray(y_true, dtype=int)

    # Probabilities
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X)[:, 1]
    elif hasattr(model, "decision_function"):
        df_vals = model.decision_function(X)
        y_prob = 1.0 / (1.0 + np.exp(-df_vals))
    else:
        y_prob = model.predict(X).astype(float)

    # Binary predictions
    y_pred = (y_prob >= threshold).astype(int)

    # Standard metrics
    prec = precision_score(y_true_arr, y_pred, zero_division=0)
    rec = recall_score(y_true_arr, y_pred, zero_division=0)
    f1 = f1_score(y_true_arr, y_pred, zero_division=0)
    acc = accuracy_score(y_true_arr, y_pred)

    try:
        roc_auc = roc_auc_score(y_true_arr, y_prob)
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = average_precision_score(y_true_arr, y_prob)
    except Exception:
        pr_auc = float(np.mean(y_true_arr))

    cm = confusion_matrix(y_true_arr, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
    brier = brier_score_loss(y_true_arr, y_prob)

    # Precision@K and Recall@K
    top_k_metrics = compute_precision_recall_at_k(y_true_arr, y_prob, k_fractions=k_fractions)

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "pr_auc": round(float(pr_auc), 4),
        "roc_auc": round(float(roc_auc), 4),
        "brier_score": round(float(brier), 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "precision_at_k": top_k_metrics["precision_at_k"],
        "recall_at_k": top_k_metrics["recall_at_k"],
        "threshold": threshold,
        "sample_count": len(y_true_arr),
        "fraud_count": int(np.sum(y_true_arr == 1)),
    }


def compare_models(
    models_dict: Mapping[str, Any],
    X_test: pd.DataFrame | np.ndarray,
    y_test: Sequence[int],
    k_fractions: Sequence[float] = (0.10, 0.20),
) -> pd.DataFrame:
    """
    Evaluates multiple models and returns a consolidated comparison DataFrame.
    """
    rows = []
    for name, model in models_dict.items():
        metrics = evaluate_model(model, X_test, y_test, k_fractions=k_fractions)
        row = {
            "Model": name,
            "PR-AUC": metrics["pr_auc"],
            "ROC-AUC": metrics["roc_auc"],
            "F1-Score": metrics["f1"],
            "Precision": metrics["precision"],
            "Recall": metrics["recall"],
            "Precision@10%": metrics["precision_at_k"].get("top_10%", 0.0),
            "Recall@10%": metrics["recall_at_k"].get("top_10%", 0.0),
            "Precision@20%": metrics["precision_at_k"].get("top_20%", 0.0),
            "Recall@20%": metrics["recall_at_k"].get("top_20%", 0.0),
            "Brier Score": metrics["brier_score"],
        }
        rows.append(row)
    return pd.DataFrame(rows).sort_values("PR-AUC", ascending=False).reset_index(drop=True)
