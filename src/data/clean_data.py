"""
src/data/clean_data.py
----------------------
Table-specific cleaning functions.

Each function:
  - Receives the raw DataFrame for one table.
  - Returns a cleaned DataFrame + a cleaning_log dict.
  - NEVER writes to data/raw/.
  - NEVER alters fraud_label values.
  - Documents every change made.

Cleaning philosophy:
  - Strip whitespace from all string columns.
  - Normalize categorical values to the known valid set.
  - Parse date columns to datetime64.
  - Flag impossible numeric values as pd.NA (do not guess replacements).
  - Drop rows only for duplicate primary keys (keeping first occurrence).
  - Document every row/value flagged or changed.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from src.data.standardize import (
    VALID_CITIES,
    clamp_age,
    clamp_model_year,
    clamp_rating,
    clamp_to_positive,
    normalize_city,
    normalize_claim_type,
    normalize_gender,
    normalize_marital_status,
    normalize_policy_type,
    normalize_provider_type,
    normalize_status,
    normalize_vehicle_type,
    parse_date_column,
    strip_whitespace,
    validate_id_pattern,
    ID_PATTERNS,
)

logger = logging.getLogger(__name__)


def _make_log(table: str, raw_rows: int) -> dict[str, Any]:
    return {
        "table": table,
        "raw_rows": raw_rows,
        "duplicate_pk_removed": 0,
        "invalid_ids": {},
        "whitespace_stripped": {},
        "categorical_normalized": {},
        "invalid_categoricals_flagged": {},
        "dates_parsed": {},
        "invalid_dates_flagged": {},
        "numeric_range_violations": {},
        "other_flags": [],
        "fraud_label_unchanged": True,
        "final_rows": 0,
    }


# ---------------------------------------------------------------------------
# Per-table cleaning functions
# ---------------------------------------------------------------------------

def clean_claims(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the claims table.

    Fraud label is NEVER modified. It is copied as-is from the source.
    """
    log = _make_log("claims", len(df))
    out = df.copy()

    # ── 1. Strip whitespace from all object columns ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── 2. Drop duplicate primary keys (claim_id), keep first ──
    dupes = out.duplicated(subset=["claim_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["claim_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)
        logger.warning("claims: removed %d duplicate claim_id rows", dupes)

    # ── 3. Validate ID format ──
    for id_col in ["claim_id", "claimant_id", "policy_id", "vehicle_id",
                   "provider_id", "invoice_id"]:
        pattern = ID_PATTERNS.get(id_col)
        if pattern:
            valid_mask = validate_id_pattern(out[id_col], pattern)
            n_invalid = (~valid_mask).sum()
            if n_invalid:
                log["invalid_ids"][id_col] = int(n_invalid)
                logger.warning("claims: %d invalid %s values", n_invalid, id_col)

    # ── 4. Normalize categoricals ──
    for col, fn in [
        ("claim_type", normalize_claim_type),
        ("status",     normalize_status),
    ]:
        original = out[col].copy()
        out[col] = fn(out[col])
        n_changed = (original != out[col]).sum()
        n_invalid = out[col].isna().sum() - original.isna().sum()
        if n_changed:
            log["categorical_normalized"][col] = int(n_changed)
        if n_invalid > 0:
            log["invalid_categoricals_flagged"][col] = int(n_invalid)
            logger.warning("claims: %d invalid '%s' values set to NA", n_invalid, col)

    # ── 5. Parse claim_date ──
    out["claim_date"] = parse_date_column(out["claim_date"], "claim_date")
    nat_count = out["claim_date"].isna().sum()
    log["dates_parsed"]["claim_date"] = {"parsed_ok": int(len(out) - nat_count),
                                          "nat_count":  int(nat_count)}
    if nat_count:
        log["invalid_dates_flagged"]["claim_date"] = int(nat_count)
        logger.warning("claims: %d unparseable claim_date values", nat_count)

    # ── 6. Validate claim_amount > 0 ──
    n_before_na = out["claim_amount"].isna().sum()
    out["claim_amount"] = clamp_to_positive(out["claim_amount"], "claim_amount")
    n_flagged = out["claim_amount"].isna().sum() - n_before_na
    if n_flagged:
        log["numeric_range_violations"]["claim_amount"] = int(n_flagged)
        logger.warning("claims: %d claim_amount values <= 0 set to NA", n_flagged)

    # ── 7. Preserve fraud_label exactly ──
    # fraud_label was already loaded as Int64 — ensure no coercion happened
    assert out["fraud_label"].isin([0, 1, pd.NA]).all(), \
        "fraud_label contains unexpected values — aborting"
    log["fraud_label_unchanged"] = True

    log["final_rows"] = int(len(out))
    logger.info("clean_claims: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_claimants(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the claimants table."""
    log = _make_log("claimants", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["claimant_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["claimant_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── ID format ──
    valid_mask = validate_id_pattern(out["claimant_id"], ID_PATTERNS["claimant_id"])
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        log["invalid_ids"]["claimant_id"] = int(n_invalid)

    # ── Normalize gender ──
    original = out["gender"].copy()
    out["gender"] = normalize_gender(out["gender"])
    n_inv = out["gender"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["gender"] = int(n_inv)

    # ── Normalize marital_status ──
    original = out["marital_status"].copy()
    out["marital_status"] = normalize_marital_status(out["marital_status"])
    n_inv = out["marital_status"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["marital_status"] = int(n_inv)

    # ── Normalize city ──
    original = out["city"].copy()
    out["city"] = normalize_city(out["city"], VALID_CITIES)
    n_inv = out["city"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["city"] = int(n_inv)

    # ── Age range [18, 100] ──
    n_before = out["age"].isna().sum()
    out["age"] = clamp_age(out["age"])
    n_flagged = out["age"].isna().sum() - n_before
    if n_flagged:
        log["numeric_range_violations"]["age"] = int(n_flagged)

    log["final_rows"] = int(len(out))
    logger.info("clean_claimants: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_policies(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the policies table."""
    log = _make_log("policies", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["policy_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["policy_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── ID format ──
    valid_mask = validate_id_pattern(out["policy_id"], ID_PATTERNS["policy_id"])
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        log["invalid_ids"]["policy_id"] = int(n_invalid)

    # ── Normalize policy_type ──
    original = out["policy_type"].copy()
    out["policy_type"] = normalize_policy_type(out["policy_type"])
    n_inv = out["policy_type"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["policy_type"] = int(n_inv)

    # ── Parse dates ──
    out["start_date"] = parse_date_column(out["start_date"], "start_date")
    out["end_date"]   = parse_date_column(out["end_date"],   "end_date")
    for dcol in ["start_date", "end_date"]:
        nat = out[dcol].isna().sum()
        log["dates_parsed"][dcol] = {"parsed_ok": int(len(out) - nat), "nat_count": int(nat)}
        if nat:
            log["invalid_dates_flagged"][dcol] = int(nat)

    # ── Flag rows where end_date <= start_date ──
    invalid_range_mask = (
        out["start_date"].notna() & out["end_date"].notna() &
        (out["end_date"] <= out["start_date"])
    )
    n_inv_range = int(invalid_range_mask.sum())
    if n_inv_range:
        log["other_flags"].append(
            f"{n_inv_range} rows where end_date <= start_date "
            f"(policy_ids: {out.loc[invalid_range_mask, 'policy_id'].tolist()})"
        )
        logger.warning(
            "policies: %d rows with end_date <= start_date. "
            "Flagged in quality report. NOT removed (FK used by claims).",
            n_inv_range,
        )
        # Add flag column so downstream can filter if needed
        out["date_order_invalid"] = invalid_range_mask.astype(bool)
    else:
        out["date_order_invalid"] = False

    # ── Validate premium > 0 ──
    n_before = out["premium"].isna().sum()
    out["premium"] = clamp_to_positive(out["premium"], "premium")
    n_flagged = out["premium"].isna().sum() - n_before
    if n_flagged:
        log["numeric_range_violations"]["premium"] = int(n_flagged)

    log["final_rows"] = int(len(out))
    logger.info("clean_policies: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_vehicles(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the vehicles table."""
    log = _make_log("vehicles", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["vehicle_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["vehicle_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── ID format ──
    valid_mask = validate_id_pattern(out["vehicle_id"], ID_PATTERNS["vehicle_id"])
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        log["invalid_ids"]["vehicle_id"] = int(n_invalid)

    # ── Normalize vehicle_type ──
    original = out["vehicle_type"].copy()
    out["vehicle_type"] = normalize_vehicle_type(out["vehicle_type"])
    n_inv = out["vehicle_type"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["vehicle_type"] = int(n_inv)

    # ── Model year [1990, 2026] ──
    n_before = out["model_year"].isna().sum()
    out["model_year"] = clamp_model_year(out["model_year"])
    n_flagged = out["model_year"].isna().sum() - n_before
    if n_flagged:
        log["numeric_range_violations"]["model_year"] = int(n_flagged)

    log["final_rows"] = int(len(out))
    logger.info("clean_vehicles: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_providers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the providers table."""
    log = _make_log("providers", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["provider_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["provider_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── ID format ──
    valid_mask = validate_id_pattern(out["provider_id"], ID_PATTERNS["provider_id"])
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        log["invalid_ids"]["provider_id"] = int(n_invalid)

    # ── Normalize provider_type ──
    original = out["provider_type"].copy()
    out["provider_type"] = normalize_provider_type(out["provider_type"])
    n_inv = out["provider_type"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["provider_type"] = int(n_inv)

    # ── Normalize city ──
    original = out["city"].copy()
    out["city"] = normalize_city(out["city"], VALID_CITIES)
    n_inv = out["city"].isna().sum() - original.isna().sum()
    if n_inv > 0:
        log["invalid_categoricals_flagged"]["city"] = int(n_inv)

    # ── Rating [0, 5] ──
    n_before = out["rating"].isna().sum()
    out["rating"] = clamp_rating(out["rating"])
    n_flagged = out["rating"].isna().sum() - n_before
    if n_flagged:
        log["numeric_range_violations"]["rating"] = int(n_flagged)

    log["final_rows"] = int(len(out))
    logger.info("clean_providers: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_invoices(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the invoices table."""
    log = _make_log("invoices", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["invoice_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["invoice_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── ID format ──
    valid_mask = validate_id_pattern(out["invoice_id"], ID_PATTERNS["invoice_id"])
    n_invalid = (~valid_mask).sum()
    if n_invalid:
        log["invalid_ids"]["invoice_id"] = int(n_invalid)

    # ── Parse invoice_date ──
    out["invoice_date"] = parse_date_column(out["invoice_date"], "invoice_date")
    nat = out["invoice_date"].isna().sum()
    log["dates_parsed"]["invoice_date"] = {"parsed_ok": int(len(out) - nat), "nat_count": int(nat)}
    if nat:
        log["invalid_dates_flagged"]["invoice_date"] = int(nat)

    # ── Validate invoice_amount > 0 ──
    n_before = out["invoice_amount"].isna().sum()
    out["invoice_amount"] = clamp_to_positive(out["invoice_amount"], "invoice_amount")
    n_flagged = out["invoice_amount"].isna().sum() - n_before
    if n_flagged:
        log["numeric_range_violations"]["invoice_amount"] = int(n_flagged)

    log["final_rows"] = int(len(out))
    logger.info("clean_invoices: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


def clean_locations(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the locations table."""
    log = _make_log("locations", len(df))
    out = df.copy()

    # ── Strip whitespace ──
    str_cols = out.select_dtypes(include="object").columns.tolist()
    for col in str_cols:
        before = out[col].copy()
        out[col] = strip_whitespace(out[col])
        changed = (before != out[col]).sum()
        if changed:
            log["whitespace_stripped"][col] = int(changed)

    # ── Duplicate PK ──
    dupes = out.duplicated(subset=["location_id"], keep="first").sum()
    if dupes:
        out = out.drop_duplicates(subset=["location_id"], keep="first")
        log["duplicate_pk_removed"] = int(dupes)

    # ── Lat/lon plausibility (India bounding box roughly) ──
    lat_invalid = ((out["latitude"] < 6.0) | (out["latitude"] > 36.0)).sum()
    lon_invalid = ((out["longitude"] < 68.0) | (out["longitude"] > 98.0)).sum()
    if lat_invalid:
        log["numeric_range_violations"]["latitude"] = int(lat_invalid)
    if lon_invalid:
        log["numeric_range_violations"]["longitude"] = int(lon_invalid)

    log["final_rows"] = int(len(out))
    logger.info("clean_locations: %d -> %d rows", log["raw_rows"], log["final_rows"])
    return out, log


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

TABLE_CLEANERS = {
    "claims":    clean_claims,
    "claimants": clean_claimants,
    "policies":  clean_policies,
    "vehicles":  clean_vehicles,
    "providers": clean_providers,
    "invoices":  clean_invoices,
    "locations": clean_locations,
}


def clean_table(name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean a named table and return (cleaned_df, cleaning_log)."""
    if name not in TABLE_CLEANERS:
        raise ValueError(f"No cleaner defined for table '{name}'")
    return TABLE_CLEANERS[name](df)
