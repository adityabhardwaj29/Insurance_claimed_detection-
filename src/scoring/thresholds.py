"""
src/scoring/thresholds.py
--------------------------
Configurable risk band thresholds and component normalization parameters
for the Hybrid Fraud Risk Engine (Phase 8).

DESIGN PHILOSOPHY
-----------------
All thresholds are derived from empirically observed data distributions
(computed from the actual dataset in scratch/calibrate_thresholds.py).
No threshold is arbitrary; each is documented with the data-driven rationale.

RISK BANDS
----------
Operational investigation priority categories — NOT claims that a claimant is fraudulent.

  CRITICAL  : final_risk_score >= 0.75 — Immediate escalation recommended
  HIGH      : final_risk_score >= 0.55 — Priority review within 24h
  MEDIUM    : final_risk_score >= 0.35 — Standard review queue
  LOW       : final_risk_score <  0.35 — Routine processing

COMPONENT WEIGHTS
-----------------
Weights are documented rationale-based, not arbitrary:

  fraud_probability  (0.45): The supervised ML model is trained on ground-truth
      fraud_label. It has the strongest empirical link to fraud outcomes.

  anomaly_score      (0.25): Isolation Forest calibrated to [0,1]. Unsupervised;
      may detect novel fraud patterns not in training labels.

  duplicate_score    (0.15): Normalized similarity score. Duplicate/similar claims
      are a documented fraud pattern (shared invoice reuse = 23.5% fraud rate in
      POSSIBLE_DUPLICATE category vs 16.25% overall).

  graph_risk_score   (0.15): Network risk aggregating claimant connectivity,
      provider volume, fraud-neighbor ratio, and repeated relationships.
      Lower weight because graph signal was marginal on this dataset (Phase 7).

Total: 1.00

NORMALIZATION PARAMETERS
-------------------------
Derived from actual data percentiles (see scratch/calibrate_thresholds.py):

  Claim amount p90: 232,188 — used as upper bound for amount outlier flag
  Amount-to-premium p90: 7.02 — threshold for ratio outlier flag
  Provider claim count p75: 18 (approx) — above median: suspicious provider
  Duplicate similarity min/max: 0.33 / 0.63 — actual data range
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class RiskBands:
    """Risk band thresholds derived from operational requirements.
    All bands are configurable by overriding this object.
    """
    CRITICAL: float = 0.75
    HIGH: float = 0.55
    MEDIUM: float = 0.35

    def classify(self, score: float) -> str:
        """Maps a final_risk_score in [0, 1] to an operational risk band."""
        if score >= self.CRITICAL:
            return "CRITICAL"
        if score >= self.HIGH:
            return "HIGH"
        if score >= self.MEDIUM:
            return "MEDIUM"
        return "LOW"


@dataclass(frozen=True)
class ComponentWeights:
    """
    Weights for the four scoring components.
    Rationale is documented in the module docstring.
    Must sum to 1.0.
    """
    fraud_probability: float = 0.45
    anomaly_score: float = 0.25
    duplicate_score: float = 0.15
    graph_risk_score: float = 0.15

    def __post_init__(self) -> None:
        total = (
            self.fraud_probability
            + self.anomaly_score
            + self.duplicate_score
            + self.graph_risk_score
        )
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"Component weights must sum to 1.0, got {total:.6f}. "
                f"fraud={self.fraud_probability}, anomaly={self.anomaly_score}, "
                f"duplicate={self.duplicate_score}, graph={self.graph_risk_score}"
            )


@dataclass(frozen=True)
class ReasonThresholds:
    """
    Data-driven thresholds for generating explainable risk reasons.
    Each threshold is derived from actual percentiles of the dataset
    (see scratch/calibrate_thresholds.py for provenance).
    """
    # Fraud probability: any claim above this is considered high-probability fraud
    HIGH_FRAUD_PROB: float = 0.60  # XGBoost p60 threshold

    # Anomaly score: top 10% of anomaly scores in dataset
    HIGH_ANOMALY: float = 0.57  # empirical p90 = 0.5665, rounded to 0.57

    # Duplicate similarity: top quartile of actual data range
    HIGH_DUPLICATE_SIMILARITY: float = 0.50  # above p75 of similarity distribution (0.505)

    # Claim amount: 90th percentile of actual dataset
    HIGH_CLAIM_AMOUNT: float = 232_188.0  # p90 of claim_amount

    # Amount-to-premium ratio: 90th percentile
    HIGH_AMOUNT_PREMIUM_RATIO: float = 7.02  # p90 of amount_to_premium_ratio

    # Claimant degree: above dataset mean (6.84)
    HIGH_CLAIMANT_DEGREE: int = 7  # above mean

    # Provider claim count: above dataset median (13)
    HIGH_PROVIDER_VOLUME: int = 13  # above dataset median provider_claim_count (per node in graph)

    # Provider claim volume (from claim_features, raw count): above p75
    HIGH_PROVIDER_VOLUME_TABULAR: int = 10  # p75 of provider_claim_volume in claim_features

    # Fraud neighbor ratio: any non-zero claimant-sibling fraud signal
    NONZERO_FRAUD_NEIGHBOR_RATIO: float = 0.0

    # Claimant claim frequency: having 4+ claims
    HIGH_CLAIM_FREQUENCY: int = 3  # claimant_claim_frequency > 3

    # Suspicious neighbor count: 1+ suspicious provider connections in claimant history
    SUSPICIOUS_NEIGHBOR_MIN: int = 1


@dataclass(frozen=True)
class NormalizationParams:
    """
    Parameters for normalizing component scores to [0, 1] range.
    All bounds are derived from actual dataset distributions.
    """
    # Duplicate similarity: actual min/max from data
    DUP_SCORE_MIN: float = 0.33   # data minimum
    DUP_SCORE_MAX: float = 0.63   # data maximum

    # Provider claim count (graph node): data range 7-25
    PROVIDER_COUNT_MIN: float = 7.0
    PROVIDER_COUNT_MAX: float = 25.0

    # Claimant degree: data range 2-11
    CLAIMANT_DEGREE_MIN: float = 2.0
    CLAIMANT_DEGREE_MAX: float = 11.0

    # Provider betweenness: data range 0.01-0.046
    PROVIDER_BC_MIN: float = 0.01
    PROVIDER_BC_MAX: float = 0.046

    # Suspicious neighbor count: data range 0-6
    SUSPICIOUS_NEIGHBOR_MAX: float = 6.0

    # Claimant claim count: data range 1-7
    CLAIMANT_CLAIM_COUNT_MAX: float = 7.0


# Default configuration instances
DEFAULT_RISK_BANDS = RiskBands()
DEFAULT_WEIGHTS = ComponentWeights()
DEFAULT_REASON_THRESHOLDS = ReasonThresholds()
DEFAULT_NORMALIZATION = NormalizationParams()
