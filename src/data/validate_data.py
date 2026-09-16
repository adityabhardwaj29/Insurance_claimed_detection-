"""
src/data/validate_data.py
--------------------------
Post-cleaning validation checks.

Each check returns a ValidationResult namedtuple:
    passed  : bool
    check   : str  (name of check)
    details : str  (human-readable summary)
    failures: list (specific failing values/rows, if any)

The validate_all() function runs every check against a dict of cleaned
DataFrames and returns a structured report dict.

Rules:
- No random values.
- No modifications to DataFrames.
- Purely assertive / reporting logic.
"""

from __future__ import annotations

import logging
from collections import namedtuple
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

ValidationResult = namedtuple("ValidationResult", ["passed", "check", "details", "failures"])

# ─────────────────────────────────────────────────────────────────────────────
# Expected categorical value sets (ground truth from raw data audit)
# ─────────────────────────────────────────────────────────────────────────────
VALID_CLAIM_TYPES     = {"Theft", "Glass Damage", "Fire", "Accident", "Natural Disaster"}
VALID_STATUSES        = {"Open", "Approved", "Under Review", "Rejected"}
VALID_POLICY_TYPES    = {"Comprehensive", "Zero Dep", "Third Party"}
VALID_VEHICLE_TYPES   = {"MUV", "Sedan", "Hatchback", "SUV"}
VALID_MAKES           = {"Tata", "Maruti", "Hyundai", "Mahindra", "Honda"}
VALID_PROVIDER_TYPES  = {"Surveyor", "Dealer", "Garage", "Hospital"}
VALID_GENDERS         = {"M", "F"}
VALID_MARITAL_STATUSES = {"Married", "Single"}
VALID_CITIES          = {"Mumbai", "Pune", "Delhi", "Ahmedabad", "Surat"}
VALID_FRAUD_LABELS    = {0, 1}


# ─────────────────────────────────────────────────────────────────────────────
# Individual check functions
# ─────────────────────────────────────────────────────────────────────────────

def check_no_duplicate_pk(df: pd.DataFrame, pk_col: str, table: str) -> ValidationResult:
    """Fail if any primary key value appears more than once."""
    dupes = df[df.duplicated(subset=[pk_col], keep=False)][pk_col].tolist()
    passed = len(dupes) == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.no_duplicate_{pk_col}",
        details=f"{len(dupes)} duplicate {pk_col} values found" if dupes else "PASS",
        failures=dupes[:20],  # cap at 20 for readability
    )


def check_no_nulls_in_pk(df: pd.DataFrame, pk_col: str, table: str) -> ValidationResult:
    """Fail if any primary key value is null."""
    n_null = df[pk_col].isna().sum()
    passed = n_null == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.no_null_{pk_col}",
        details=f"{n_null} null {pk_col} values" if n_null else "PASS",
        failures=[],
    )


def check_fk_integrity(
    child_df: pd.DataFrame,
    child_col: str,
    parent_df: pd.DataFrame,
    parent_col: str,
    child_table: str,
    parent_table: str,
) -> ValidationResult:
    """Fail if child FK values do not appear in parent PK."""
    orphans = child_df.loc[
        ~child_df[child_col].isin(parent_df[parent_col]), child_col
    ].tolist()
    passed = len(orphans) == 0
    return ValidationResult(
        passed=passed,
        check=f"{child_table}.{child_col}_fk_to_{parent_table}",
        details=f"{len(orphans)} FK orphan(s)" if orphans else "PASS",
        failures=orphans[:20],
    )


def check_no_null_in_column(df: pd.DataFrame, col: str, table: str) -> ValidationResult:
    """Fail if column contains any NA."""
    n_null = df[col].isna().sum()
    passed = n_null == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.{col}_no_null",
        details=f"{n_null} null values in {col}" if n_null else "PASS",
        failures=[],
    )


def check_categorical_values(
    df: pd.DataFrame, col: str, valid: set, table: str
) -> ValidationResult:
    """Fail if any non-null value is outside the valid set."""
    non_null = df[col].dropna()
    invalid_vals = non_null[~non_null.isin(valid)].unique().tolist()
    passed = len(invalid_vals) == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.{col}_valid_categories",
        details=f"Invalid values: {invalid_vals}" if invalid_vals else "PASS",
        failures=invalid_vals,
    )


def check_positive_numeric(df: pd.DataFrame, col: str, table: str) -> ValidationResult:
    """Fail if any non-null value is <= 0."""
    non_null = df[col].dropna()
    bad = non_null[non_null <= 0].tolist()
    passed = len(bad) == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.{col}_positive",
        details=f"{len(bad)} non-positive values in {col}" if bad else "PASS",
        failures=bad[:20],
    )


def check_date_order(
    df: pd.DataFrame, start_col: str, end_col: str, table: str
) -> ValidationResult:
    """Fail if end_date <= start_date in any row."""
    both_valid = df[start_col].notna() & df[end_col].notna()
    bad = df.loc[both_valid & (df[end_col] <= df[start_col])]
    passed = len(bad) == 0
    return ValidationResult(
        passed=passed,
        check=f"{table}.{start_col}_before_{end_col}",
        details=(
            f"{len(bad)} rows where {end_col} <= {start_col}: "
            f"{bad.index.tolist()[:10]}"
        ) if not passed else "PASS",
        failures=bad.index.tolist()[:20],
    )


def check_fraud_label_values(df: pd.DataFrame) -> ValidationResult:
    """Fail if fraud_label contains values other than 0 or 1."""
    non_null = df["fraud_label"].dropna()
    invalid = non_null[~non_null.isin(VALID_FRAUD_LABELS)].tolist()
    passed = len(invalid) == 0
    return ValidationResult(
        passed=passed,
        check="claims.fraud_label_binary",
        details=f"Invalid fraud_label values: {invalid}" if invalid else "PASS",
        failures=invalid,
    )


def check_fraud_label_preserved(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> ValidationResult:
    """Fail if any fraud_label changed during cleaning."""
    merged = raw_df[["claim_id", "fraud_label"]].merge(
        clean_df[["claim_id", "fraud_label"]],
        on="claim_id",
        suffixes=("_raw", "_clean"),
        how="inner",
    )
    changed = merged[merged["fraud_label_raw"] != merged["fraud_label_clean"]]
    passed = len(changed) == 0
    return ValidationResult(
        passed=passed,
        check="claims.fraud_label_unchanged",
        details=(
            f"{len(changed)} fraud_label values changed during cleaning"
        ) if not passed else "PASS — all fraud labels preserved exactly",
        failures=changed["claim_id"].tolist(),
    )


def check_age_range(df: pd.DataFrame, low: int = 18, high: int = 100) -> ValidationResult:
    """Fail if any non-null age is outside [low, high]."""
    non_null = df["age"].dropna()
    bad = non_null[(non_null < low) | (non_null > high)].tolist()
    passed = len(bad) == 0
    return ValidationResult(
        passed=passed,
        check="claimants.age_range",
        details=f"{len(bad)} ages outside [{low},{high}]" if bad else "PASS",
        failures=bad,
    )


def check_model_year_range(df: pd.DataFrame, low: int = 1990, high: int = 2026) -> ValidationResult:
    """Fail if any non-null model_year is outside [low, high]."""
    non_null = df["model_year"].dropna()
    bad = non_null[(non_null < low) | (non_null > high)].tolist()
    passed = len(bad) == 0
    return ValidationResult(
        passed=passed,
        check="vehicles.model_year_range",
        details=f"{len(bad)} model_years outside [{low},{high}]" if bad else "PASS",
        failures=bad,
    )


def check_rating_range(df: pd.DataFrame, low: float = 0.0, high: float = 5.0) -> ValidationResult:
    """Fail if any non-null rating is outside [low, high]."""
    non_null = df["rating"].dropna()
    bad = non_null[(non_null < low) | (non_null > high)].tolist()
    passed = len(bad) == 0
    return ValidationResult(
        passed=passed,
        check="providers.rating_range",
        details=f"{len(bad)} ratings outside [{low},{high}]" if bad else "PASS",
        failures=bad,
    )


def check_class_imbalance(df: pd.DataFrame) -> dict[str, Any]:
    """Compute fraud_label distribution — informational, not pass/fail."""
    counts = df["fraud_label"].value_counts().to_dict()
    total = len(df)
    fraud_count = int(counts.get(1, 0))
    legit_count = int(counts.get(0, 0))
    fraud_rate = round(fraud_count / total, 4) if total else 0.0
    imbalance_ratio = round(legit_count / fraud_count, 2) if fraud_count else None
    return {
        "total_claims": total,
        "fraud_count": fraud_count,
        "legit_count": legit_count,
        "fraud_rate": fraud_rate,
        "imbalance_ratio_legit_to_fraud": imbalance_ratio,
        "note": (
            "Class imbalance detected. "
            f"Ratio {imbalance_ratio}:1 (legit:fraud). "
            "Use class_weight='balanced' or SMOTE during model training."
            if imbalance_ratio and imbalance_ratio > 2 else "Balanced"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Master validation runner
# ─────────────────────────────────────────────────────────────────────────────

def validate_all(
    tables: dict[str, pd.DataFrame],
    raw_claims: pd.DataFrame,
) -> dict[str, Any]:
    """Run all validation checks and return a structured report.

    Parameters
    ----------
    tables : dict
        Mapping of table name -> cleaned DataFrame.
    raw_claims : pd.DataFrame
        Original raw claims for fraud_label preservation check.
    """
    results: list[ValidationResult] = []

    claims    = tables["claims"]
    claimants = tables["claimants"]
    policies  = tables["policies"]
    vehicles  = tables["vehicles"]
    providers = tables["providers"]
    invoices  = tables["invoices"]
    locations = tables["locations"]

    # ── Primary key checks ──
    results += [
        check_no_duplicate_pk(claims,    "claim_id",    "claims"),
        check_no_duplicate_pk(claimants, "claimant_id", "claimants"),
        check_no_duplicate_pk(policies,  "policy_id",   "policies"),
        check_no_duplicate_pk(vehicles,  "vehicle_id",  "vehicles"),
        check_no_duplicate_pk(providers, "provider_id", "providers"),
        check_no_duplicate_pk(invoices,  "invoice_id",  "invoices"),
        check_no_duplicate_pk(locations, "location_id", "locations"),
    ]

    # ── Null PK checks ──
    for table, df, pk in [
        ("claims",    claims,    "claim_id"),
        ("claimants", claimants, "claimant_id"),
        ("policies",  policies,  "policy_id"),
        ("vehicles",  vehicles,  "vehicle_id"),
        ("providers", providers, "provider_id"),
        ("invoices",  invoices,  "invoice_id"),
        ("locations", locations, "location_id"),
    ]:
        results.append(check_no_nulls_in_pk(df, pk, table))

    # ── Foreign key integrity ──
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
    for child_df, child_col, parent_df, parent_col, ct, pt in fk_checks:
        results.append(check_fk_integrity(child_df, child_col, parent_df, parent_col, ct, pt))

    # ── Categorical value checks ──
    results += [
        check_categorical_values(claims,    "claim_type",      VALID_CLAIM_TYPES,      "claims"),
        check_categorical_values(claims,    "status",          VALID_STATUSES,         "claims"),
        check_categorical_values(claimants, "gender",          VALID_GENDERS,          "claimants"),
        check_categorical_values(claimants, "marital_status",  VALID_MARITAL_STATUSES, "claimants"),
        check_categorical_values(claimants, "city",            VALID_CITIES,           "claimants"),
        check_categorical_values(providers, "city",            VALID_CITIES,           "providers"),
        check_categorical_values(providers, "provider_type",   VALID_PROVIDER_TYPES,   "providers"),
        check_categorical_values(policies,  "policy_type",     VALID_POLICY_TYPES,     "policies"),
        check_categorical_values(vehicles,  "vehicle_type",    VALID_VEHICLE_TYPES,    "vehicles"),
        check_categorical_values(vehicles,  "make",            VALID_MAKES,            "vehicles"),
    ]

    # ── Numeric range checks ──
    results += [
        check_positive_numeric(claims,    "claim_amount",   "claims"),
        check_positive_numeric(policies,  "premium",        "policies"),
        check_positive_numeric(invoices,  "invoice_amount", "invoices"),
        check_age_range(claimants),
        check_model_year_range(vehicles),
        check_rating_range(providers),
    ]

    # ── Date checks ──
    results.append(check_date_order(policies, "start_date", "end_date", "policies"))

    # ── Fraud label integrity ──
    results.append(check_fraud_label_values(claims))
    results.append(check_fraud_label_preserved(raw_claims, claims))

    # ── Class imbalance (informational) ──
    imbalance_info = check_class_imbalance(claims)

    # ── Summarize ──
    total_checks = len(results)
    passed_checks = sum(1 for r in results if r.passed)
    failed_checks = total_checks - passed_checks

    report = {
        "summary": {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "all_passed": failed_checks == 0,
        },
        "class_imbalance": imbalance_info,
        "checks": [
            {
                "check": r.check,
                "passed": r.passed,
                "details": r.details,
                "failures": r.failures,
            }
            for r in results
        ],
    }

    if failed_checks > 0:
        logger.warning("Validation: %d/%d checks FAILED", failed_checks, total_checks)
    else:
        logger.info("Validation: all %d checks passed", total_checks)

    return report
