"""
database/seed.py
-----------------
Seeds a SQLite database from data/relational/*.csv using the schema
defined in database/schema.sql.

SQLite is used for development/testing. For PostgreSQL, use the
PostgreSQL-compatible schema.sql with psql directly.

Usage:
    python database/seed.py [--db PATH]

Default database path: database/fraud_detection.db

The script:
  1. Creates/re-creates the database file.
  2. Reads and applies database/schema.sql (SQLite-compatible subset).
  3. Loads all 7 relational CSVs in FK-dependency order.
  4. Runs basic row-count verification.
  5. Prints a summary.

SQLite compatibility note:
  - COMMENT ON is PostgreSQL-only; this script strips those statements.
  - CREATE OR REPLACE VIEW -> CREATE VIEW (SQLite syntax).
  - DECIMAL -> REAL, VARCHAR -> TEXT, BOOLEAN -> INTEGER in SQLite.
"""

from __future__ import annotations

import argparse
import logging
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT       = Path(__file__).resolve().parent.parent
DB_DEFAULT = ROOT / "database" / "fraud_detection.db"
REL_DIR    = ROOT / "data" / "relational"
DB_DIR     = ROOT / "database"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ── SQLite-compatible schema (DDL only) ──────────────────────────────────────
# We redefine the CREATE TABLE statements here rather than parsing schema.sql
# so the schema is explicit and version-controlled separately for each backend.

SQLITE_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS claimants (
    claimant_id    TEXT NOT NULL PRIMARY KEY,
    name           TEXT NOT NULL,
    age            INTEGER,
    city           TEXT,
    gender         TEXT CHECK (gender IN ('M','F')),
    marital_status TEXT CHECK (marital_status IN ('Married','Single'))
);

CREATE TABLE IF NOT EXISTS providers (
    provider_id   TEXT NOT NULL PRIMARY KEY,
    provider_name TEXT NOT NULL,
    city          TEXT,
    provider_type TEXT CHECK (provider_type IN ('Surveyor','Dealer','Garage','Hospital')),
    rating        REAL CHECK (rating >= 0 AND rating <= 5)
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id          TEXT NOT NULL PRIMARY KEY,
    claimant_id        TEXT NOT NULL REFERENCES claimants(claimant_id),
    start_date         TEXT,
    end_date           TEXT,
    policy_type        TEXT CHECK (policy_type IN ('Comprehensive','Zero Dep','Third Party')),
    premium            REAL CHECK (premium > 0),
    date_order_invalid INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id      TEXT NOT NULL PRIMARY KEY,
    claimant_id     TEXT NOT NULL REFERENCES claimants(claimant_id),
    make            TEXT CHECK (make IN ('Tata','Maruti','Hyundai','Mahindra','Honda')),
    vehicle_type    TEXT CHECK (vehicle_type IN ('MUV','Sedan','Hatchback','SUV')),
    registration_no TEXT,
    model_year      INTEGER CHECK (model_year >= 1990 AND model_year <= 2026)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id     TEXT NOT NULL PRIMARY KEY,
    provider_id    TEXT NOT NULL REFERENCES providers(provider_id),
    invoice_amount REAL CHECK (invoice_amount > 0),
    invoice_date   TEXT,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id     TEXT NOT NULL PRIMARY KEY,
    claimant_id  TEXT NOT NULL REFERENCES claimants(claimant_id),
    policy_id    TEXT NOT NULL REFERENCES policies(policy_id),
    vehicle_id   TEXT NOT NULL REFERENCES vehicles(vehicle_id),
    provider_id  TEXT NOT NULL REFERENCES providers(provider_id),
    invoice_id   TEXT NOT NULL REFERENCES invoices(invoice_id),
    claim_date   TEXT,
    claim_amount REAL CHECK (claim_amount > 0),
    claim_type   TEXT CHECK (claim_type IN ('Theft','Glass Damage','Fire','Accident','Natural Disaster')),
    status       TEXT CHECK (status IN ('Open','Approved','Under Review','Rejected')),
    fraud_label  INTEGER CHECK (fraud_label IN (0,1)),
    description  TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT NOT NULL PRIMARY KEY,
    city        TEXT,
    latitude    REAL,
    longitude   REAL
);

-- Phase 9: Fraud Investigation Case Management
CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id     TEXT NOT NULL PRIMARY KEY,
    claim_id    TEXT NOT NULL REFERENCES claims(claim_id),
    risk_score  REAL CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_band   TEXT CHECK (risk_band IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    priority    TEXT CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status      TEXT NOT NULL CHECK (status IN ('NEW','UNDER_REVIEW','ESCALATED','RESOLVED','FALSE_POSITIVE')),
    assigned_to TEXT,
    reason      TEXT,
    notes       TEXT,
    resolution  TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_notes (
    note_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     TEXT NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    author      TEXT NOT NULL,
    note_text   TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_events (
    event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     TEXT NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    event_type  TEXT NOT NULL,
    actor       TEXT NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    details     TEXT,
    timestamp   TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_claims_claimant_id  ON claims(claimant_id);
CREATE INDEX IF NOT EXISTS idx_claims_policy_id    ON claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_claims_vehicle_id   ON claims(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_claims_provider_id  ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_invoice_id   ON claims(invoice_id);
CREATE INDEX IF NOT EXISTS idx_claims_fraud_label  ON claims(fraud_label);
CREATE INDEX IF NOT EXISTS idx_claims_status       ON claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_claim_date   ON claims(claim_date);
CREATE INDEX IF NOT EXISTS idx_policies_claimant   ON policies(claimant_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_claimant   ON vehicles(claimant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_provider   ON invoices(provider_id);
CREATE INDEX IF NOT EXISTS idx_cases_claim_id      ON investigation_cases(claim_id);
CREATE INDEX IF NOT EXISTS idx_cases_status        ON investigation_cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_priority      ON investigation_cases(priority);
CREATE INDEX IF NOT EXISTS idx_cases_assigned_to   ON investigation_cases(assigned_to);
CREATE INDEX IF NOT EXISTS idx_case_notes_case     ON case_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_case_events_case    ON case_events(case_id);

-- Views (SQLite syntax)
CREATE VIEW IF NOT EXISTS provider_summary AS
SELECT
    p.provider_id,
    p.provider_name,
    p.provider_type,
    p.city,
    p.rating,
    COUNT(c.claim_id)                                         AS total_claims,
    COUNT(DISTINCT c.claimant_id)                             AS unique_claimants,
    SUM(c.claim_amount)                                       AS total_claim_amount,
    AVG(c.claim_amount)                                       AS avg_claim_amount,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END)       AS fraud_claims,
    CASE WHEN COUNT(c.claim_id) > 0
         THEN ROUND(100.0 * SUM(CASE WHEN c.fraud_label=1 THEN 1 ELSE 0 END)
                    / COUNT(c.claim_id), 2)
         ELSE 0 END                                           AS fraud_rate_pct
FROM providers p
LEFT JOIN claims c ON p.provider_id = c.provider_id
GROUP BY p.provider_id, p.provider_name, p.provider_type, p.city, p.rating;

CREATE VIEW IF NOT EXISTS claimant_summary AS
SELECT
    cl.claimant_id,
    cl.name,
    cl.age,
    cl.city,
    cl.gender,
    cl.marital_status,
    COUNT(c.claim_id)                                         AS total_claims,
    SUM(c.claim_amount)                                       AS total_claim_amount,
    AVG(c.claim_amount)                                       AS avg_claim_amount,
    MAX(c.claim_date)                                         AS latest_claim_date,
    MIN(c.claim_date)                                         AS earliest_claim_date,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END)       AS fraud_claims,
    COUNT(DISTINCT c.policy_id)                               AS policies_used,
    COUNT(DISTINCT c.provider_id)                             AS providers_used
FROM claimants cl
LEFT JOIN claims c ON cl.claimant_id = c.claimant_id
GROUP BY cl.claimant_id, cl.name, cl.age, cl.city, cl.gender, cl.marital_status;

CREATE VIEW IF NOT EXISTS fraud_overview AS
SELECT
    COUNT(*)                                                          AS total_claims,
    SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END)                AS fraud_count,
    SUM(CASE WHEN fraud_label = 0 THEN 1 ELSE 0 END)                AS legit_count,
    ROUND(100.0 * SUM(CASE WHEN fraud_label=1 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                              AS fraud_rate_pct,
    SUM(CASE WHEN fraud_label = 1 THEN claim_amount ELSE 0 END)     AS fraud_amount_total,
    AVG(CASE WHEN fraud_label = 1 THEN claim_amount END)             AS avg_fraud_amount,
    AVG(CASE WHEN fraud_label = 0 THEN claim_amount END)             AS avg_legit_amount
FROM claims;

CREATE VIEW IF NOT EXISTS invoice_reuse AS
SELECT
    i.invoice_id,
    i.provider_id,
    i.invoice_amount,
    i.invoice_date,
    COUNT(c.claim_id)                                         AS claim_count,
    SUM(CASE WHEN c.fraud_label = 1 THEN 1 ELSE 0 END)       AS fraud_claim_count
FROM invoices i
JOIN claims c ON i.invoice_id = c.invoice_id
GROUP BY i.invoice_id, i.provider_id, i.invoice_amount, i.invoice_date
HAVING COUNT(c.claim_id) > 1
ORDER BY claim_count DESC;

CREATE VIEW IF NOT EXISTS claim_risk_base AS
SELECT
    c.claim_id, c.claimant_id, c.policy_id, c.vehicle_id,
    c.provider_id, c.invoice_id, c.claim_date, c.claim_amount,
    c.claim_type, c.status, c.fraud_label,
    p.policy_type, p.premium,
    p.start_date AS policy_start, p.end_date AS policy_end,
    p.date_order_invalid,
    pr.provider_type, pr.rating AS provider_rating,
    i.invoice_amount, i.invoice_date,
    cl.age AS claimant_age, cl.city AS claimant_city,
    cl.gender, cl.marital_status
FROM claims c
JOIN policies  p  ON c.policy_id  = p.policy_id
JOIN providers pr ON c.provider_id = pr.provider_id
JOIN invoices  i  ON c.invoice_id  = i.invoice_id
JOIN claimants cl ON c.claimant_id = cl.claimant_id;
"""


# ── Load order (parents before children) ─────────────────────────────────────
LOAD_ORDER = [
    ("claimants", "claimants.csv"),
    ("providers", "providers.csv"),
    ("policies",  "policies.csv"),
    ("vehicles",  "vehicles.csv"),
    ("invoices",  "invoices.csv"),
    ("claims",    "claims.csv"),
    ("locations", "locations.csv"),
]


def _coerce_for_sqlite(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame columns to SQLite-compatible types."""
    df = df.copy()
    # Booleans -> integers
    for col in df.select_dtypes(include="bool").columns:
        df[col] = df[col].astype(int)
    # Convert string 'True'/'False' to int for date_order_invalid
    if "date_order_invalid" in df.columns:
        df["date_order_invalid"] = (
            df["date_order_invalid"].astype(str).str.lower().map(
                {"true": 1, "false": 0, "1": 1, "0": 0}
            ).fillna(0).astype(int)
        )
    return df


def seed_database(db_path: Path) -> dict:
    """Create and seed the SQLite database. Returns load summary."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.info("Seeding database: %s", db_path)

    # Remove existing DB so schema is clean
    if db_path.exists():
        db_path.unlink()
        logger.info("Removed existing database for clean seed")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Apply DDL
    logger.info("Applying schema DDL")
    conn.executescript(SQLITE_DDL)
    conn.commit()

    # Load tables
    row_counts: dict[str, int] = {}
    for table_name, csv_name in LOAD_ORDER:
        csv_path = REL_DIR / csv_name
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Relational CSV not found: {csv_path}. "
                "Run `python -m src.data.relational_builder` first."
            )
        df = pd.read_csv(csv_path)
        df = _coerce_for_sqlite(table_name, df)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        row_counts[table_name] = len(df)
        logger.info("  Loaded %-14s  %d rows", table_name, len(df))

    conn.commit()

    # Load investigation cases from final_risk_scores if available
    risk_scores_path = ROOT / "data" / "features" / "final_risk_scores.csv"
    if risk_scores_path.exists():
        risk_df = pd.read_csv(risk_scores_path, keep_default_na=False)
        high_risk = risk_df[risk_df["risk_band"].isin(["HIGH", "CRITICAL"])].copy()
        case_rows = []
        event_rows = []
        cur_init = conn.cursor()
        for _, r in high_risk.iterrows():
            cid = str(r["claim_id"])
            case_id = f"CASE-{cid}"
            r_score = float(r["final_risk_score"])
            r_band = str(r["risk_band"])
            priority = r_band
            reason = str(r.get("risk_reasons", ""))
            case_rows.append((
                case_id, cid, r_score, r_band, priority, "NEW", None, reason, None, None, ts, ts
            ))
            event_rows.append((
                case_id, "CASE_CREATED", "SYSTEM", None, "NEW",
                f"Auto-created from risk scoring ({r_band} band, score {r_score:.4f})", ts
            ))
        cur_init.executemany("""
            INSERT OR IGNORE INTO investigation_cases
            (case_id, claim_id, risk_score, risk_band, priority, status, assigned_to, reason, notes, resolution, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, case_rows)
        cur_init.executemany("""
            INSERT INTO case_events
            (case_id, event_type, actor, old_value, new_value, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, event_rows)
        conn.commit()
        row_counts["investigation_cases"] = len(case_rows)
        row_counts["case_events"] = len(event_rows)
        row_counts["case_notes"] = 0
        logger.info("  Loaded investigation_cases %d rows", len(case_rows))

    # Verify row counts
    logger.info("Verifying row counts")
    errors = []
    cur = conn.cursor()
    for table_name, _ in LOAD_ORDER:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        db_count = cur.fetchone()[0]
        expected = row_counts[table_name]
        if db_count != expected:
            errors.append(
                f"{table_name}: expected {expected}, got {db_count}"
            )
        else:
            logger.info("  %-14s OK (%d rows)", table_name, db_count)

    # Quick FK sanity via count query
    cur.execute("""
        SELECT COUNT(*) FROM claims c
        WHERE NOT EXISTS (SELECT 1 FROM claimants cl WHERE cl.claimant_id = c.claimant_id)
    """)
    fk_violations = cur.fetchone()[0]
    if fk_violations:
        errors.append(f"FK violation: {fk_violations} claims with missing claimant_id")

    # Query fraud_overview view
    cur.execute("SELECT * FROM fraud_overview")
    row = cur.fetchone()
    col_names = [d[0] for d in cur.description]
    fraud_stats = dict(zip(col_names, row))

    conn.close()

    summary = {
        "generated":   ts,
        "database":    str(db_path.relative_to(ROOT)),
        "row_counts":  row_counts,
        "errors":      errors,
        "fraud_stats": fraud_stats,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed fraud detection SQLite database")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT,
                        help=f"Database path (default: {DB_DEFAULT})")
    args = parser.parse_args()

    summary = seed_database(args.db)

    print("\n" + "=" * 65)
    print("DATABASE SEED - COMPLETE")
    print("=" * 65)
    print(f"Database: {summary['database']}")
    print(f"\n{'Table':<14} {'Rows':>6}")
    print("-" * 25)
    for name, count in summary["row_counts"].items():
        print(f"{name:<14} {count:>6}")

    fs = summary["fraud_stats"]
    print(f"\nFraud Overview (from fraud_overview view):")
    print(f"  Total claims  : {fs.get('total_claims')}")
    print(f"  Fraud count   : {fs.get('fraud_count')}")
    print(f"  Legit count   : {fs.get('legit_count')}")
    print(f"  Fraud rate    : {fs.get('fraud_rate_pct')}%")

    if summary["errors"]:
        print(f"\nERRORS ({len(summary['errors'])}):")
        for e in summary["errors"]:
            print(f"  FAIL: {e}")
    else:
        print("\nAll verifications passed [OK]")
    print("=" * 65)


if __name__ == "__main__":
    main()
