"""
src/scoring/risk_score.py
-------------------------
Calculates the hybrid composite risk score for an insurance claim by
combining machine learning, anomaly detection, duplicate similarity,
and graph topology signals.

Uses configured weights from src.scoring.thresholds:
  - ml_probability: 0.45
  - anomaly_score:  0.25
  - duplicate_score: 0.15
  - graph_risk:     0.15
"""

from __future__ import annotations

from typing import Optional
import numpy as np

from src.scoring.thresholds import DEFAULT_WEIGHTS, ComponentWeights


def calculate_risk_score(
    ml_probability: float,
    anomaly_score: float,
    duplicate_score: float,
    graph_risk: float,
    weights: Optional[ComponentWeights] = None,
) -> float:
    """
    Computes a calibrated, weighted composite risk score in [0, 1].

    Parameters
    ----------
    ml_probability : float
        Supervised model predicted probability of fraud in [0, 1].
    anomaly_score : float
        Calibrated unsupervised anomaly score in [0, 1].
    duplicate_score : float
        Normalised duplicate similarity score in [0, 1].
    graph_risk : float
        Composite graph topology risk score in [0, 1].
    weights : ComponentWeights, optional
        Weight configuration. Defaults to DEFAULT_WEIGHTS (0.45, 0.25, 0.15, 0.15).

    Returns
    -------
    float
        Weighted composite risk score rounded to 4 decimal places, clamped to [0, 1].
    """
    w = weights or DEFAULT_WEIGHTS

    # Clip components to valid [0, 1] range to prevent scale leakage
    ml = float(np.clip(ml_probability, 0.0, 1.0))
    an = float(np.clip(anomaly_score, 0.0, 1.0))
    dup = float(np.clip(duplicate_score, 0.0, 1.0))
    gr = float(np.clip(graph_risk, 0.0, 1.0))

    score = (
        w.fraud_probability * ml
        + w.anomaly_score * an
        + w.duplicate_score * dup
        + w.graph_risk_score * gr
    )
    return round(float(np.clip(score, 0.0, 1.0)), 4)
