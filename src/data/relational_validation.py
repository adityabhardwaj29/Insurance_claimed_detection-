"""
src/data/relational_validation.py
-----------------------------------
Relational-layer validation checks.

Checks every entity in data/relational/ for:
  - Primary key uniqueness
  - Null primary keys
  - Foreign key consistency (orphan detection)
  - Duplicate row detection (full row, not just PK)
  - ID pattern format
  - Categorical value validity
  - Numeric range validity

Run:
    python -m src.data.relational_validation
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

RELATIONAL_DIR = ROOT / "data" / "relational"
REPORTS_DIR    = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ── Expected sets ─────────────────────────────────────────────────────────────
VALID_CLAIM_TYPES     = {"Theft", "Glass Damage", "Fire", "Accident", "Natural Disaster"}
VALID_STATUSES        = {"Open", "Approved", "Under Review", "Rejected"}
VALID_POLICY_TYPES    = {"Comprehensive", "Zero Dep", "Third Party"}
VALID_VEHICLE_TYPES   = {"MUV", "Sedan", "Hatchback", "SUV"}
VALID_MAKES           = {"Tata", "Maruti", "Hyundai", "Mahindra", "Honda"}
VALID_PROVIDER_TYPES  = {"Surveyor", "Dealer", "Garage", "Hospital"}
VALID_GENDERS         = {"M", "F"}
VALID_MARITAL_STATUS  = {"Married", "Single"}
VALID_CITIES          = {"Mumbai", "Pune", "Delhi", "Ahmedabad", "Surat"}
VALID_FRAUD_LABELS    = {"0", "1", 0, 1}

ID_PATTERNS = {
    "claim_id":    r"^CLM\d{5}$",
    "claimant_id": r"^CLT\d{4}$",
    "policy_id":   r"^POL\d{4}$",
    "vehicle_id":  r"^VEH\d{4}$",
    "provider_id": r"^PRV\d{3}$",
    "invoice_id":  r"^INV\d{5}$",
    "location_id": r"^LOC\d{3}$",
}


def _chk(passed: bool, name: str, details: str, failures: list = None) -> dict:
    return {
        "check":    name,
        "passed":   passed,
        "details":  details,
        "failures": (failures or [])[:20],
    }


def _load(name: str) -> pd.DataFrame:
    path = RELATIONAL_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Relational file not found: {path}. "
            "Run `python -m src.data.relational_builder` first."
        )
    return pd.read_csv(path, dtype=str)


# ── Check functions ──────────────────────────────────────────────────────────

def chk_pk_unique(df: pd.DataFrame, pk: str, table: str) -> dict:
    dupes = df[df.duplicated(subset=[pk], keep=False)][pk].tolist()
    return _chk(
        not dupes,
        f"{table}.pk_unique_{pk}",
        f"{len(dupes)} duplicate {pk} values" if dupes else "PASS",
        dupes,
    )


def chk_pk_not_null(df: pd.DataFrame, pk: str, table: str) -> dict:
    n = df[pk].isna().sum()
    return _chk(n == 0, f"{table}.pk_not_null_{pk}",
                f"{n} null {pk}" if n else "PASS")


def chk_no_full_row_duplicates(df: pd.DataFrame, table: str) -> dict:
    n = df.duplicated(keep=False).sum()
    return _chk(n == 0, f"{table}.no_full_row_duplicates",
                f"{n} fully-duplicate rows" if n else "PASS")


def chk_fk(child: pd.DataFrame, child_col: str,
           parent: pd.DataFrame, parent_col: str,
           child_table: str, parent_table: str) -> dict:
    orphans = child.loc[
        ~child[child_col].isin(parent[parent_col].dropna()), child_col
    ].tolist()
    return _chk(
        not orphans,
        f"{child_table}.{child_col} → {parent_table}.{parent_col}",
        f"{len(orphans)} FK orphan(s)" if orphans else "PASS",
        orphans,
    )


def chk_id_pattern(df: pd.DataFrame, col: str, table: str) -> dict:
    pattern = ID_PATTERNS.get(col)
    if not pattern:
        return _chk(True, f"{table}.{col}_pattern", "No pattern defined — skip")
    valid = df[col].str.match(pattern, na=False)
    bad = df.loc[~valid, col].tolist()
    return _chk(not bad, f"{table}.{col}_pattern",
                f"{len(bad)} non-matching {col}" if bad else "PASS", bad)


def chk_categorical(df: pd.DataFrame, col: str, valid: set, table: str) -> dict:
    non_null = df[col].dropna()
    bad = non_null[~non_null.isin(valid)].unique().tolist()
    return _chk(not bad, f"{table}.{col}_valid_values",
                f"Invalid: {bad}" if bad else "PASS", bad)


def chk_positive_numeric(df: pd.DataFrame, col: str, table: str) -> dict:
    vals = pd.to_numeric(df[col], errors="coerce").dropna()
    bad = vals[vals <= 0].tolist()
    return _chk(not bad, f"{table}.{col}_positive",
                f"{len(bad)} non-positive" if bad else "PASS", bad[:10])


def chk_range(df: pd.DataFrame, col: str, lo: float, hi: float, table: str) -> dict:
    vals = pd.to_numeric(df[col], errors="coerce").dropna()
    bad = vals[(vals < lo) | (vals > hi)].tolist()
    return _chk(not bad, f"{table}.{col}_range_{lo}_{hi}",
                f"{len(bad)} outside [{lo},{hi}]" if bad else "PASS", bad[:10])


def chk_date_parseable(df: pd.DataFrame, col: str, table: str) -> dict:
    parsed = pd.to_datetime(df[col], errors="coerce")
    n_nat = parsed.isna().sum()
    n_ok  = len(df) - n_nat
    return _chk(n_nat == 0, f"{table}.{col}_date_parseable",
                f"{n_nat} unparseable dates (parsed {n_ok}/{len(df)})" if n_nat else "PASS")


def chk_date_order(df: pd.DataFrame, start: str, end: str, table: str) -> dict:
    s = pd.to_datetime(df[start], errors="coerce")
    e = pd.to_datetime(df[end],   errors="coerce")
    both = s.notna() & e.notna()
    bad_idx = df.index[both & (e <= s)].tolist()
    # Retrieve policy_ids if available
    id_col = "policy_id" if "policy_id" in df.columns else df.columns[0]
    bad_ids = df.loc[bad_idx, id_col].tolist() if bad_idx else []
    return _chk(not bad_idx, f"{table}.{start}_before_{end}",
                f"{len(bad_idx)} rows with {end} <= {start}: {bad_ids}" if bad_idx else "PASS",
                bad_ids)


def chk_fraud_label(df: pd.DataFrame) -> dict:
    non_null = df["fraud_label"].dropna()
    bad = non_null[~non_null.isin({"0", "1"})].tolist()
    return _chk(not bad, "claims.fraud_label_binary_values",
                f"Invalid labels: {bad}" if bad else "PASS", bad)


# ── Master runner ─────────────────────────────────────────────────────────────

def validate_relational() -> dict[str, Any]:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: list[dict] = []

    # Load all tables
    tables = {n: _load(n) for n in
              ["claimants", "policies", "vehicles", "providers",
               "invoices", "claims", "locations"]}
    claimants = tables["claimants"]
    policies  = tables["policies"]
    vehicles  = tables["vehicles"]
    providers = tables["providers"]
    invoices  = tables["invoices"]
    claims    = tables["claims"]
    locations = tables["locations"]

    # ── PK uniqueness ──────────────────────────────────────────────────────
    for tbl, df, pk in [
        ("claimants", claimants, "claimant_id"),
        ("policies",  policies,  "policy_id"),
        ("vehicles",  vehicles,  "vehicle_id"),
        ("providers", providers, "provider_id"),
        ("invoices",  invoices,  "invoice_id"),
        ("claims",    claims,    "claim_id"),
        ("locations", locations, "location_id"),
    ]:
        results.append(chk_pk_unique(df, pk, tbl))
        results.append(chk_pk_not_null(df, pk, tbl))

    # ── Full-row duplicates ────────────────────────────────────────────────
    for tbl, df in tables.items():
        results.append(chk_no_full_row_duplicates(df, tbl))

    # ── ID patterns ───────────────────────────────────────────────────────
    for tbl, df, col in [
        ("claimants", claimants, "claimant_id"),
        ("policies",  policies,  "policy_id"),
        ("vehicles",  vehicles,  "vehicle_id"),
        ("providers", providers, "provider_id"),
        ("invoices",  invoices,  "invoice_id"),
        ("claims",    claims,    "claim_id"),
        ("locations", locations, "location_id"),
    ]:
        results.append(chk_id_pattern(df, col, tbl))

    # ── FK integrity ──────────────────────────────────────────────────────
    fk_checks = [
        (claims,   "claimant_id", claimants, "claimant_id", "claims",   "claimants"),
        (claims,   "policy_id",   policies,  "policy_id",   "claims",   "policies"),
        (claims,   "vehicle_id",  vehicles,  "vehicle_id",  "claims",   "vehicles"),
        (claims,   "provider_id", providers, "provider_id", "claims",   "providers"),
        (claims,   "invoice_id",  invoices,  "invoice_id",  "claims",   "invoices"),
        (policies, "claimant_id", claimants, "claimant_id", "policies", "claimants"),
        (vehicles, "claimant_id", claimants, "claimant_id", "vehicles", "claimants"),
        (invoices, "provider_id", providers, "provider_id", "invoices", "providers"),
    ]
    for child, cc, parent, pc, ct, pt in fk_checks:
        results.append(chk_fk(child, cc, parent, pc, ct, pt))

    # ── Categorical values ────────────────────────────────────────────────
    results += [
        chk_categorical(claims,    "claim_type",     VALID_CLAIM_TYPES,    "claims"),
        chk_categorical(claims,    "status",          VALID_STATUSES,       "claims"),
        chk_categorical(claimants, "gender",          VALID_GENDERS,        "claimants"),
        chk_categorical(claimants, "marital_status",  VALID_MARITAL_STATUS, "claimants"),
        chk_categorical(claimants, "city",            VALID_CITIES,         "claimants"),
        chk_categorical(providers, "city",            VALID_CITIES,         "providers"),
        chk_categorical(providers, "provider_type",   VALID_PROVIDER_TYPES, "providers"),
        chk_categorical(policies,  "policy_type",     VALID_POLICY_TYPES,   "policies"),
        chk_categorical(vehicles,  "vehicle_type",    VALID_VEHICLE_TYPES,  "vehicles"),
        chk_categorical(vehicles,  "make",            VALID_MAKES,          "vehicles"),
    ]

    # ── Numeric ranges ────────────────────────────────────────────────────
    results += [
        chk_positive_numeric(claims,   "claim_amount",   "claims"),
        chk_positive_numeric(policies, "premium",        "policies"),
        chk_positive_numeric(invoices, "invoice_amount", "invoices"),
        chk_range(claimants, "age",        18,   100,  "claimants"),
        chk_range(vehicles,  "model_year", 1990, 2026, "vehicles"),
        chk_range(providers, "rating",     0,    5,    "providers"),
    ]

    # ── Dates ─────────────────────────────────────────────────────────────
    results += [
        chk_date_parseable(claims,   "claim_date",    "claims"),
        chk_date_parseable(policies, "start_date",    "policies"),
        chk_date_parseable(policies, "end_date",      "policies"),
        chk_date_parseable(invoices, "invoice_date",  "invoices"),
        chk_date_order(policies, "start_date", "end_date", "policies"),
    ]

    # ── Fraud label ───────────────────────────────────────────────────────
    results.append(chk_fraud_label(claims))

    # ── Orphan check: locations ───────────────────────────────────────────
    # locations is legitimately orphaned — we document this rather than fail
    results.append(_chk(
        True,
        "locations.orphaned_by_design",
        (
            "locations has no FK from any other table. "
            "City string matching is the only join path. "
            "Documented in data dictionary as a source-data limitation."
        ),
    ))

    # ── Invoice reuse (informational, not a failure) ──────────────────────
    invoice_use = claims["invoice_id"].value_counts()
    n_reused = int((invoice_use > 1).sum())
    results.append(_chk(
        True,
        "claims.invoice_reuse_documented",
        (
            f"{n_reused} invoice_ids are referenced by more than one claim. "
            "This is a source-data characteristic, preserved as-is."
        ),
    ))

    # ── Summary ───────────────────────────────────────────────────────────
    total   = len(results)
    passed  = sum(1 for r in results if r["passed"])
    failed  = total - passed
    failed_checks = [r for r in results if not r["passed"]]

    report = {
        "generated":   ts,
        "source":      "data/relational/",
        "summary": {
            "total_checks": total,
            "passed":       passed,
            "failed":       failed,
            "all_passed":   failed == 0,
        },
        "failed_checks": failed_checks,
        "checks":        results,
    }

    if failed:
        logger.warning("Relational validation: %d/%d FAILED", failed, total)
        for c in failed_checks:
            logger.warning("  FAIL %s: %s", c["check"], c["details"])
    else:
        logger.info("Relational validation: all %d checks passed", total)

    return report


def run() -> None:
    report = validate_relational()
    out = REPORTS_DIR / "relational_validation_report.json"

    def _json_default(obj):
        import numpy as np
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        raise TypeError(f"Not JSON serializable: {type(obj)}")

    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=_json_default)
    logger.info("Report saved -> %s", out)

    s = report["summary"]
    print(f"\nRelational Validation: {s['passed']}/{s['total_checks']} checks passed")
    if s["failed"]:
        print(f"FAILED ({s['failed']}):")
        for c in report["failed_checks"]:
            print(f"  FAIL {c['check']}: {c['details']}")
    else:
        print("All checks passed ✅")


if __name__ == "__main__":
    run()
