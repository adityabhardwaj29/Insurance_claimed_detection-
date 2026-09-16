"""
src/models/preprocessing.py
---------------------------
Data preprocessing, column transformation, and temporal train/val/test splitting
for fraud detection machine learning models.

Avoids data leakage by:
  - Performing chronological splits by claim_date so models are evaluated on future claims.
  - Fitting preprocessors (scalers, encoders) strictly on training data only.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Default feature column lists
NUMERIC_FEATURES = [
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
]

CATEGORICAL_FEATURES = [
    "claim_type",
    "policy_type",
    "vehicle_type",
    "vehicle_make",
    "provider_type",
    "claimant_city",
]

TARGET_COL = "fraud_label"


def build_column_transformer(
    numeric_cols: Sequence[str] | None = None,
    categorical_cols: Sequence[str] | None = None,
) -> ColumnTransformer:
    """
    Constructs a scikit-learn ColumnTransformer with median imputation + standard scaling
    for numerics and most-frequent imputation + one-hot encoding for categoricals.
    """
    num_cols = list(numeric_cols or NUMERIC_FEATURES)
    cat_cols = list(categorical_cols or CATEGORICAL_FEATURES)

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    transformer = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, num_cols),
            ("cat", cat_pipeline, cat_cols),
        ],
        remainder="drop",
    )
    return transformer


def split_data_temporal(
    df: pd.DataFrame,
    date_col: str = "claim_date",
    train_ratio: float = 0.70,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits data chronologically to ensure strict prevention of future-data leakage.

    Returns:
        X_train, X_test, y_train, y_test
    """
    sorted_df = df.copy()
    sorted_df["_dt"] = pd.to_datetime(sorted_df[date_col])
    sorted_df = sorted_df.sort_values("_dt").reset_index(drop=True)

    n = len(sorted_df)
    split_idx = int(n * train_ratio)

    train_df = sorted_df.iloc[:split_idx].copy()
    test_df = sorted_df.iloc[split_idx:].copy()

    feature_cols = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in df.columns]

    X_train = train_df[feature_cols]
    y_train = train_df[TARGET_COL].astype(int)

    X_test = test_df[feature_cols]
    y_test = test_df[TARGET_COL].astype(int)

    return X_train, X_test, y_train, y_test


def split_data_train_val_test(
    df: pd.DataFrame,
    date_col: str = "claim_date",
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Splits data chronologically into train (60%), validation (20%), and test (20%).
    """
    sorted_df = df.copy()
    sorted_df["_dt"] = pd.to_datetime(sorted_df[date_col])
    sorted_df = sorted_df.sort_values("_dt").reset_index(drop=True)

    n = len(sorted_df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = sorted_df.iloc[:train_end]
    val_df = sorted_df.iloc[train_end:val_end]
    test_df = sorted_df.iloc[val_end:]

    feature_cols = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in df.columns]

    X_train = train_df[feature_cols]
    y_train = train_df[TARGET_COL].astype(int)

    X_val = val_df[feature_cols]
    y_val = val_df[TARGET_COL].astype(int)

    X_test = test_df[feature_cols]
    y_test = test_df[TARGET_COL].astype(int)

    return X_train, X_val, X_test, y_train, y_val, y_test
