"""
scripts/seed.py
---------------
CLI utility to seed the database with initial enterprise entities,
policyholders, policies, repair facilities, and demo claims.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from database.seed import seed_database, DB_DEFAULT


def main():
    parser = argparse.ArgumentParser(description="Seed FraudShield AI database")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT, help="Path to SQLite database")
    args = parser.parse_args()

    print("=" * 60)
    print("  FraudShield AI - Database Seeder")
    print("=" * 60)
    print(f"Target Database: {args.db}")
    seed_database(args.db)
    print("\nDatabase seeding completed successfully.")


if __name__ == "__main__":
    main()
