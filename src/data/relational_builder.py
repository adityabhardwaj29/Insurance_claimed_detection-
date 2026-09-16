"""
src/data/relational_builder.py
------------------------------
Builds the normalised relational layer in data/relational/ from
the already-cleaned tables in data/processed/.

Design:
  - Every entity's ID is preserved exactly as it appears in data/processed/.
  - No new random IDs are minted.
  - No new relationships are invented beyond those present in source data.
  - The locations table is included as-is; it is technically orphaned in the
    schema (no FK from other tables) but included because it is in the source
    dataset. Its status is documented in the data dictionary and provenance.
  - policies carries a `date_order_invalid` flag from Phase 1 cleaning;
    that flag is preserved here.
  - invoice_ids are reused across claims (153 of 320 claims share invoices
    with at least one other claim) — this is a source-data characteristic
    that is preserved and documented, NOT corrected.

Run:
    python -m src.data.relational_builder
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PROCESSED_DIR  = ROOT / "data" / "processed"
RELATIONAL_DIR = ROOT / "data" / "relational"
PROVENANCE_DIR = ROOT / "data" / "provenance"
REPORTS_DIR    = ROOT / "reports"

for d in [RELATIONAL_DIR, PROVENANCE_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Column definitions for relational layer
# These are a subset of (or equal to) the processed columns.
# We do NOT add new columns here; Phase 3 (features) will add derived cols.
# ---------------------------------------------------------------------------

RELATIONAL_COLUMNS = {
    "claimants": [
        "claimant_id", "name", "age", "city", "gender", "marital_status"
    ],
    "policies": [
        "policy_id", "claimant_id", "start_date", "end_date",
        "policy_type", "premium", "date_order_invalid"
    ],
    "vehicles": [
        "vehicle_id", "claimant_id", "make", "vehicle_type",
        "registration_no", "model_year"
    ],
    "providers": [
        "provider_id", "provider_name", "city", "provider_type", "rating"
    ],
    "invoices": [
        "invoice_id", "provider_id", "invoice_amount", "invoice_date", "description"
    ],
    "claims": [
        "claim_id", "claimant_id", "policy_id", "vehicle_id",
        "provider_id", "invoice_id", "claim_date", "claim_amount",
        "claim_type", "status", "fraud_label", "description"
    ],
    "locations": [
        "location_id", "city", "latitude", "longitude"
    ],
}

# Canonical output filenames in data/relational/
OUTPUT_NAMES = {
    "claimants": "claimants.csv",
    "policies":  "policies.csv",
    "vehicles":  "vehicles.csv",
    "providers": "providers.csv",
    "invoices":  "invoices.csv",
    "claims":    "claims.csv",
    "locations": "locations.csv",
}

# Input filenames from data/processed/
INPUT_NAMES = {
    "claimants": "claimants_clean.csv",
    "policies":  "policies_clean.csv",
    "vehicles":  "vehicles_clean.csv",
    "providers": "providers_clean.csv",
    "invoices":  "invoices_clean.csv",
    "claims":    "claims_clean.csv",
    "locations": "locations_clean.csv",
}


def _load_processed(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / INPUT_NAMES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Processed file not found: {path}. "
            "Run `python -m src.data.pipeline` first."
        )
    return pd.read_csv(path, dtype=str)   # load as str; casting done in SQL/usage


def _select_columns(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Select only the relational columns for this entity."""
    expected = RELATIONAL_COLUMNS[name]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"[{name}] Missing columns in processed data: {missing}")
    return df[expected].copy()


def build_relational_tables() -> dict[str, pd.DataFrame]:
    """Load processed tables and project to relational column sets."""
    tables: dict[str, pd.DataFrame] = {}
    for name in OUTPUT_NAMES:
        logger.info("Building relational entity: %s", name)
        raw = _load_processed(name)
        tables[name] = _select_columns(raw, name)
        logger.info(
            "  %s: %d rows, %d cols — %s",
            name, len(tables[name]), len(tables[name].columns),
            list(tables[name].columns),
        )
    return tables


def save_relational_tables(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    """Write relational CSVs to data/relational/."""
    saved: dict[str, Path] = {}
    for name, df in tables.items():
        path = RELATIONAL_DIR / OUTPUT_NAMES[name]
        df.to_csv(path, index=False)
        saved[name] = path
        logger.info("Saved: %s (%d rows)", path.relative_to(ROOT), len(df))
    return saved


def compute_relational_stats(tables: dict[str, pd.DataFrame]) -> dict:
    """Compute statistics needed for provenance and reporting."""
    claims    = tables["claims"]
    policies  = tables["policies"]
    vehicles  = tables["vehicles"]
    invoices  = tables["invoices"]

    # Invoice reuse: how many invoices appear in more than one claim?
    invoice_use = claims["invoice_id"].value_counts()
    reused_invoices = int((invoice_use > 1).sum())
    max_reuse       = int(invoice_use.max())

    # Policy cardinality
    pol_per_claimant = policies.groupby("claimant_id").size()

    # Vehicle cardinality
    veh_per_claimant = vehicles.groupby("claimant_id").size()

    # Claims per policy
    claims_per_policy = claims.groupby("policy_id").size()

    # Policies with date_order_invalid
    n_invalid_dates = int((policies["date_order_invalid"] == "True").sum())

    return {
        "row_counts":            {n: len(t) for n, t in tables.items()},
        "invoice_reuse": {
            "invoices_referenced_by_multiple_claims": reused_invoices,
            "max_claims_per_invoice":                 max_reuse,
            "note": (
                "Some invoices are referenced by multiple claims. "
                "This is a source-data characteristic, NOT corrected."
            ),
        },
        "policies_per_claimant": {
            "min": int(pol_per_claimant.min()),
            "max": int(pol_per_claimant.max()),
            "mean": round(float(pol_per_claimant.mean()), 2),
        },
        "vehicles_per_claimant": {
            "min": int(veh_per_claimant.min()),
            "max": int(veh_per_claimant.max()),
            "mean": round(float(veh_per_claimant.mean()), 2),
        },
        "claims_per_policy": {
            "min": int(claims_per_policy.min()),
            "max": int(claims_per_policy.max()),
            "mean": round(float(claims_per_policy.mean()), 2),
        },
        "policies_with_invalid_date_order": n_invalid_dates,
        "locations_orphaned": True,
        "locations_orphan_note": (
            "locations.csv has no FK referencing it from any other table. "
            "City string matching is the only possible join. "
            "This is a source-data limitation, not modelled as a FK."
        ),
    }


def run() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.info("=" * 65)
    logger.info("PHASE 2 RELATIONAL BUILDER — %s", ts)
    logger.info("=" * 65)

    tables = build_relational_tables()
    saved  = save_relational_tables(tables)
    stats  = compute_relational_stats(tables)

    # Write a small provenance sidecar
    provenance = {
        "generated": ts,
        "source":    "data/processed/",
        "output":    "data/relational/",
        "builder":   "src/data/relational_builder.py",
        "note":      "All IDs preserved exactly from source. No new relationships invented.",
        "stats":     stats,
    }
    prov_path = PROVENANCE_DIR / "relational_provenance.json"
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    logger.info("Provenance -> %s", prov_path.relative_to(ROOT))

    print("\n" + "=" * 65)
    print("PHASE 2 RELATIONAL LAYER — COMPLETE")
    print("=" * 65)
    print(f"\nTimestamp: {ts}")
    print(f"\n{'Entity':<14} {'Rows':>6}  File")
    print("-" * 50)
    for name, path in saved.items():
        print(f"{name:<14} {len(tables[name]):>6}  {path.relative_to(ROOT)}")
    print(f"\nProvenance: {prov_path.relative_to(ROOT)}")
    print("=" * 65)


if __name__ == "__main__":
    run()
