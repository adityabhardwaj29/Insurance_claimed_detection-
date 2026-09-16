"""
src/duplicate/duplicate_detector.py
-----------------------------------
Production-style duplicate and similar claim detection module for insurance claims.

Goal:
  Identify claims that are:
    - EXACT_DUPLICATE: Identical entity, vehicle, policy, date, and amount.
    - POSSIBLE_DUPLICATE: High-confidence collision in critical operational dimensions
      (e.g., same vehicle in short time window, same policy & invoice, or near-identical attributes).
    - SIMILAR: Shared entities (reused invoice, same claimant filing multiple claims,
      or matching provider + city + claim_type + close amount).
    - NO_MATCH: Standard independent claims without suspicious overlap.

Produces:
  - data/features/duplicate_features.csv (320 rows, per-claim feature vector)
  - data/features/duplicate_pairs.csv (all pairwise candidate matches)
  - reports/duplicate_detection_report.json (evaluation metrics & distribution)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from src.duplicate.similarity import (
    categorical_similarity,
    composite_similarity,
    date_similarity,
    numeric_similarity,
)
from src.duplicate.text_similarity import hybrid_text_similarity

ROOT = Path(__file__).resolve().parent.parent.parent
RELATIONAL_DIR = ROOT / "data" / "relational"
FEATURES_DIR = ROOT / "data" / "features"
REPORTS_DIR = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Default Weights & Thresholds
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "claimant": 0.20,
    "policy": 0.15,
    "vehicle": 0.15,
    "date": 0.15,
    "amount": 0.10,
    "location": 0.05,
    "incident": 0.10,
    "invoice": 0.10,
}

# Thresholds for classification
THRESHOLDS = {
    "exact_min_score": 0.98,
    "possible_min_score": 0.65,
    "similar_min_score": 0.45,
}


class DuplicateDetector:
    """
    Deterministic insurance claim duplicate detection engine.
    Compares claims across all operational, financial, and incident dimensions.
    """

    def __init__(
        self,
        weights: Mapping[str, float] | None = None,
        max_date_diff_days: int = 60,
    ) -> None:
        self.weights = dict(weights or DEFAULT_WEIGHTS)
        self.max_date_diff_days = max_date_diff_days

    def compare_claims(self, c1: Mapping[str, Any], c2: Mapping[str, Any]) -> dict[str, Any]:
        """
        Compare two claim records and compute multi-field similarity scores,
        matching fields list, duplicate type classification, and composite score.
        """
        # 1. Claimant similarity
        claimant_id_match = categorical_similarity(c1.get("claimant_id"), c2.get("claimant_id"))
        claimant_name_sim = hybrid_text_similarity(c1.get("name"), c2.get("name"))
        claimant_sim = claimant_id_match if claimant_id_match > 0 else (0.4 * claimant_name_sim)

        # 2. Policy similarity
        policy_id_match = categorical_similarity(c1.get("policy_id"), c2.get("policy_id"))
        policy_type_match = categorical_similarity(c1.get("policy_type"), c2.get("policy_type"))
        policy_sim = policy_id_match if policy_id_match > 0 else (0.2 * policy_type_match)

        # 3. Vehicle similarity
        vehicle_id_match = categorical_similarity(c1.get("vehicle_id"), c2.get("vehicle_id"))
        reg_match = categorical_similarity(c1.get("registration_no"), c2.get("registration_no"))
        veh_type_match = categorical_similarity(c1.get("vehicle_type"), c2.get("vehicle_type"))
        vehicle_sim = vehicle_id_match if vehicle_id_match > 0 else (0.5 * reg_match + 0.1 * veh_type_match)

        # 4. Accident / Claim Date similarity
        date_sim, days_diff = date_similarity(
            c1.get("claim_date"), c2.get("claim_date"), max_days=self.max_date_diff_days
        )

        # 5. Claim Amount similarity
        amount_sim = numeric_similarity(c1.get("claim_amount"), c2.get("claim_amount"))

        # 6. Location similarity
        loc_sim = categorical_similarity(c1.get("city"), c2.get("city"))

        # 7. Incident characteristics similarity
        claim_type_match = categorical_similarity(c1.get("claim_type"), c2.get("claim_type"))
        desc_sim = hybrid_text_similarity(c1.get("description"), c2.get("description"))
        incident_sim = 0.6 * claim_type_match + 0.4 * desc_sim

        # 8. Operational / Invoice similarity
        invoice_id_match = categorical_similarity(c1.get("invoice_id"), c2.get("invoice_id"))
        provider_id_match = categorical_similarity(c1.get("provider_id"), c2.get("provider_id"))
        invoice_sim = invoice_id_match if invoice_id_match > 0 else (0.3 * provider_id_match)

        # Composite score
        components = {
            "claimant": claimant_sim,
            "policy": policy_sim,
            "vehicle": vehicle_sim,
            "date": date_sim,
            "amount": amount_sim,
            "location": loc_sim,
            "incident": incident_sim,
            "invoice": invoice_sim,
        }
        composite_score = composite_similarity(components, self.weights)

        # Compile matching field tags
        matching_fields: list[str] = []
        if claimant_id_match == 1.0:
            matching_fields.append("claimant_id")
        if policy_id_match == 1.0:
            matching_fields.append("policy_id")
        if vehicle_id_match == 1.0:
            matching_fields.append("vehicle_id")
        if invoice_id_match == 1.0:
            matching_fields.append("invoice_id")
        if provider_id_match == 1.0:
            matching_fields.append("provider_id")
        if days_diff == 0:
            matching_fields.append("exact_date")
        elif days_diff <= 7:
            matching_fields.append("close_date_7d")
        elif days_diff <= 30:
            matching_fields.append("close_date_30d")
        if amount_sim >= 0.95:
            matching_fields.append("exact_amount")
        elif amount_sim >= 0.90:
            matching_fields.append("close_amount_10pct")
        if loc_sim == 1.0:
            matching_fields.append("city")
        if claim_type_match == 1.0:
            matching_fields.append("claim_type")

        # ─────────────────────────────────────────────────────────────────────
        # Duplicate Status Classification Rules (Deterministic & Evidence-based)
        # ─────────────────────────────────────────────────────────────────────
        # 1. EXACT_DUPLICATE: Same claimant, vehicle, policy, exact date, and amount
        if (
            claimant_id_match == 1.0
            and vehicle_id_match == 1.0
            and policy_id_match == 1.0
            and days_diff == 0
            and amount_sim >= 0.95
        ):
            dup_type = "EXACT_DUPLICATE"

        # 2. POSSIBLE_DUPLICATE: High-confidence operational collision
        elif (
            (vehicle_id_match == 1.0 and days_diff <= 14)
            or (policy_id_match == 1.0 and invoice_id_match == 1.0)
            or (vehicle_id_match == 1.0 and invoice_id_match == 1.0)
            or (claimant_id_match == 1.0 and policy_id_match == 1.0 and vehicle_id_match == 1.0)
            or (composite_score >= THRESHOLDS["possible_min_score"] and len(matching_fields) >= 4)
        ):
            dup_type = "POSSIBLE_DUPLICATE"

        # 3. SIMILAR: Meaningful shared identifiers or significant collision
        elif (
            invoice_id_match == 1.0
            or vehicle_id_match == 1.0
            or policy_id_match == 1.0
            or claimant_id_match == 1.0
            or (claimant_id_match == 1.0 and days_diff <= 30)
            or (
                provider_id_match == 1.0
                and loc_sim == 1.0
                and days_diff <= 7
                and claim_type_match == 1.0
                and amount_sim >= 0.85
            )
            or (composite_score >= THRESHOLDS["similar_min_score"] and (
                claimant_id_match == 1.0 or provider_id_match == 1.0 or invoice_id_match == 1.0
            ))
        ):
            dup_type = "SIMILAR"

        else:
            dup_type = "NO_MATCH"

        dup_flag = 1 if dup_type in ("EXACT_DUPLICATE", "POSSIBLE_DUPLICATE", "SIMILAR") else 0

        return {
            "similarity_score": composite_score,
            "duplicate_type": dup_type,
            "matching_fields": ", ".join(matching_fields),
            "duplicate_flag": dup_flag,
            "days_diff": days_diff,
            "claimant_similarity": round(claimant_sim, 4),
            "policy_similarity": round(policy_sim, 4),
            "vehicle_similarity": round(vehicle_sim, 4),
            "date_similarity": round(date_sim, 4),
            "amount_similarity": round(amount_sim, 4),
            "location_similarity": round(loc_sim, 4),
            "incident_similarity": round(incident_sim, 4),
            "invoice_similarity": round(invoice_sim, 4),
            "description_similarity": round(desc_sim, 4),
            "provider_similarity": round(provider_id_match, 4),
        }

    def detect_all(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run pairwise comparison across all claims in df.

        Returns:
          1. per_claim_features: Exactly 1 row per claim (320 rows) with its top matching candidate.
          2. candidate_pairs: All unique claim pairs (c1 < c2) classified as non-NO_MATCH.
        """
        records = df.to_dict("records")
        n = len(records)
        logger.info("Running duplicate detection on %d claims (%d total pairs)", n, n * (n - 1) // 2)

        # 1. Evaluate all pairs
        all_pairs: list[dict[str, Any]] = []
        # Keep track of the best match for each claim
        best_for_claim: dict[str, dict[str, Any]] = {}

        for i in range(n):
            c1 = records[i]
            cid1 = str(c1["claim_id"])

            for j in range(i + 1, n):
                c2 = records[j]
                cid2 = str(c2["claim_id"])

                comp = self.compare_claims(c1, c2)
                score = comp["similarity_score"]
                dup_type = comp["duplicate_type"]

                # If non-trivial similarity or match, record in candidate pairs
                if dup_type != "NO_MATCH" or score >= 0.35:
                    pair_record = {
                        "claim_id_1": cid1,
                        "claim_id_2": cid2,
                        "similarity_score": score,
                        "duplicate_type": dup_type,
                        "matching_fields": comp["matching_fields"],
                        "days_diff": comp["days_diff"],
                        "amount_similarity": comp["amount_similarity"],
                        "invoice_similarity": comp["invoice_similarity"],
                        "vehicle_similarity": comp["vehicle_similarity"],
                        "claimant_similarity": comp["claimant_similarity"],
                        "fraud_1": int(c1.get("fraud_label", 0)),
                        "fraud_2": int(c2.get("fraud_label", 0)),
                    }
                    all_pairs.append(pair_record)

                # Update best match for c1
                if cid1 not in best_for_claim or score > best_for_claim[cid1]["similarity_score"]:
                    best_for_claim[cid1] = {
                        "claim_id": cid1,
                        "compared_claim_id": cid2,
                        "similarity_score": score,
                        "duplicate_type": dup_type,
                        "matching_fields": comp["matching_fields"],
                        "duplicate_flag": comp["duplicate_flag"],
                        "claimant_similarity": comp["claimant_similarity"],
                        "policy_similarity": comp["policy_similarity"],
                        "vehicle_similarity": comp["vehicle_similarity"],
                        "date_similarity": comp["date_similarity"],
                        "amount_similarity": comp["amount_similarity"],
                        "location_similarity": comp["location_similarity"],
                        "incident_similarity": comp["incident_similarity"],
                        "invoice_similarity": comp["invoice_similarity"],
                        "description_similarity": comp["description_similarity"],
                    }

                # Update best match for c2
                if cid2 not in best_for_claim or score > best_for_claim[cid2]["similarity_score"]:
                    best_for_claim[cid2] = {
                        "claim_id": cid2,
                        "compared_claim_id": cid1,
                        "similarity_score": score,
                        "duplicate_type": dup_type,
                        "matching_fields": comp["matching_fields"],
                        "duplicate_flag": comp["duplicate_flag"],
                        "claimant_similarity": comp["claimant_similarity"],
                        "policy_similarity": comp["policy_similarity"],
                        "vehicle_similarity": comp["vehicle_similarity"],
                        "date_similarity": comp["date_similarity"],
                        "amount_similarity": comp["amount_similarity"],
                        "location_similarity": comp["location_similarity"],
                        "incident_similarity": comp["incident_similarity"],
                        "invoice_similarity": comp["invoice_similarity"],
                        "description_similarity": comp["description_similarity"],
                    }

        # Build DataFrames
        features_list = [best_for_claim[str(records[i]["claim_id"])] for i in range(n)]
        features_df = pd.DataFrame(features_list)

        pairs_df = pd.DataFrame(all_pairs)
        if not pairs_df.empty:
            pairs_df = pairs_df.sort_values("similarity_score", ascending=False).reset_index(drop=True)

        logger.info(
            "Duplicate detection complete: %d per-claim rows, %d matching pairs detected",
            len(features_df),
            len(pairs_df),
        )
        return features_df, pairs_df


def load_claims_context() -> pd.DataFrame:
    """
    Loads claims joined with claimant, policy, vehicle, provider, and invoice metadata
    from data/relational/.
    """
    claims = pd.read_csv(RELATIONAL_DIR / "claims.csv")
    claimants = pd.read_csv(RELATIONAL_DIR / "claimants.csv")
    policies = pd.read_csv(RELATIONAL_DIR / "policies.csv")
    vehicles = pd.read_csv(RELATIONAL_DIR / "vehicles.csv")
    providers = pd.read_csv(RELATIONAL_DIR / "providers.csv")
    invoices = pd.read_csv(RELATIONAL_DIR / "invoices.csv")

    df = claims.merge(
        claimants[["claimant_id", "name", "city"]], on="claimant_id", how="left"
    )
    df = df.merge(
        policies[["policy_id", "policy_type", "premium"]], on="policy_id", how="left"
    )
    df = df.merge(
        vehicles[["vehicle_id", "make", "vehicle_type", "registration_no"]],
        on="vehicle_id",
        how="left",
    )
    df = df.merge(
        providers[["provider_id", "provider_type", "city"]].rename(
            columns={"city": "provider_city"}
        ),
        on="provider_id",
        how="left",
    )
    df = df.merge(
        invoices[["invoice_id", "invoice_amount", "invoice_date"]],
        on="invoice_id",
        how="left",
    )
    return df


def evaluate_duplicate_detection(
    features_df: pd.DataFrame,
    pairs_df: pd.DataFrame,
    claims_df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Computes summary metrics, cross-tabulations with ground truth fraud labels,
    and precision/recall metrics.
    """
    merged = features_df.merge(claims_df[["claim_id", "fraud_label"]], on="claim_id")

    type_counts = features_df["duplicate_type"].value_counts().to_dict()
    type_fraud_rates = (
        merged.groupby("duplicate_type")["fraud_label"]
        .agg(["count", "sum", "mean"])
        .to_dict(orient="index")
    )

    # Format type_fraud_rates cleanly
    formatted_rates = {}
    for k, v in type_fraud_rates.items():
        formatted_rates[k] = {
            "count": int(v["count"]),
            "fraud_count": int(v["sum"]),
            "fraud_rate_pct": round(float(v["mean"]) * 100.0, 2),
        }

    # High-similarity pairs analysis
    num_pairs = len(pairs_df)
    pair_type_counts = pairs_df["duplicate_type"].value_counts().to_dict() if not pairs_df.empty else {}
    pairs_with_fraud = int(((pairs_df["fraud_1"] == 1) | (pairs_df["fraud_2"] == 1)).sum()) if not pairs_df.empty else 0
    pairs_both_fraud = int(((pairs_df["fraud_1"] == 1) & (pairs_df["fraud_2"] == 1)).sum()) if not pairs_df.empty else 0

    return {
        "timestamp": datetime.now().isoformat(),
        "total_claims_scored": len(features_df),
        "total_candidate_pairs": num_pairs,
        "duplicate_type_distribution": type_counts,
        "fraud_rates_by_type": formatted_rates,
        "pairwise_metrics": {
            "total_matches": num_pairs,
            "type_counts": pair_type_counts,
            "pairs_involving_fraud_claims": pairs_with_fraud,
            "pairs_with_both_fraud_claims": pairs_both_fraud,
        },
        "statistics": {
            "mean_similarity_score": round(float(features_df["similarity_score"].mean()), 4),
            "median_similarity_score": round(float(features_df["similarity_score"].median()), 4),
            "max_similarity_score": round(float(features_df["similarity_score"].max()), 4),
            "min_similarity_score": round(float(features_df["similarity_score"].min()), 4),
        },
    }


def run_pipeline() -> None:
    """Full execution pipeline for duplicate detection."""
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading relational dataset...")
    df = load_claims_context()

    detector = DuplicateDetector()
    features_df, pairs_df = detector.detect_all(df)

    # Save per-claim feature table
    out_features = FEATURES_DIR / "duplicate_features.csv"
    features_df.to_csv(out_features, index=False)
    logger.info("Saved duplicate features -> %s (%d rows)", out_features, len(features_df))

    # Save candidate pairs table
    out_pairs = FEATURES_DIR / "duplicate_pairs.csv"
    pairs_df.to_csv(out_pairs, index=False)
    logger.info("Saved duplicate candidate pairs -> %s (%d pairs)", out_pairs, len(pairs_df))

    # Evaluation report
    report = evaluate_duplicate_detection(features_df, pairs_df, df)
    out_report = REPORTS_DIR / "duplicate_detection_report.json"
    with open(out_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved evaluation report -> %s", out_report)

    # Print summary
    print("\n" + "=" * 65)
    print("PHASE 3 DUPLICATE DETECTION - SUMMARY")
    print("=" * 65)
    print(f"Total claims evaluated     : {report['total_claims_scored']}")
    print(f"Candidate pairs detected   : {report['total_candidate_pairs']}")
    print("\nDuplicate Type Breakdown (Per Claim Top Match):")
    for dtype, count in report["duplicate_type_distribution"].items():
        rate_info = report["fraud_rates_by_type"].get(dtype, {})
        frate = rate_info.get("fraud_rate_pct", 0.0)
        fcount = rate_info.get("fraud_count", 0)
        print(f"  {dtype:<20}: {count:>4} claims | Fraud: {fcount:>3} ({frate:>5.1f}%)")
    print(f"\nMean top similarity score : {report['statistics']['mean_similarity_score']}")
    print(f"Max similarity score      : {report['statistics']['max_similarity_score']}")
    print("=" * 65)


if __name__ == "__main__":
    run_pipeline()
