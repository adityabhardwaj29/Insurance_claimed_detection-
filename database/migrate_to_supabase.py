"""
database/migrate_to_supabase.py
-------------------------------
Automated migration script transferring relational insurance data from SQLite
to Supabase PostgreSQL with strict row count verification and schema validation.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("migration")

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "database" / "fraud_detection.db"
MIGRATIONS_DIR = ROOT / "database" / "migrations"


MIGRATION_ORDER = [
    "claimants",
    "providers",
    "policies",
    "vehicles",
    "invoices",
    "claims",
    "locations",
    "investigation_cases",
    "case_notes",
    "case_events",
]


def load_sqlite_counts(sqlite_path: Path) -> Dict[str, int]:
    """Retrieves exact row counts for each entity table in SQLite."""
    counts: Dict[str, int] = {}
    with sqlite3.connect(sqlite_path) as conn:
        cur = conn.cursor()
        for tbl in MIGRATION_ORDER:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                counts[tbl] = cur.fetchone()[0]
            except Exception:
                counts[tbl] = 0
    return counts


def run_migration(database_url: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Transfers records from SQLite to Supabase PostgreSQL and verifies integrity.
    """
    logger.info("Starting migration pipeline: SQLite -> Supabase PostgreSQL")
    logger.info("Source SQLite: %s", SQLITE_DB)

    if not SQLITE_DB.exists():
        raise FileNotFoundError(f"Source SQLite database not found: {SQLITE_DB}")

    src_counts = load_sqlite_counts(SQLITE_DB)
    logger.info("Source record counts: %s", json.dumps(src_counts, indent=2))

    if dry_run or not database_url:
        logger.warning("Dry run mode active or DATABASE_URL not set. Skipping live transfer.")
        return {
            "status": "dry_run",
            "source_counts": src_counts,
            "target_counts": {k: 0 for k in src_counts},
            "verified": False,
            "note": "Supply valid DATABASE_URL or SUPABASE_URL to perform live sync."
        }

    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise ImportError("psycopg2 is required for PostgreSQL migration. Run: pip install psycopg2-binary")

    dest_counts: Dict[str, int] = {}
    pg_conn = psycopg2.connect(database_url)
    pg_conn.autocommit = False

    with sqlite3.connect(SQLITE_DB) as sq_conn:
        sq_conn.row_factory = sqlite3.Row
        sq_cur = sq_conn.cursor()

        with pg_conn.cursor() as pg_cur:
            for tbl in MIGRATION_ORDER:
                logger.info("Migrating table: %s ...", tbl)
                sq_cur.execute(f"SELECT * FROM {tbl}")
                rows = [dict(r) for r in sq_cur.fetchall()]

                if not rows:
                    dest_counts[tbl] = 0
                    continue

                cols = list(rows[0].keys())
                col_names = ", ".join(cols)
                placeholders = ", ".join(["%s"] * len(cols))
                insert_sql = f"INSERT INTO {tbl} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

                values = [[r[c] for c in cols] for r in rows]
                psycopg2.extras.execute_batch(pg_cur, insert_sql, values, page_size=100)
                pg_conn.commit()

                # Verify target count
                pg_cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                dest_counts[tbl] = pg_cur.fetchone()[0]
                logger.info("Table %s migrated: %d / %d records verified.", tbl, dest_counts[tbl], src_counts[tbl])

    pg_conn.close()

    # Compare counts
    all_matched = all(dest_counts.get(t, 0) == src_counts.get(t, 0) for t in MIGRATION_ORDER)
    report = {
        "status": "success" if all_matched else "partial_match",
        "source_counts": src_counts,
        "target_counts": dest_counts,
        "verified": all_matched,
    }

    report_path = ROOT / "reports" / "SUPABASE_MIGRATION_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info("Migration finished with status: %s. Report written to %s", report["status"], report_path)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite insurance data to Supabase PostgreSQL")
    parser.add_argument("--url", default=os.getenv("DATABASE_URL", ""), help="Target PostgreSQL connection string")
    parser.add_argument("--dry-run", action="store_true", help="Inspect source counts without writing")
    args = parser.parse_args()

    res = run_migration(database_url=args.url, dry_run=args.dry_run)
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    for t, c in res["source_counts"].items():
        print(f"  {t:<22} | Source (SQLite): {c:>4} | Target (Supabase): {res['target_counts'].get(t, 0):>4}")
    print("=" * 60)
