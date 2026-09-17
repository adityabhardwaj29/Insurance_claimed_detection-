"""
src/scoring/risk_engine.py
--------------------------
Phase 8: Hybrid Fraud Risk Engine.

Produces a transparent, explainable risk score for every insurance claim
by combining four independently derived signals into a weighted composite
score with configurable risk band classification.

INPUTS (all from actual pipeline outputs — no random numbers)
--------------------------------------------------------------
1. fraud_probability : XGBoost supervised model output (Phase 4)
2. anomaly_score     : Calibrated Isolation Forest + LOF ensemble score (Phase 5)
3. duplicate_score   : Normalised pairwise similarity score (Phase 3)
4. graph_risk_score  : Composite graph topology risk signal (Phase 6/7)

OUTPUTS
-------
data/features/final_risk_scores.csv with columns:
  claim_id, fraud_probability, anomaly_score, duplicate_score,
  graph_risk_score, final_risk_score, risk_band, risk_reasons

SCORING FORMULA (transparent, documented)
-----------------------------------------
  final_risk_score =
      w_fraud * fraud_probability
    + w_anomaly * anomaly_score
    + w_duplicate * duplicate_score
    + w_graph * graph_risk_score

  where weights are configured in thresholds.ComponentWeights
  (fraud=0.45, anomaly=0.25, duplicate=0.15, graph=0.15)

  All component scores are in [0, 1] before weighting.
  final_risk_score is in [0, 1].

GRAPH RISK SCORE DERIVATION
----------------------------
graph_risk_score is a weighted composite of 5 normalised graph signals:

  signal_1 = fraud_neighbor_ratio                          [0, 1]       w=0.35
  signal_2 = claimant_degree (min-max normalised)         [0, 1]       w=0.20
  signal_3 = provider_claim_count (min-max normalised)   [0, 1]       w=0.20
  signal_4 = repeated_claimant_provider                   {0, 1}       w=0.15
  signal_5 = suspicious_neighbor_count / max_count        [0, 1]       w=0.10

All normalisation bounds are from actual dataset distributions (thresholds.py).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from src.scoring.thresholds import (
    ComponentWeights,
    NormalizationParams,
    ReasonThresholds,
    RiskBands,
    DEFAULT_RISK_BANDS,
    DEFAULT_WEIGHTS,
    DEFAULT_REASON_THRESHOLDS,
    DEFAULT_NORMALIZATION,
)
from src.scoring.risk_reasons import (
    generate_reasons,
    reasons_to_string,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent

# Graph risk sub-component weights (must sum to 1.0)
GRAPH_SIGNAL_WEIGHTS = {
    "fraud_neighbor_ratio": 0.35,
    "claimant_degree_norm": 0.20,
    "provider_count_norm": 0.20,
    "repeated_claimant_provider": 0.15,
    "suspicious_neighbor_norm": 0.10,
}
assert abs(sum(GRAPH_SIGNAL_WEIGHTS.values()) - 1.0) < 1e-9, \
    "Graph signal weights must sum to 1.0"


def _minmax_clip(val: float, lo: float, hi: float) -> float:
    """Normalises val to [0, 1] using actual dataset min/max bounds."""
    if hi <= lo:
        return 0.0
    return float(np.clip((val - lo) / (hi - lo), 0.0, 1.0))


def compute_graph_risk_score(
    row: Dict[str, Any],
    norm: NormalizationParams = DEFAULT_NORMALIZATION,
) -> float:
    """
    Computes a composite graph risk score in [0, 1] from graph topology features.

    Sub-signals (all in [0, 1]):
      fraud_neighbor_ratio    — fraction of claimant's sibling claims that are fraudulent
      claimant_degree_norm    — normalised claimant connectivity in the insurance network
      provider_count_norm     — normalised provider claim volume (high volume = more risk)
      repeated_claimant_provider — binary flag for repeat claimant-provider pairs
      suspicious_neighbor_norm — normalised count of suspicious providers in claimant history
    """
    def get(key: float, default: float = 0.0) -> float:
        v = row.get(key)
        try:
            return float(v) if v is not None else default
        except (TypeError, ValueError):
            return default

    fnr = float(np.clip(get("fraud_neighbor_ratio"), 0.0, 1.0))

    clt_deg = get("claimant_degree")
    clt_deg_norm = _minmax_clip(clt_deg, norm.CLAIMANT_DEGREE_MIN, norm.CLAIMANT_DEGREE_MAX)

    prv_cnt = get("provider_claim_count")
    prv_cnt_norm = _minmax_clip(prv_cnt, norm.PROVIDER_COUNT_MIN, norm.PROVIDER_COUNT_MAX)

    repeated = float(np.clip(get("repeated_claimant_provider"), 0.0, 1.0))

    susp = get("suspicious_neighbor_count")
    susp_norm = float(np.clip(susp / norm.SUSPICIOUS_NEIGHBOR_MAX, 0.0, 1.0))

    score = (
        GRAPH_SIGNAL_WEIGHTS["fraud_neighbor_ratio"] * fnr
        + GRAPH_SIGNAL_WEIGHTS["claimant_degree_norm"] * clt_deg_norm
        + GRAPH_SIGNAL_WEIGHTS["provider_count_norm"] * prv_cnt_norm
        + GRAPH_SIGNAL_WEIGHTS["repeated_claimant_provider"] * repeated
        + GRAPH_SIGNAL_WEIGHTS["suspicious_neighbor_norm"] * susp_norm
    )
    return round(float(np.clip(score, 0.0, 1.0)), 6)


def compute_duplicate_score(
    row: Dict[str, Any],
    norm: NormalizationParams = DEFAULT_NORMALIZATION,
) -> float:
    """
    Normalises the duplicate similarity score to [0, 1] using actual data min/max.
    Falls back to dup_similarity_score, then duplicate_similarity_score.
    """
    raw = row.get("dup_similarity_score") or row.get("duplicate_similarity_score")
    if raw is None:
        return 0.0
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return 0.0
    return round(
        _minmax_clip(val, norm.DUP_SCORE_MIN, norm.DUP_SCORE_MAX),
        6,
    )


def load_fraud_model_and_predict(
    feature_df: pd.DataFrame,
    model_path: Optional[str] = None,
) -> np.ndarray:
    """
    Loads the trained fraud model (Phase 4) and computes fraud probability
    for all claims using the same feature columns the model was trained on.

    Returns a numpy array of probabilities in [0, 1].
    """
    if model_path is None:
        model_path = str(ROOT / "models" / "fraud_model" / "model.joblib")
    meta_path = str(ROOT / "models" / "fraud_model" / "metadata.json")

    if not Path(model_path).exists():
        raise FileNotFoundError(f"Fraud model not found: {model_path}")

    pipe = joblib.load(model_path)

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    numeric_features = meta.get("numeric_features", [])
    categorical_features = meta.get("categorical_features", [])
    feature_cols = [c for c in numeric_features + categorical_features if c in feature_df.columns]

    X = feature_df[feature_cols]
    probs = pipe.predict_proba(X)[:, 1]
    logger.info("Fraud probabilities computed: min=%.4f, max=%.4f, mean=%.4f",
                probs.min(), probs.max(), probs.mean())
    return probs


def compute_risk_scores(
    feature_df: Optional[pd.DataFrame] = None,
    weights: ComponentWeights = DEFAULT_WEIGHTS,
    risk_bands: RiskBands = DEFAULT_RISK_BANDS,
    reason_thresholds: ReasonThresholds = DEFAULT_REASON_THRESHOLDS,
    norm: NormalizationParams = DEFAULT_NORMALIZATION,
    output_path: Optional[str] = "data/features/final_risk_scores.csv",
    fraud_model_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Main entry point for the Hybrid Fraud Risk Engine.

    For each claim, computes:
      - fraud_probability   from trained supervised model
      - anomaly_score       from Phase 5 calibrated output [0, 1]
      - duplicate_score     normalised similarity [0, 1]
      - graph_risk_score    composite graph topology score [0, 1]
      - final_risk_score    weighted combination [0, 1]
      - risk_band           operational category (LOW/MEDIUM/HIGH/CRITICAL)
      - risk_reasons        pipe-separated evidence-based explanations

    Parameters
    ----------
    feature_df : DataFrame, optional
        Merged feature DataFrame with all signal columns. If None, loads from
        data/features/final_claim_features.csv.
    weights : ComponentWeights
        Configurable component weights (see thresholds.py).
    risk_bands : RiskBands
        Configurable band thresholds (see thresholds.py).
    reason_thresholds : ReasonThresholds
        Configurable reason trigger thresholds (see thresholds.py).
    norm : NormalizationParams
        Normalisation bounds derived from actual data distributions.
    output_path : str, optional
        Where to save the output CSV.
    fraud_model_path : str, optional
        Override path to fraud model joblib.

    Returns
    -------
    pd.DataFrame with columns:
        claim_id, fraud_probability, anomaly_score, duplicate_score,
        graph_risk_score, final_risk_score, risk_band, risk_reasons
    """
    if feature_df is None:
        feature_df = pd.read_csv("data/features/final_claim_features.csv")
    logger.info("Risk engine: processing %d claims...", len(feature_df))

    # --- Compute fraud_probability via actual model ---
    fraud_probs = load_fraud_model_and_predict(feature_df, model_path=fraud_model_path)

    # --- Anomaly score (already [0, 1] from Phase 5 calibration) ---
    anomaly_scores = feature_df["anomaly_score"].fillna(0.0).values.astype(float)
    anomaly_scores = np.clip(anomaly_scores, 0.0, 1.0)

    records = []

    for idx, row in feature_df.iterrows():
        cid = str(row["claim_id"])
        fp = float(fraud_probs[idx])
        ans = float(anomaly_scores[idx])
        row_dict = row.to_dict()

        # Augment row with computed fraud_probability for reason generation
        row_dict["fraud_probability"] = fp
        row_dict["anomaly_score"] = ans

        # Duplicate score — normalised to [0, 1]
        dup_score = compute_duplicate_score(row_dict, norm)

        # Graph risk score — composite normalised
        graph_score = compute_graph_risk_score(row_dict, norm)

        # Final weighted composite
        final_score = round(
            weights.fraud_probability * fp
            + weights.anomaly_score * ans
            + weights.duplicate_score * dup_score
            + weights.graph_risk_score * graph_score,
            6,
        )
        final_score = float(np.clip(final_score, 0.0, 1.0))

        # Risk band
        band = risk_bands.classify(final_score)

        # Evidence-based risk reasons
        reason_codes = generate_reasons(row_dict, reason_thresholds)
        reason_str = reasons_to_string(reason_codes)

        records.append({
            "claim_id": cid,
            "fraud_probability": round(fp, 6),
            "anomaly_score": round(ans, 6),
            "duplicate_score": round(dup_score, 6),
            "graph_risk_score": round(graph_score, 6),
            "final_risk_score": round(final_score, 6),
            "risk_band": band,
            "risk_reasons": reason_str,
        })

    result_df = pd.DataFrame(records)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(out_p, index=False)
        logger.info("Risk scores saved: %s (%d rows)", out_p, len(result_df))

    return result_df


def print_summary(df: pd.DataFrame) -> None:
    """Prints a console summary of the risk scoring results."""
    print("\n" + "=" * 60)
    print("PHASE 8: HYBRID FRAUD RISK ENGINE — RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total claims scored: {len(df)}")
    print()

    print("Risk Band Distribution:")
    band_counts = df["risk_band"].value_counts().reindex(
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"], fill_value=0
    )
    for band, count in band_counts.items():
        pct = count / len(df) * 100
        print(f"  {band:<10}: {count:>4} claims ({pct:5.1f}%)")

    print()
    print("Component Score Statistics (mean ± std):")
    for col in ["fraud_probability", "anomaly_score", "duplicate_score",
                "graph_risk_score", "final_risk_score"]:
        print(f"  {col:<25}: mean={df[col].mean():.4f}, std={df[col].std():.4f}, "
              f"min={df[col].min():.4f}, max={df[col].max():.4f}")

    print()
    print("Top 10 Highest Risk Claims:")
    top10 = df.nlargest(10, "final_risk_score")[
        ["claim_id", "final_risk_score", "risk_band", "fraud_probability",
         "graph_risk_score"]
    ]
    print(top10.to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s",
                        stream=sys.stdout)
    print("Running Hybrid Fraud Risk Engine...")
    df = compute_risk_scores()
    print_summary(df)
