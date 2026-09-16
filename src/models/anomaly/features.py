"""
src/models/anomaly/features.py
------------------------------
Feature extraction module for unsupervised anomaly detection in insurance claims.

Constructs operational, financial, and frequency features without using target labels (unsupervised).
Dataset Limitation Note:
  Fields such as 'injury_count' and 'witness_count' are not present in the master
  dataset and are strictly omitted per project reproducibility rules rather than fabricated.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RELATIONAL_DIR = ROOT / "data" / "relational"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

ANOMALY_FEATURE_COLS = [
    "claim_amount",
    "amount_to_premium_ratio",
    "days_since_policy_start",
    "claimant_vehicle_count",
    "claimant_policy_count",
    "claimant_claim_count",
    "provider_claim_count",
    "location_claim_count",
    "invoice_to_claim_ratio",
    "vehicle_age",
    "claimant_age",
    "provider_rating",
]


def extract_anomaly_features() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts unsupervised anomaly features from data/relational/.

    Returns:
        (features_df, raw_context_df)
        features_df contains claim_id and the scaled/unscaled numeric features.
    """
    logger.info("Extracting anomaly features from relational layer...")
    claims = pd.read_csv(RELATIONAL_DIR / "claims.csv")
    claimants = pd.read_csv(RELATIONAL_DIR / "claimants.csv")
    policies = pd.read_csv(RELATIONAL_DIR / "policies.csv")
    vehicles = pd.read_csv(RELATIONAL_DIR / "vehicles.csv")
    providers = pd.read_csv(RELATIONAL_DIR / "providers.csv")
    invoices = pd.read_csv(RELATIONAL_DIR / "invoices.csv")

    # Aggregate entity counts
    c_veh = vehicles.groupby("claimant_id")["vehicle_id"].count().rename("claimant_vehicle_count")
    c_pol = policies.groupby("claimant_id")["policy_id"].count().rename("claimant_policy_count")
    c_clm = claims.groupby("claimant_id")["claim_id"].count().rename("claimant_claim_count")
    prv_clm = claims.groupby("provider_id")["claim_id"].count().rename("provider_claim_count")

    # Join contextual dimensions
    df = claims.merge(
        claimants[["claimant_id", "age", "city"]].rename(columns={"age": "claimant_age"}),
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
        vehicles[["vehicle_id", "make", "vehicle_type", "model_year"]],
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

    df = df.merge(c_veh, on="claimant_id", how="left")
    df = df.merge(c_pol, on="claimant_id", how="left")
    df = df.merge(c_clm, on="claimant_id", how="left")
    df = df.merge(prv_clm, on="provider_id", how="left")

    loc_clm = df.groupby("city")["claim_id"].transform("count").rename("location_claim_count")
    df["location_claim_count"] = loc_clm

    # Derived temporal and financial metrics
    df["claim_dt"] = pd.to_datetime(df["claim_date"])
    df["policy_start_dt"] = pd.to_datetime(df["policy_start_date"], errors="coerce")
    df["days_since_policy_start"] = (df["claim_dt"] - df["policy_start_dt"]).dt.days.fillna(0).clip(lower=0)

    df["amount_to_premium_ratio"] = (
        df["claim_amount"] / df["premium"].replace(0, np.nan)
    ).fillna(1.0).round(4)

    df["invoice_to_claim_ratio"] = (
        df["invoice_amount"] / df["claim_amount"].replace(0, np.nan)
    ).fillna(1.0).round(4)

    df["vehicle_age"] = (2026 - df["model_year"]).clip(lower=0)

    # Impute missing values with medians if any
    for col in ANOMALY_FEATURE_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    features_df = df[["claim_id"] + ANOMALY_FEATURE_COLS].copy()
    logger.info("Extracted %d claims with %d anomaly features", len(features_df), len(ANOMALY_FEATURE_COLS))
    return features_df, df
