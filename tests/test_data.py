"""
tests/test_data.py
------------------
Validation tests for the data pipeline.

These tests verify:
- No unexpected duplicate primary keys in cleaned data
- No invalid data types
- No impossible negative amounts
- Valid date ranges
- Valid categorical values
- No broken FK relationships
- Fraud label preservation

Run with:
    pytest tests/test_data.py -v
"""

from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def claims():
    return pd.read_csv(PROCESSED / "claims_clean.csv", parse_dates=["claim_date"])

@pytest.fixture(scope="module")
def claimants():
    return pd.read_csv(PROCESSED / "claimants_clean.csv")

@pytest.fixture(scope="module")
def policies():
    return pd.read_csv(
        PROCESSED / "policies_clean.csv",
        parse_dates=["start_date", "end_date"]
    )

@pytest.fixture(scope="module")
def vehicles():
    return pd.read_csv(PROCESSED / "vehicles_clean.csv")

@pytest.fixture(scope="module")
def providers():
    return pd.read_csv(PROCESSED / "providers_clean.csv")

@pytest.fixture(scope="module")
def invoices():
    return pd.read_csv(PROCESSED / "invoices_clean.csv", parse_dates=["invoice_date"])

@pytest.fixture(scope="module")
def locations():
    return pd.read_csv(PROCESSED / "locations_clean.csv")

@pytest.fixture(scope="module")
def raw_claims():
    return pd.read_csv(RAW / "claims_raw.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Primary key uniqueness
# ─────────────────────────────────────────────────────────────────────────────

def test_claims_no_duplicate_claim_id(claims):
    assert not claims.duplicated(subset=["claim_id"]).any(), \
        "Duplicate claim_id found in claims_clean"

def test_claimants_no_duplicate_id(claimants):
    assert not claimants.duplicated(subset=["claimant_id"]).any(), \
        "Duplicate claimant_id in claimants_clean"

def test_policies_no_duplicate_id(policies):
    assert not policies.duplicated(subset=["policy_id"]).any(), \
        "Duplicate policy_id in policies_clean"

def test_vehicles_no_duplicate_id(vehicles):
    assert not vehicles.duplicated(subset=["vehicle_id"]).any(), \
        "Duplicate vehicle_id in vehicles_clean"

def test_providers_no_duplicate_id(providers):
    assert not providers.duplicated(subset=["provider_id"]).any(), \
        "Duplicate provider_id in providers_clean"

def test_invoices_no_duplicate_id(invoices):
    assert not invoices.duplicated(subset=["invoice_id"]).any(), \
        "Duplicate invoice_id in invoices_clean"

def test_locations_no_duplicate_id(locations):
    assert not locations.duplicated(subset=["location_id"]).any(), \
        "Duplicate location_id in locations_clean"


# ─────────────────────────────────────────────────────────────────────────────
# Null PK checks
# ─────────────────────────────────────────────────────────────────────────────

def test_claims_claim_id_not_null(claims):
    assert claims["claim_id"].notna().all()

def test_claimants_id_not_null(claimants):
    assert claimants["claimant_id"].notna().all()

def test_policies_id_not_null(policies):
    assert policies["policy_id"].notna().all()

def test_invoices_id_not_null(invoices):
    assert invoices["invoice_id"].notna().all()


# ─────────────────────────────────────────────────────────────────────────────
# Referential integrity (FK)
# ─────────────────────────────────────────────────────────────────────────────

def test_claims_claimant_fk(claims, claimants):
    orphans = ~claims["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in claims"

def test_claims_policy_fk(claims, policies):
    orphans = ~claims["policy_id"].isin(policies["policy_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan policy_id in claims"

def test_claims_vehicle_fk(claims, vehicles):
    orphans = ~claims["vehicle_id"].isin(vehicles["vehicle_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan vehicle_id in claims"

def test_claims_provider_fk(claims, providers):
    orphans = ~claims["provider_id"].isin(providers["provider_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan provider_id in claims"

def test_claims_invoice_fk(claims, invoices):
    orphans = ~claims["invoice_id"].isin(invoices["invoice_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan invoice_id in claims"

def test_policies_claimant_fk(policies, claimants):
    orphans = ~policies["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in policies"

def test_vehicles_claimant_fk(vehicles, claimants):
    orphans = ~vehicles["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in vehicles"

def test_invoices_provider_fk(invoices, providers):
    orphans = ~invoices["provider_id"].isin(providers["provider_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan provider_id in invoices"


# ─────────────────────────────────────────────────────────────────────────────
# Categorical value validity
# ─────────────────────────────────────────────────────────────────────────────

VALID_CLAIM_TYPES     = {"Theft", "Glass Damage", "Fire", "Accident", "Natural Disaster"}
VALID_STATUSES        = {"Open", "Approved", "Under Review", "Rejected"}
VALID_POLICY_TYPES    = {"Comprehensive", "Zero Dep", "Third Party"}
VALID_VEHICLE_TYPES   = {"MUV", "Sedan", "Hatchback", "SUV"}
VALID_MAKES           = {"Tata", "Maruti", "Hyundai", "Mahindra", "Honda"}
VALID_PROVIDER_TYPES  = {"Surveyor", "Dealer", "Garage", "Hospital"}
VALID_GENDERS         = {"M", "F"}
VALID_MARITAL_STATUS  = {"Married", "Single"}
VALID_CITIES          = {"Mumbai", "Pune", "Delhi", "Ahmedabad", "Surat"}


def test_claim_type_valid(claims):
    non_null = claims["claim_type"].dropna()
    assert non_null.isin(VALID_CLAIM_TYPES).all(), \
        f"Invalid claim_type: {non_null[~non_null.isin(VALID_CLAIM_TYPES)].unique()}"

def test_claim_status_valid(claims):
    non_null = claims["status"].dropna()
    assert non_null.isin(VALID_STATUSES).all()

def test_gender_valid(claimants):
    non_null = claimants["gender"].dropna()
    assert non_null.isin(VALID_GENDERS).all()

def test_marital_status_valid(claimants):
    non_null = claimants["marital_status"].dropna()
    assert non_null.isin(VALID_MARITAL_STATUS).all()

def test_claimant_city_valid(claimants):
    non_null = claimants["city"].dropna()
    assert non_null.isin(VALID_CITIES).all()

def test_provider_type_valid(providers):
    non_null = providers["provider_type"].dropna()
    assert non_null.isin(VALID_PROVIDER_TYPES).all()

def test_provider_city_valid(providers):
    non_null = providers["city"].dropna()
    assert non_null.isin(VALID_CITIES).all()

def test_policy_type_valid(policies):
    non_null = policies["policy_type"].dropna()
    assert non_null.isin(VALID_POLICY_TYPES).all()

def test_vehicle_type_valid(vehicles):
    non_null = vehicles["vehicle_type"].dropna()
    assert non_null.isin(VALID_VEHICLE_TYPES).all()

def test_vehicle_make_valid(vehicles):
    non_null = vehicles["make"].dropna()
    assert non_null.isin(VALID_MAKES).all()


# ─────────────────────────────────────────────────────────────────────────────
# Numeric range checks
# ─────────────────────────────────────────────────────────────────────────────

def test_claim_amount_positive(claims):
    non_null = claims["claim_amount"].dropna()
    assert (non_null > 0).all(), "Non-positive claim_amount found"

def test_invoice_amount_positive(invoices):
    non_null = invoices["invoice_amount"].dropna()
    assert (non_null > 0).all(), "Non-positive invoice_amount found"

def test_premium_positive(policies):
    non_null = policies["premium"].dropna()
    assert (non_null > 0).all(), "Non-positive premium found"

def test_age_range(claimants):
    non_null = claimants["age"].dropna()
    assert (non_null >= 18).all() and (non_null <= 100).all(), \
        "Age outside [18, 100]"

def test_model_year_range(vehicles):
    non_null = vehicles["model_year"].dropna()
    assert (non_null >= 1990).all() and (non_null <= 2026).all(), \
        "model_year outside [1990, 2026]"

def test_provider_rating_range(providers):
    non_null = providers["rating"].dropna()
    assert (non_null >= 0).all() and (non_null <= 5).all(), \
        "Provider rating outside [0, 5]"


# ─────────────────────────────────────────────────────────────────────────────
# Date validity
# ─────────────────────────────────────────────────────────────────────────────

def test_claim_date_parseable(claims):
    assert claims["claim_date"].dtype == "datetime64[ns]" or \
           str(claims["claim_date"].dtype).startswith("datetime"), \
        "claim_date not parsed to datetime"

def test_claim_date_not_all_null(claims):
    assert claims["claim_date"].notna().sum() > 0

def test_invoice_date_parseable(invoices):
    assert str(invoices["invoice_date"].dtype).startswith("datetime"), \
        "invoice_date not parsed to datetime"

def test_policy_start_before_end_for_most(policies):
    """At least 95% of policies should have valid date order."""
    valid = policies[policies["start_date"].notna() & policies["end_date"].notna()]
    ok = (valid["end_date"] > valid["start_date"]).sum()
    pct_ok = ok / len(valid)
    assert pct_ok >= 0.95, f"Only {pct_ok:.1%} policies have start_date < end_date"


# ─────────────────────────────────────────────────────────────────────────────
# Fraud label integrity
# ─────────────────────────────────────────────────────────────────────────────

def test_fraud_label_binary(claims):
    non_null = claims["fraud_label"].dropna()
    assert non_null.isin([0, 1]).all(), \
        f"fraud_label contains non-binary values: {non_null[~non_null.isin([0,1])].unique()}"

def test_fraud_label_unchanged_from_raw(claims, raw_claims):
    """Verify fraud_label was not altered during cleaning."""
    merged = raw_claims[["claim_id", "fraud_label"]].merge(
        claims[["claim_id", "fraud_label"]],
        on="claim_id",
        suffixes=("_raw", "_clean"),
        how="inner",
    )
    changed = (merged["fraud_label_raw"] != merged["fraud_label_clean"]).sum()
    assert changed == 0, f"{changed} fraud_label values changed during cleaning"

def test_fraud_rate_plausible(claims):
    """Fraud rate should be between 5% and 50%."""
    rate = claims["fraud_label"].mean()
    assert 0.05 <= rate <= 0.50, f"Implausible fraud rate: {rate:.2%}"

def test_class_imbalance_present(claims):
    """Confirm class imbalance exists and is documented (fraud < 50%)."""
    fraud_count = claims["fraud_label"].sum()
    legit_count = (claims["fraud_label"] == 0).sum()
    assert legit_count > fraud_count, \
        "Expected more legitimate than fraud claims"


# ─────────────────────────────────────────────────────────────────────────────
# Row count sanity (raw files must not be modified)
# ─────────────────────────────────────────────────────────────────────────────

def test_raw_claims_unchanged():
    """Raw file must not be modified by pipeline."""
    raw = pd.read_csv(RAW / "claims_raw.csv")
    assert len(raw) == 320, f"Raw claims row count changed: {len(raw)}"
    assert list(raw.columns) == [
        "claim_id", "claimant_id", "policy_id", "vehicle_id",
        "provider_id", "invoice_id", "claim_date", "claim_amount",
        "claim_type", "status", "fraud_label", "description"
    ], "Raw claims columns changed"

def test_processed_dir_exists():
    assert PROCESSED.is_dir(), "data/processed/ directory not found"

def test_all_processed_files_exist():
    expected = [
        "claims_clean.csv", "claimants_clean.csv", "policies_clean.csv",
        "vehicles_clean.csv", "providers_clean.csv", "invoices_clean.csv",
        "locations_clean.csv",
    ]
    for fname in expected:
        assert (PROCESSED / fname).exists(), f"Missing: {fname}"

def test_quality_report_exists():
    assert (ROOT / "reports" / "data_quality_report.json").exists()

def test_data_quality_md_exists():
    assert (ROOT / "docs" / "DATA_QUALITY.md").exists()

def test_provenance_md_exists():
    assert (ROOT / "data" / "provenance" / "DATA_GENERATION.md").exists()
