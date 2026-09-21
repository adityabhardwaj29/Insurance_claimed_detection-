"""
scripts/migrate.py
------------------
CLI utility to apply database schema and migrations.
Supports both Supabase PostgreSQL and local SQLite.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
from database.migrate_to_supabase import run_migration
from api.db import db


def run_migrations(target: str = "auto") -> None:
    print("=" * 60)
    print("  FraudShield AI - Database Migration Runner")
    print("=" * 60)
    print(f"Target Database Engine: {db.engine_type}")

    if db.is_postgres or target == "supabase":
        print("\nApplying migrations and sync to Supabase PostgreSQL...")
        db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL") or ""
        summary = run_migration(database_url=db_url)
        print(f"\nMigration completed with status: {summary.get('status', 'unknown')}")
    else:
        print("\nTarget is local SQLite. Applying migration SQL files from database/migrations/...")
        migrations_dir = ROOT / "database" / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        with db.connection_scope() as conn:
            cur = conn.cursor()
            for mf in migration_files:
                print(f"  -> Applying {mf.name} ...", end=" ")
                try:
                    sql_content = mf.read_text(encoding="utf-8")
                    cur.executescript(sql_content)
                    print("[OK]")
                except Exception as e:
                    print(f"[NOTE] Skipped or partially applied: {e}")
        print("\nSQLite schema migrations completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FraudShield AI database migrations")
    parser.add_argument("--target", choices=["auto", "supabase", "sqlite"], default="auto", help="Migration target")
    args = parser.parse_args()
    run_migrations(args.target)
