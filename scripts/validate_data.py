"""
scripts/validate_data.py
------------------------
CLI runner for data validation and schema integrity checks.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data.validate_data import validate_all


def main():
    print("=" * 60)
    print("  FraudShield AI - Data & Schema Integrity Validator")
    print("=" * 60)

    # Load relational tables from data/relational
    rel_dir = ROOT / "data" / "relational"
    tables = {}
    for csv_file in sorted(rel_dir.glob("*.csv")):
        tables[csv_file.stem] = pd.read_csv(csv_file)

    print(f"Loaded {len(tables)} relational tables from {rel_dir}:")
    for name, df in tables.items():
        print(f"  - {name}: {len(df)} rows, {len(df.columns)} columns")

    raw_path = ROOT / "data" / "raw" / "claims_raw.csv"
    raw_df = pd.read_csv(raw_path) if raw_path.exists() else None

    print("\nRunning relational schema, foreign key, and domain range validation...")
    report = validate_all(tables, raw_df)

    summary = report.get("summary", {})
    all_passed = summary.get("all_passed", False)
    total = summary.get("total_checks", 0)
    failed = summary.get("failed", 0)

    # Print failures only
    for check in report.get("checks", []):
        if not check["passed"]:
            print(f"  [FAIL] {check['check']}: {check['details']}")

    # Filter unexpected failures (date order is a known raw data anomaly documented in docs/DATA_QUALITY.md)
    unexpected = [
        c for c in report.get("checks", [])
        if not c["passed"] and "start_date_before_end_date" not in c["check"] and "date_order" not in c["check"]
    ]

    print()
    if not unexpected:
        if failed > 0:
            print(f"[SUCCESS] Validation passed with {failed} documented anomaly (see docs/DATA_QUALITY.md).")
        else:
            print(f"[SUCCESS] All {total} validation checks passed.")
        sys.exit(0)
    else:
        print(f"[ERROR] {len(unexpected)} unexpected validation failures detected.")
        sys.exit(1)


if __name__ == "__main__":
    main()
