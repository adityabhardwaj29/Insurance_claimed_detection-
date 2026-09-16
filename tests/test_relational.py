"""
tests/test_relational.py
-------------------------
Tests for the Phase 2 relational layer (data/relational/).

Covers:
  - All 7 relational CSVs exist
  - Primary key uniqueness for every table
  - No null primary keys
  - Full FK consistency (all 8 FK relationships)
  - Orphan detection
  - No full-row duplicates
  - ID format patterns match expected regex
  - Categorical values within valid sets
  - Numeric ranges (amounts, age, model_year, rating)
  - Date parseability
  - Fraud label binary integrity
  - Invoice reuse documented (informational)
  - SQLite database creation and view queries
  - Row counts match relational CSVs

Run with:
    pytest tests/test_relational.py -v
"""

from pathlib import Path
import sqlite3
import pandas as pd
import pytest
import re

ROOT         = Path(__file__).resolve().parent.parent
RELATIONAL   = ROOT / "data" / "relational"
DB_PATH      = ROOT / "database" / "fraud_detection.db"
REPORTS      = ROOT / "reports"
DOCS         = ROOT / "docs"
DATABASE_DIR = ROOT / "database"

# ── Valid value sets ─────────────────────────────────────────────────────────
VALID_CLAIM_TYPES     = {"Theft", "Glass Damage", "Fire", "Accident", "Natural Disaster"}
VALID_STATUSES        = {"Open", "Approved", "Under Review", "Rejected"}
VALID_POLICY_TYPES    = {"Comprehensive", "Zero Dep", "Third Party"}
VALID_VEHICLE_TYPES   = {"MUV", "Sedan", "Hatchback", "SUV"}
VALID_MAKES           = {"Tata", "Maruti", "Hyundai", "Mahindra", "Honda"}
VALID_PROVIDER_TYPES  = {"Surveyor", "Dealer", "Garage", "Hospital"}
VALID_GENDERS         = {"M", "F"}
VALID_MARITAL_STATUS  = {"Married", "Single"}
VALID_CITIES          = {"Mumbai", "Pune", "Delhi", "Ahmedabad", "Surat"}

ID_PATTERNS = {
    "claim_id":    r"^CLM\d{5}$",
    "claimant_id": r"^CLT\d{4}$",
    "policy_id":   r"^POL\d{4}$",
    "vehicle_id":  r"^VEH\d{4}$",
    "provider_id": r"^PRV\d{3}$",
    "invoice_id":  r"^INV\d{5}$",
    "location_id": r"^LOC\d{3}$",
}


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def claims():
    return pd.read_csv(RELATIONAL / "claims.csv")

@pytest.fixture(scope="module")
def claimants():
    return pd.read_csv(RELATIONAL / "claimants.csv")

@pytest.fixture(scope="module")
def policies():
    return pd.read_csv(RELATIONAL / "policies.csv")

@pytest.fixture(scope="module")
def vehicles():
    return pd.read_csv(RELATIONAL / "vehicles.csv")

@pytest.fixture(scope="module")
def providers():
    return pd.read_csv(RELATIONAL / "providers.csv")

@pytest.fixture(scope="module")
def invoices():
    return pd.read_csv(RELATIONAL / "invoices.csv")

@pytest.fixture(scope="module")
def locations():
    return pd.read_csv(RELATIONAL / "locations.csv")

@pytest.fixture(scope="module")
def db_conn():
    """Open a read-only connection to the seeded SQLite database."""
    if not DB_PATH.exists():
        pytest.skip("SQLite database not seeded; run `python database/seed.py` first")
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()


# ── File existence ───────────────────────────────────────────────────────────

def test_relational_dir_exists():
    assert RELATIONAL.is_dir(), "data/relational/ not found"

@pytest.mark.parametrize("fname", [
    "claims.csv", "claimants.csv", "policies.csv", "vehicles.csv",
    "providers.csv", "invoices.csv", "locations.csv",
])
def test_relational_file_exists(fname):
    assert (RELATIONAL / fname).exists(), f"Missing: {fname}"

def test_data_dictionary_exists():
    assert (DOCS / "data_dictionary.md").exists()

def test_database_design_exists():
    assert (DOCS / "database_design.md").exists()

def test_schema_sql_exists():
    assert (DATABASE_DIR / "schema.sql").exists()

def test_seed_py_exists():
    assert (DATABASE_DIR / "seed.py").exists()

def test_views_sql_exists():
    assert (DATABASE_DIR / "views.sql").exists()

def test_indexes_sql_exists():
    assert (DATABASE_DIR / "indexes.sql").exists()


# ── Row counts ───────────────────────────────────────────────────────────────

def test_claims_row_count(claims):
    assert len(claims) == 320

def test_claimants_row_count(claimants):
    assert len(claimants) == 120

def test_policies_row_count(policies):
    assert len(policies) == 140

def test_vehicles_row_count(vehicles):
    assert len(vehicles) == 130

def test_providers_row_count(providers):
    assert len(providers) == 25

def test_invoices_row_count(invoices):
    assert len(invoices) == 220

def test_locations_row_count(locations):
    assert len(locations) == 60


# ── Primary key uniqueness ───────────────────────────────────────────────────

def test_claims_pk_unique(claims):
    assert not claims.duplicated("claim_id").any()

def test_claimants_pk_unique(claimants):
    assert not claimants.duplicated("claimant_id").any()

def test_policies_pk_unique(policies):
    assert not policies.duplicated("policy_id").any()

def test_vehicles_pk_unique(vehicles):
    assert not vehicles.duplicated("vehicle_id").any()

def test_providers_pk_unique(providers):
    assert not providers.duplicated("provider_id").any()

def test_invoices_pk_unique(invoices):
    assert not invoices.duplicated("invoice_id").any()

def test_locations_pk_unique(locations):
    assert not locations.duplicated("location_id").any()


# ── Null primary keys ────────────────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name,pk", [
    ("claims",    "claim_id"),
    ("claimants", "claimant_id"),
    ("policies",  "policy_id"),
    ("vehicles",  "vehicle_id"),
    ("providers", "provider_id"),
    ("invoices",  "invoice_id"),
    ("locations", "location_id"),
])
def test_pk_not_null(fixture_name, pk, request):
    df = request.getfixturevalue(fixture_name)
    assert df[pk].notna().all(), f"{fixture_name}.{pk} has null values"


# ── ID pattern format ────────────────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name,col", [
    ("claims",    "claim_id"),
    ("claimants", "claimant_id"),
    ("policies",  "policy_id"),
    ("vehicles",  "vehicle_id"),
    ("providers", "provider_id"),
    ("invoices",  "invoice_id"),
    ("locations", "location_id"),
])
def test_id_format(fixture_name, col, request):
    df = request.getfixturevalue(fixture_name)
    pattern = ID_PATTERNS[col]
    valid = df[col].str.match(pattern, na=False)
    bad = df.loc[~valid, col].tolist()
    assert not bad, f"{fixture_name}.{col}: {len(bad)} IDs don't match {pattern}: {bad[:5]}"


# ── No full-row duplicates ───────────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "claims","claimants","policies","vehicles","providers","invoices","locations"
])
def test_no_full_row_duplicates(fixture_name, request):
    df = request.getfixturevalue(fixture_name)
    n = df.duplicated(keep=False).sum()
    assert n == 0, f"{fixture_name} has {n} fully-duplicate rows"


# ── Foreign key integrity ────────────────────────────────────────────────────

def test_fk_claims_claimant(claims, claimants):
    orphans = ~claims["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in claims"

def test_fk_claims_policy(claims, policies):
    orphans = ~claims["policy_id"].isin(policies["policy_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan policy_id in claims"

def test_fk_claims_vehicle(claims, vehicles):
    orphans = ~claims["vehicle_id"].isin(vehicles["vehicle_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan vehicle_id in claims"

def test_fk_claims_provider(claims, providers):
    orphans = ~claims["provider_id"].isin(providers["provider_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan provider_id in claims"

def test_fk_claims_invoice(claims, invoices):
    orphans = ~claims["invoice_id"].isin(invoices["invoice_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan invoice_id in claims"

def test_fk_policies_claimant(policies, claimants):
    orphans = ~policies["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in policies"

def test_fk_vehicles_claimant(vehicles, claimants):
    orphans = ~vehicles["claimant_id"].isin(claimants["claimant_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan claimant_id in vehicles"

def test_fk_invoices_provider(invoices, providers):
    orphans = ~invoices["provider_id"].isin(providers["provider_id"])
    assert not orphans.any(), f"{orphans.sum()} orphan provider_id in invoices"


# ── Categorical values ───────────────────────────────────────────────────────

def test_claim_type_valid(claims):
    non_null = claims["claim_type"].dropna()
    assert non_null.isin(VALID_CLAIM_TYPES).all()

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

def test_location_cities_valid(locations):
    non_null = locations["city"].dropna()
    assert non_null.isin(VALID_CITIES).all()


# ── Numeric ranges ───────────────────────────────────────────────────────────

def test_claim_amount_positive(claims):
    vals = pd.to_numeric(claims["claim_amount"], errors="coerce").dropna()
    assert (vals > 0).all()

def test_invoice_amount_positive(invoices):
    vals = pd.to_numeric(invoices["invoice_amount"], errors="coerce").dropna()
    assert (vals > 0).all()

def test_premium_positive(policies):
    vals = pd.to_numeric(policies["premium"], errors="coerce").dropna()
    assert (vals > 0).all()

def test_age_range(claimants):
    vals = pd.to_numeric(claimants["age"], errors="coerce").dropna()
    assert (vals >= 18).all() and (vals <= 100).all()

def test_model_year_range(vehicles):
    vals = pd.to_numeric(vehicles["model_year"], errors="coerce").dropna()
    assert (vals >= 1990).all() and (vals <= 2026).all()

def test_provider_rating_range(providers):
    vals = pd.to_numeric(providers["rating"], errors="coerce").dropna()
    assert (vals >= 0).all() and (vals <= 5).all()

def test_latitude_in_india_range(locations):
    vals = pd.to_numeric(locations["latitude"], errors="coerce").dropna()
    assert (vals >= 6).all() and (vals <= 36).all()

def test_longitude_in_india_range(locations):
    vals = pd.to_numeric(locations["longitude"], errors="coerce").dropna()
    assert (vals >= 68).all() and (vals <= 98).all()


# ── Dates ────────────────────────────────────────────────────────────────────

def test_claim_date_parseable(claims):
    parsed = pd.to_datetime(claims["claim_date"], errors="coerce")
    assert parsed.notna().sum() > 300, "Too many unparseable claim_dates"

def test_policy_start_date_parseable(policies):
    parsed = pd.to_datetime(policies["start_date"], errors="coerce")
    assert parsed.notna().sum() > 130

def test_policy_end_date_parseable(policies):
    parsed = pd.to_datetime(policies["end_date"], errors="coerce")
    assert parsed.notna().sum() > 130

def test_invoice_date_parseable(invoices):
    parsed = pd.to_datetime(invoices["invoice_date"], errors="coerce")
    assert parsed.notna().sum() > 210

def test_policy_date_order_flagged_correctly(policies):
    """The 4 known bad policies should have date_order_invalid=True."""
    bad_ids = {"POL0039", "POL0063", "POL0076", "POL0134"}
    flagged = policies[policies["date_order_invalid"].astype(str).str.lower() == "true"]
    flagged_ids = set(flagged["policy_id"].tolist())
    assert bad_ids == flagged_ids, (
        f"Expected flagged policies {bad_ids}, got {flagged_ids}"
    )


# ── Fraud label ──────────────────────────────────────────────────────────────

def test_fraud_label_binary(claims):
    vals = claims["fraud_label"].dropna()
    assert vals.isin([0, 1]).all()

def test_fraud_label_not_all_zero(claims):
    assert claims["fraud_label"].sum() > 0, "No fraud cases found"

def test_fraud_rate_is_known_value(claims):
    """Fraud rate should be exactly 16.25% (52/320) per audit."""
    rate = claims["fraud_label"].mean()
    assert abs(rate - 0.1625) < 0.001, f"Unexpected fraud rate: {rate:.4f}"


# ── Invoice reuse (informational) ────────────────────────────────────────────

def test_invoice_reuse_count(claims):
    """153 claims share an invoice with ≥1 other claim per audit findings."""
    reused = claims[claims.duplicated("invoice_id", keep=False)]
    assert len(reused) >= 100, (
        f"Expected >= 100 claims with reused invoices, got {len(reused)}"
    )

def test_unique_invoices_less_than_claims(claims):
    """Fewer unique invoices than claims confirms reuse."""
    assert claims["invoice_id"].nunique() < len(claims)


# ── Locations orphan (documented) ────────────────────────────────────────────

def test_locations_has_no_fk_col(locations):
    """Locations table should have exactly 4 columns: no FK to other tables."""
    assert list(locations.columns) == ["location_id", "city", "latitude", "longitude"]


# ── Relational validation report ─────────────────────────────────────────────

def test_relational_validation_report_exists():
    assert (REPORTS / "relational_validation_report.json").exists(), (
        "Run `python -m src.data.relational_validation` first"
    )

def test_relational_validation_report_passes():
    import json
    report_path = REPORTS / "relational_validation_report.json"
    if not report_path.exists():
        pytest.skip("Validation report not generated yet")
    with open(report_path) as f:
        report = json.load(f)
    failed = report["summary"]["failed"]
    failed_checks = report.get("failed_checks", [])
    # The only known failure is date_order_invalid for 4 policies
    # All other checks must pass
    non_date_failures = [
        c for c in failed_checks
        if "start_date_before_end_date" not in c["check"]
        and "date_order" not in c["check"]
    ]
    assert not non_date_failures, (
        f"Unexpected validation failures: {[c['check'] for c in non_date_failures]}"
    )


# ── SQLite database ───────────────────────────────────────────────────────────

def test_db_file_exists():
    assert DB_PATH.exists(), (
        "SQLite database not found. Run `python database/seed.py` first."
    )

def test_db_all_tables_present(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    expected = {"claimants","policies","vehicles","providers","invoices","claims","locations"}
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"

def test_db_all_views_present(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = {row[0] for row in cur.fetchall()}
    expected = {"claim_risk_base","provider_summary","claimant_summary",
                "fraud_overview","invoice_reuse"}
    assert expected.issubset(views), f"Missing views: {expected - views}"

def test_db_claim_count(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM claims")
    assert cur.fetchone()[0] == 320

def test_db_claimant_count(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM claimants")
    assert cur.fetchone()[0] == 120

def test_db_fraud_overview_view(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT total_claims, fraud_count, legit_count FROM fraud_overview")
    row = cur.fetchone()
    total, fraud, legit = row
    assert total == 320
    assert fraud == 52
    assert legit == 268

def test_db_fk_no_orphan_claims(db_conn):
    """Verify FK integrity via SQL query."""
    cur = db_conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM claims c
        WHERE NOT EXISTS (
            SELECT 1 FROM claimants cl WHERE cl.claimant_id = c.claimant_id
        )
    """)
    assert cur.fetchone()[0] == 0, "Orphan claims found (missing claimant)"

def test_db_provider_summary_view(db_conn):
    """provider_summary view should return 25 rows (one per provider)."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM provider_summary")
    assert cur.fetchone()[0] == 25

def test_db_claim_risk_base_view(db_conn):
    """claim_risk_base should join to produce 320 rows."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM claim_risk_base")
    assert cur.fetchone()[0] == 320

def test_db_invoice_reuse_view_non_empty(db_conn):
    """At least some invoices should appear in invoice_reuse view."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoice_reuse")
    assert cur.fetchone()[0] > 0
