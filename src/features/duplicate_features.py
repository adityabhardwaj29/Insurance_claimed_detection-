from pathlib import Path
import pandas as pd
from src.duplicate.duplicate_detector import DuplicateDetector, load_claims_context

FEATURES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "features" / "duplicate_features.csv"


def create_duplicate_features(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Returns the duplicate features DataFrame (320 rows).
    If duplicate_features.csv exists, loads it; otherwise computes it via DuplicateDetector.
    If a DataFrame with claim_id is provided, joins on claim_id.
    """
    if FEATURES_PATH.exists():
        dup_df = pd.read_csv(FEATURES_PATH)
    else:
        context_df = load_claims_context()
        detector = DuplicateDetector()
        dup_df, _ = detector.detect_all(context_df)

    if df is not None and "claim_id" in df.columns:
        return df.merge(dup_df, on="claim_id", how="left")
    return dup_df
