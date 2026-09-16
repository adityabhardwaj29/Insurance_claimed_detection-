"""
src/models/anomaly/models.py
----------------------------
Model definitions and score calibration for unsupervised anomaly detection.

Models:
  - Isolation Forest: Recursive partitioning isolating sparse points.
  - Local Outlier Factor (LOF): Density-based local neighborhood anomaly detection.
  - One-Class SVM: Boundary-based kernel support vector outlier detector.

Score Calibration:
  Standardizes disparate raw decision functions (where negative usually means anomaly)
  into a strictly bounded continuous score in [0.0, 1.0], where 1.0 indicates maximum anomaly.
"""

from __future__ import annotations

from typing import Any, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM


def build_isolation_forest(
    contamination: float = 0.10,
    n_estimators: int = 150,
    random_state: int = 42,
) -> IsolationForest:
    """Instantiates an Isolation Forest estimator."""
    return IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1,
    )


def build_local_outlier_factor(
    contamination: float = 0.10,
    n_neighbors: int = 20,
) -> LocalOutlierFactor:
    """Instantiates Local Outlier Factor configured for novelty detection."""
    return LocalOutlierFactor(
        contamination=contamination,
        n_neighbors=n_neighbors,
        novelty=True,
        n_jobs=-1,
    )


def build_one_class_svm(
    nu: float = 0.10,
    kernel: str = "rbf",
    gamma: str = "scale",
) -> OneClassSVM:
    """Instantiates a One-Class SVM estimator."""
    return OneClassSVM(
        nu=nu,
        kernel=kernel,
        gamma=gamma,
    )


def calibrate_anomaly_score(raw_scores: np.ndarray, invert: bool = True) -> np.ndarray:
    """
    Normalizes decision_function output to [0.0, 1.0] where 1.0 represents the highest anomaly.
    In scikit-learn anomaly models (IsolationForest, LOF, OneClassSVM),
    lower/more negative decision_function values denote greater anomaly.
    Hence, invert=True inverts the scale so higher = more anomalous.
    """
    arr = np.asarray(raw_scores, dtype=float)
    min_val = np.min(arr)
    max_val = np.max(arr)

    if max_val - min_val < 1e-9:
        return np.zeros_like(arr)

    if invert:
        # Lower raw score -> Higher normalized anomaly score
        normalized = (max_val - arr) / (max_val - min_val)
    else:
        normalized = (arr - min_val) / (max_val - min_val)

    return np.clip(np.round(normalized, 4), 0.0, 1.0)
