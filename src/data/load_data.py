"""
src/data/load_data.py
--------------------
Loads all raw datasets from data/raw/.

Rules:
- Raw files are NEVER written to.
- Returns DataFrames with original dtypes exactly as stored.
- All callers are responsible for type conversion after loading.
"""

from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

# Expected raw filenames
RAW_FILES = {
    "claims":     "claims_raw.csv",
    "claimants":  "claimants_raw.csv",
    "policies":   "policies_raw.csv",
    "vehicles":   "vehicles_raw.csv",
    "providers":  "providers_raw.csv",
    "invoices":   "invoices_raw.csv",
    "locations":  "locations_raw.csv",
}

# Expected columns per table (for early sanity check)
EXPECTED_COLUMNS = {
    "claims":    ["claim_id", "claimant_id", "policy_id", "vehicle_id",
                  "provider_id", "invoice_id", "claim_date", "claim_amount",
                  "claim_type", "status", "fraud_label", "description"],
    "claimants": ["claimant_id", "name", "age", "city", "gender", "marital_status"],
    "policies":  ["policy_id", "claimant_id", "start_date", "end_date",
                  "policy_type", "premium"],
    "vehicles":  ["vehicle_id", "claimant_id", "make", "vehicle_type",
                  "registration_no", "model_year"],
    "providers": ["provider_id", "provider_name", "city", "provider_type", "rating"],
    "invoices":  ["invoice_id", "provider_id", "invoice_amount",
                  "invoice_date", "description"],
    "locations": ["location_id", "city", "latitude", "longitude"],
}


def load_raw_table(name: str) -> pd.DataFrame:
    """Load a single raw table by logical name.

    Parameters
    ----------
    name : str
        One of the keys in RAW_FILES.

    Returns
    -------
    pd.DataFrame
        DataFrame with original dtypes. Date columns remain as strings.
    """
    if name not in RAW_FILES:
        raise ValueError(f"Unknown table '{name}'. Available: {list(RAW_FILES)}")

    path = RAW_DIR / RAW_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")

    df = pd.read_csv(path, dtype=str)  # load everything as str first
    # Re-parse known numeric columns with explicit types to avoid dtype surprises
    df = _coerce_dtypes(name, df)

    # Verify columns match expectations
    expected = EXPECTED_COLUMNS[name]
    missing_cols = [c for c in expected if c not in df.columns]
    if missing_cols:
        raise ValueError(f"[{name}] Missing expected columns: {missing_cols}")

    logger.info("Loaded %s: %d rows, %d cols", name, len(df), len(df.columns))
    return df


def load_all_raw() -> dict[str, pd.DataFrame]:
    """Load all 7 raw tables.

    Returns
    -------
    dict
        Mapping of table name -> DataFrame.
    """
    tables = {}
    for name in RAW_FILES:
        tables[name] = load_raw_table(name)
    logger.info("All raw tables loaded: %s", list(tables.keys()))
    return tables


def _coerce_dtypes(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Re-cast columns to their correct types after string read.

    Date columns remain as strings at this stage — conversion happens
    in clean_data.py so the raw representation is never altered.
    """
    df = df.copy()

    if name == "claims":
        df["claim_amount"] = pd.to_numeric(df["claim_amount"], errors="coerce")
        df["fraud_label"]  = pd.to_numeric(df["fraud_label"],  errors="coerce").astype("Int64")

    elif name == "claimants":
        df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")

    elif name == "policies":
        df["premium"] = pd.to_numeric(df["premium"], errors="coerce")

    elif name == "vehicles":
        df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce").astype("Int64")

    elif name == "providers":
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    elif name == "invoices":
        df["invoice_amount"] = pd.to_numeric(df["invoice_amount"], errors="coerce")

    elif name == "locations":
        df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    return df


def raw_row_counts() -> dict[str, int]:
    """Return row counts for all raw files without loading full DataFrames."""
    counts = {}
    for name, fname in RAW_FILES.items():
        path = RAW_DIR / fname
        if path.exists():
            df = pd.read_csv(path, usecols=[0])
            counts[name] = len(df)
        else:
            counts[name] = -1
    return counts
