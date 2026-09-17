"""
Phase 7: Feature Merging Pipeline.
Combines ML features, duplicate features, anomaly features, and graph features
into a single final_claim_features.csv for graph-enhanced fraud detection evaluation.

Feature Groups:
  1. Traditional ML features (claim_features.csv): 21 cols derived from claim/policy/vehicle/provider tables
  2. Duplicate detection features (duplicate_features.csv): similarity scores and flags
  3. Anomaly detection features (anomaly_features.csv): Isolation Forest, LOF, OCSVM scores
  4. Graph network features (graph_features.csv): network degree, PageRank, betweenness, fraud-neighbor ratio

Integration Key: claim_id
Target Column: fraud_label (from ML features)
"""

from pathlib import Path
from typing import Optional
import pandas as pd


def merge_all_features(
    claim_features_path: str = "data/features/claim_features.csv",
    duplicate_features_path: str = "data/features/duplicate_features.csv",
    anomaly_features_path: str = "data/features/anomaly_features.csv",
    graph_features_path: str = "data/features/graph_features.csv",
    output_path: Optional[str] = "data/features/final_claim_features.csv",
) -> pd.DataFrame:
    """
    Left-joins all feature sets on claim_id. Drops feature group columns
    that duplicate or conflict with each other. Returns the merged dataset
    with claim_id and fraud_label as anchor columns.
    """
    # --- 1. Load base ML features ---
    base_df = pd.read_csv(claim_features_path)
    print(f"Base ML features: {base_df.shape}")
    assert "claim_id" in base_df.columns, "claim_features.csv must have claim_id"
    assert "fraud_label" in base_df.columns, "claim_features.csv must have fraud_label"

    # --- 2. Load and prepare duplicate features ---
    dup_df = pd.read_csv(duplicate_features_path)
    print(f"Duplicate features: {dup_df.shape}")
    # Keep only claim-level de-duplicated columns (drop compared_claim_id, matching_fields)
    dup_cols_keep = [
        "claim_id",
        "similarity_score",
        "duplicate_type",
        "duplicate_flag",
    ]
    dup_cols_keep = [c for c in dup_cols_keep if c in dup_df.columns]
    dup_df = dup_df[dup_cols_keep].drop_duplicates(subset=["claim_id"]).copy()
    # Rename to avoid conflict with base features which already has duplicate_similarity_score / duplicate_flag
    rename_map = {
        "similarity_score": "dup_similarity_score",
        "duplicate_type": "dup_type",
        "duplicate_flag": "dup_flag",
    }
    dup_df = dup_df.rename(columns={k: v for k, v in rename_map.items() if k in dup_df.columns})

    # --- 3. Load and prepare anomaly features ---
    anom_df = pd.read_csv(anomaly_features_path)
    print(f"Anomaly features: {anom_df.shape}")
    # Keep only numeric anomaly signals (drop anomaly_reason text column)
    anom_cols_keep = [
        "claim_id",
        "anomaly_score",
        "anomaly_flag",
        "isolation_forest_score",
        "lof_score",
        "ocsvm_score",
    ]
    anom_cols_keep = [c for c in anom_cols_keep if c in anom_df.columns]
    anom_df = anom_df[anom_cols_keep].drop_duplicates(subset=["claim_id"]).copy()

    # --- 4. Load graph features ---
    graph_df = pd.read_csv(graph_features_path)
    print(f"Graph features: {graph_df.shape}")
    graph_df = graph_df.drop_duplicates(subset=["claim_id"]).copy()

    # --- 5. Merge all onto base ---
    merged = base_df.copy()

    merged = merged.merge(dup_df, on="claim_id", how="left")
    merged = merged.merge(anom_df, on="claim_id", how="left")
    merged = merged.merge(graph_df, on="claim_id", how="left")

    print(f"\nMerged dataset: {merged.shape}")
    print(f"Columns: {merged.columns.tolist()}")

    null_counts = merged.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) > 0:
        print(f"\nNull counts after merge:\n{null_cols}")
    else:
        print("No null values after merge.")

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(out_p, index=False)
        print(f"\nFinal features saved: {out_p} ({len(merged)} rows, {len(merged.columns)} cols)")

    return merged


if __name__ == "__main__":
    print("=== Merging all feature sets into final_claim_features.csv ===")
    df = merge_all_features()
    print("\nFraud label distribution:")
    print(df["fraud_label"].value_counts())
