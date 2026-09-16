"""
src/models/anomaly/anomaly_detector.py
--------------------------------------
Unsupervised anomaly detection engine for insurance claim fraud detection.

Goal:
  Identifies unusual, out-of-distribution claims independently from supervised fraud classification.
  IMPORTANT: Anomaly does NOT automatically mean fraud. Anomaly score and fraud probability
  are maintained as separate, complementary signals.

Models:
  - Isolation Forest (Primary production model)
  - Local Outlier Factor (LOF)
  - One-Class SVM

Generates:
  data/features/anomaly_features.csv:
    - claim_id
    - anomaly_score (calibrated in [0.0, 1.0], higher = more anomalous)
    - anomaly_flag (1 = anomalous, 0 = normal)
    - anomaly_reason (human-interpretable breakdown of contributing factors)
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
from sklearn.preprocessing import StandardScaler

from src.models.anomaly.features import ANOMALY_FEATURE_COLS, extract_anomaly_features
from src.models.anomaly.models import (
    build_isolation_forest,
    build_local_outlier_factor,
    build_one_class_svm,
    calibrate_anomaly_score,
)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR = ROOT / "models" / "anomaly_model"
REPORTS_DIR = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Unsupervised multi-model anomaly detection engine with calibrated scoring
    and automated explainability.
    """

    def __init__(
        self,
        contamination: float = 0.10,
        random_state: int = 42,
    ) -> None:
        self.contamination = contamination
        self.random_state = random_state

        self.iso_forest = build_isolation_forest(contamination=contamination, random_state=random_state)
        self.lof = build_local_outlier_factor(contamination=contamination)
        self.ocsvm = build_one_class_svm(nu=contamination)
        self.scaler = StandardScaler()

        self.feature_names = list(ANOMALY_FEATURE_COLS)
        self.medians: dict[str, float] = {}
        self.std_devs: dict[str, float] = {}

    def fit_predict(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Fits all 3 unsupervised models, computes calibrated scores, binary flags,
        and human-interpretable anomaly reasons.
        """
        X_raw = df_features[self.feature_names].copy()

        # Compute population statistics for reason generation
        for col in self.feature_names:
            self.medians[col] = float(X_raw[col].median())
            self.std_devs[col] = float(X_raw[col].std()) if X_raw[col].std() > 0 else 1.0

        # Scale features
        X_scaled = self.scaler.fit_transform(X_raw)

        # 1. Isolation Forest
        logger.info("Fitting Isolation Forest...")
        self.iso_forest.fit(X_scaled)
        iso_raw = self.iso_forest.decision_function(X_scaled)
        iso_scores = calibrate_anomaly_score(iso_raw, invert=True)

        # 2. Local Outlier Factor
        logger.info("Fitting Local Outlier Factor (Novelty)...")
        self.lof.fit(X_scaled)
        lof_raw = self.lof.decision_function(X_scaled)
        lof_scores = calibrate_anomaly_score(lof_raw, invert=True)

        # 3. One-Class SVM
        logger.info("Fitting One-Class SVM...")
        self.ocsvm.fit(X_scaled)
        oc_raw = self.ocsvm.decision_function(X_scaled)
        oc_scores = calibrate_anomaly_score(oc_raw, invert=True)

        # Binary flag based on contamination percentile of primary model (Isolation Forest)
        threshold_val = float(np.percentile(iso_scores, (1.0 - self.contamination) * 100.0))
        anomaly_flags = (iso_scores >= threshold_val).astype(int)

        # Generate reasons
        reasons = []
        n = len(df_features)
        for i in range(n):
            row = X_raw.iloc[i]
            flag = anomaly_flags[i]
            score = iso_scores[i]
            reason = self._generate_reason(row, flag, score)
            reasons.append(reason)

        out = pd.DataFrame({
            "claim_id": df_features["claim_id"],
            "anomaly_score": iso_scores,
            "anomaly_flag": anomaly_flags,
            "anomaly_reason": reasons,
            "isolation_forest_score": iso_scores,
            "lof_score": lof_scores,
            "ocsvm_score": oc_scores,
        })
        return out

    def _generate_reason(self, row: pd.Series, flag: int, score: float) -> str:
        """
        Derives an interpretable explanation of anomalous deviations.
        """
        if flag == 0 and score < 0.55:
            return "Normal range across operational and financial metrics"

        signals = []

        # 1. Claim Amount
        amt = float(row.get("claim_amount", 0))
        if amt >= 250000:
            signals.append(f"High claim amount (INR {amt:,.0f}, Top 5%)")

        # 2. Amount to Premium Ratio
        apr = float(row.get("amount_to_premium_ratio", 0))
        if apr >= 6.0:
            signals.append(f"High amount-to-premium ratio ({apr:.1f}x vs median {self.medians['amount_to_premium_ratio']:.1f}x)")

        # 3. Invoice to Claim Ratio discrepancy
        icr = float(row.get("invoice_to_claim_ratio", 0))
        if icr >= 2.5:
            signals.append(f"Invoice exceeds claim amount ({icr:.1f}x ratio)")
        elif icr <= 0.15:
            signals.append(f"Invoice unusually small relative to claim ({icr:.2f}x ratio)")

        # 4. Inception Proximity
        dsp = float(row.get("days_since_policy_start", 999))
        if dsp <= 14:
            signals.append(f"Early claim immediately post-inception ({int(dsp)} days)")

        # 5. Claimant Claim Frequency
        cfreq = int(row.get("claimant_claim_count", 1))
        if cfreq >= 5:
            signals.append(f"High claimant claim frequency ({cfreq} claims)")

        # 6. Multi-vehicle ownership
        vcnt = int(row.get("claimant_vehicle_count", 1))
        if vcnt >= 3:
            signals.append(f"Multiple vehicles on file ({vcnt} vehicles)")

        # 7. Provider volume concentration
        pvol = int(row.get("provider_claim_count", 1))
        if pvol >= 20:
            signals.append(f"High-volume provider concentration ({pvol} claims)")

        # 8. Provider Rating
        prat = float(row.get("provider_rating", 4.0))
        if prat <= 3.2:
            signals.append(f"Low provider quality rating ({prat:.1f}/5.0)")

        if signals:
            return "; ".join(signals[:3])
        return "Statistical multivariate outlier across combined feature dimensions"


def run_pipeline() -> None:
    """Full unsupervised anomaly detection pipeline."""
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    features_df, raw_df = extract_anomaly_features()

    detector = AnomalyDetector(contamination=0.10, random_state=42)
    anomaly_df = detector.fit_predict(features_df)

    # Save data/features/anomaly_features.csv
    out_csv = FEATURES_DIR / "anomaly_features.csv"
    anomaly_df.to_csv(out_csv, index=False)
    logger.info("Saved anomaly features -> %s (%d rows)", out_csv, len(anomaly_df))

    # Persist model artifacts
    joblib.dump(detector.iso_forest, MODELS_DIR / "isolation_forest.joblib")
    joblib.dump(detector.scaler, MODELS_DIR / "scaler.joblib")

    # Evaluation & Cross-Tabulation
    merged = anomaly_df.merge(raw_df[["claim_id", "fraud_label"]], on="claim_id")
    n_anom = int(anomaly_df["anomaly_flag"].sum())
    fraud_in_anom = int(merged[merged["anomaly_flag"] == 1]["fraud_label"].sum())
    anom_fraud_rate = float(fraud_in_anom / n_anom) if n_anom > 0 else 0.0
    base_fraud_rate = float(merged["fraud_label"].mean())

    corr_if_fraud = float(np.corrcoef(anomaly_df["anomaly_score"], merged["fraud_label"])[0, 1])

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_claims_analyzed": len(anomaly_df),
        "anomalous_claims_count": n_anom,
        "anomalous_claims_pct": round((n_anom / len(anomaly_df)) * 100.0, 2),
        "fraud_distribution": {
            "fraud_count_in_anomalous": fraud_in_anom,
            "fraud_rate_in_anomalous_pct": round(anom_fraud_rate * 100.0, 2),
            "baseline_fraud_rate_pct": round(base_fraud_rate * 100.0, 2),
            "lift": round(anom_fraud_rate / base_fraud_rate, 2) if base_fraud_rate > 0 else 1.0,
            "correlation_anomaly_score_vs_fraud": round(corr_if_fraud, 4),
        },
        "score_statistics": {
            "mean_anomaly_score": round(float(anomaly_df["anomaly_score"].mean()), 4),
            "median_anomaly_score": round(float(anomaly_df["anomaly_score"].median()), 4),
            "max_anomaly_score": round(float(anomaly_df["anomaly_score"].max()), 4),
            "min_anomaly_score": round(float(anomaly_df["anomaly_score"].min()), 4),
        },
        "model_agreement": {
            "corr_iso_vs_lof": round(float(np.corrcoef(anomaly_df["isolation_forest_score"], anomaly_df["lof_score"])[0, 1]), 4),
            "corr_iso_vs_ocsvm": round(float(np.corrcoef(anomaly_df["isolation_forest_score"], anomaly_df["ocsvm_score"])[0, 1]), 4),
        },
    }

    out_report = REPORTS_DIR / "anomaly_detection_report.json"
    with open(out_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved anomaly detection report -> %s", out_report)

    # Print summary
    print("\n" + "=" * 65)
    print("PHASE 5 UNSUPERVISED ANOMALY DETECTION - SUMMARY")
    print("=" * 65)
    print(f"Total claims analyzed   : {report['total_claims_analyzed']}")
    print(f"Anomalous claims flagged: {report['anomalous_claims_count']} ({report['anomalous_claims_pct']}%)")
    print(f"\nFraud Rate in Anomalies : {report['fraud_distribution']['fraud_rate_in_anomalous_pct']}% (vs {report['fraud_distribution']['baseline_fraud_rate_pct']}% baseline)")
    print(f"Lift over baseline      : {report['fraud_distribution']['lift']}x")
    print(f"\nModel Agreement:")
    print(f"  Isolation Forest vs LOF        : {report['model_agreement']['corr_iso_vs_lof']}")
    print(f"  Isolation Forest vs OneClassSVM: {report['model_agreement']['corr_iso_vs_ocsvm']}")
    print("\nSample Anomalous Claims with Reasons:")
    anom_sample = anomaly_df[anomaly_df["anomaly_flag"] == 1][["claim_id", "anomaly_score", "anomaly_reason"]].head(5)
    for _, r in anom_sample.iterrows():
        print(f"  {r['claim_id']} (Score: {r['anomaly_score']:.4f}): {r['anomaly_reason']}")
    print("=" * 65)


if __name__ == "__main__":
    run_pipeline()
