"""
src/features/claim_features.py
------------------------------
Generates verifiable, reproducible claim-level features from normalized relational tables.
Avoids data leakage by calculating temporal metrics relative to historical claim dates.

Output:
  data/features/claim_features.csv (320 rows, 1 per claim)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
RELATIONAL_DIR = ROOT / "data" / "relational"
FEATURES_DIR = ROOT / "data" / "features"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def build_claim_features() -> pd.DataFrame:
    """
    Assembles relational entities and computes reproducible claim-level features.
    """
    logger.info("Loading relational data for claim feature engineering...")
    claims = pd.read_csv(RELATIONAL_DIR / "claims.csv")
    claimants = pd.read_csv(RELATIONAL_DIR / "claimants.csv")
    policies = pd.read_csv(RELATIONAL_DIR / "policies.csv")
    vehicles = pd.read_csv(RELATIONAL_DIR / "vehicles.csv")
    providers = pd.read_csv(RELATIONAL_DIR / "providers.csv")
    invoices = pd.read_csv(RELATIONAL_DIR / "invoices.csv")

    dup_path = FEATURES_DIR / "duplicate_features.csv"
    if dup_path.exists():
        duplicates = pd.read_csv(dup_path)
    else:
        from src.duplicate.duplicate_detector import DuplicateDetector, load_claims_context
        detector = DuplicateDetector()
        duplicates, _ = detector.detect_all(load_claims_context())

    # Parse dates
    claims["claim_dt"] = pd.to_datetime(claims["claim_date"])
    max_observation_date = claims["claim_dt"].max()

    # Join contextual dimensions
    df = claims.merge(
        claimants[["claimant_id", "age", "city", "gender"]].rename(
            columns={"age": "claimant_age", "city": "claimant_city"}
        ),
        on="claimant_id",
        how="left",
    )
    df = df.merge(
        policies[["policy_id", "policy_type", "premium", "start_date"]].rename(
            columns={"start_date": "policy_start_date"}
        ),
        on="policy_id",
        how="left",
    )
    df = df.merge(
        vehicles[["vehicle_id", "make", "vehicle_type", "model_year"]].rename(
            columns={"make": "vehicle_make"}
        ),
        on="vehicle_id",
        how="left",
    )
    df = df.merge(
        providers[["provider_id", "provider_type", "rating"]].rename(
            columns={"rating": "provider_rating"}
        ),
        on="provider_id",
        how="left",
    )
    df = df.merge(
        invoices[["invoice_id", "invoice_amount"]],
        on="invoice_id",
        how="left",
    )
    df = df.merge(
        duplicates[["claim_id", "similarity_score", "duplicate_flag"]].rename(
            columns={"similarity_score": "duplicate_similarity_score"}
        ),
        on="claim_id",
        how="left",
    )

    # Chronological sort for historical frequency calculation (no future leakage!)
    df = df.sort_values("claim_dt").reset_index(drop=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Feature Derivations
    # ─────────────────────────────────────────────────────────────────────────
    # 1. Claim age in days relative to end of dataset
    df["claim_age_days"] = (max_observation_date - df["claim_dt"]).dt.days

    # 2. Days since policy start (early claims post-inception can indicate adverse selection)
    policy_start_dt = pd.to_datetime(df["policy_start_date"], errors="coerce")
    days_since_start = (df["claim_dt"] - policy_start_dt).dt.days
    df["days_since_policy_start"] = days_since_start.fillna(0).clip(lower=0)

    # 3. Financial ratios
    df["amount_to_premium_ratio"] = (
        df["claim_amount"] / df["premium"].replace(0, np.nan)
    ).fillna(1.0).round(4)

    df["invoice_to_claim_ratio"] = (
        df["invoice_amount"] / df["claim_amount"].replace(0, np.nan)
    ).fillna(1.0).round(4)

    # 4. Vehicle age in years
    df["vehicle_age"] = (2026 - df["model_year"]).clip(lower=0)

    # 5. Cumulative claimant claim frequency up to this claim's point in time
    df["claimant_claim_frequency"] = df.groupby("claimant_id").cumcount() + 1

    # 6. Provider historical claim volume up to this claim's point in time
    df["provider_claim_volume"] = df.groupby("provider_id").cumcount() + 1

    # Select and order final feature columns
    feature_columns = [
        "claim_id",
        "claim_date",
        "claim_amount",
        "claim_age_days",
        "days_since_policy_start",
        "amount_to_premium_ratio",
        "invoice_to_claim_ratio",
        "claimant_claim_frequency",
        "provider_claim_volume",
        "vehicle_age",
        "claimant_age",
        "provider_rating",
        "duplicate_similarity_score",
        "duplicate_flag",
        "claim_type",
        "policy_type",
        "vehicle_type",
        "vehicle_make",
        "provider_type",
        "claimant_city",
        "fraud_label",
    ]
    out_df = df[feature_columns].sort_values("claim_id").reset_index(drop=True)
    return out_df


def save_claim_features() -> Path:
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    df = build_claim_features()
    out_path = FEATURES_DIR / "claim_features.csv"
    df.to_csv(out_path, index=False)
    logger.info("Saved claim features -> %s (%d rows, %d cols)", out_path, len(df), len(df.columns))
    return out_path


def create_claim_features(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Wrapper function matching project convention."""
    out_path = FEATURES_DIR / "claim_features.csv"
    if not out_path.exists():
        save_claim_features()
    features = pd.read_csv(out_path)
    if df is not None and "claim_id" in df.columns:
        return df.merge(features, on="claim_id", how="left")
    return features


if __name__ == "__main__":
    save_claim_features()
