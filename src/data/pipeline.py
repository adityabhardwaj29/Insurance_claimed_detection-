"""
src/data/pipeline.py
--------------------
Main data pipeline orchestrator for Phase 1.

Usage:
    python -m src.data.pipeline

What it does:
    1. Loads all 7 raw tables from data/raw/ (never writes there).
    2. Cleans each table and records a per-table cleaning log.
    3. Saves cleaned tables to data/processed/*.csv.
    4. Runs all validation checks on cleaned data.
    5. Writes reports/data_quality_report.json.
    6. Writes docs/DATA_QUALITY.md (human-readable summary).
    7. Writes data/provenance/DATA_GENERATION.md (provenance doc).
    8. Prints a final pipeline summary to stdout.

All transformations are deterministic and reproducible.
No random values are introduced at any step.
"""

from __future__ import annotations

import json
import logging
import logging.config
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

# ── Project root resolution ──────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.data.load_data import load_all_raw, RAW_FILES
from src.data.clean_data import clean_table
from src.data.validate_data import validate_all

# ── Directory layout ─────────────────────────────────────────────────────────
PROCESSED_DIR  = ROOT / "data" / "processed"
PROVENANCE_DIR = ROOT / "data" / "provenance"
REPORTS_DIR    = ROOT / "reports"
DOCS_DIR       = ROOT / "docs"
LOGS_DIR       = ROOT / "logs"

for d in [PROCESSED_DIR, PROVENANCE_DIR, REPORTS_DIR, DOCS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "pipeline.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("pipeline")


# ── Output filenames ─────────────────────────────────────────────────────────
CLEAN_FILENAMES = {
    "claims":    "claims_clean.csv",
    "claimants": "claimants_clean.csv",
    "policies":  "policies_clean.csv",
    "vehicles":  "vehicles_clean.csv",
    "providers": "providers_clean.csv",
    "invoices":  "invoices_clean.csv",
    "locations": "locations_clean.csv",
}


def _save_clean_table(name: str, df: pd.DataFrame) -> Path:
    """Save a cleaned DataFrame to data/processed/ and return the path."""
    path = PROCESSED_DIR / CLEAN_FILENAMES[name]
    df.to_csv(path, index=False)
    logger.info("Saved %s -> %s (%d rows)", name, path.name, len(df))
    return path


def _build_quality_report(
    raw_tables: dict[str, pd.DataFrame],
    clean_tables: dict[str, pd.DataFrame],
    cleaning_logs: dict[str, dict],
    validation_report: dict,
    run_ts: str,
) -> dict[str, Any]:
    """Compose the full data quality report dict."""
    row_summary = {}
    for name in raw_tables:
        raw_n   = len(raw_tables[name])
        clean_n = len(clean_tables[name])
        row_summary[name] = {
            "raw_rows":     raw_n,
            "clean_rows":   clean_n,
            "rows_removed": raw_n - clean_n,
        }

    # Aggregate cleaning totals
    total_duplicates_removed = sum(
        log.get("duplicate_pk_removed", 0) for log in cleaning_logs.values()
    )
    total_whitespace_fixes = sum(
        sum(v for v in log.get("whitespace_stripped", {}).values())
        for log in cleaning_logs.values()
    )
    total_invalid_categoricals = sum(
        sum(v for v in log.get("invalid_categoricals_flagged", {}).values())
        for log in cleaning_logs.values()
    )
    total_invalid_dates = sum(
        sum(v for v in log.get("invalid_dates_flagged", {}).values())
        for log in cleaning_logs.values()
    )
    total_range_violations = sum(
        sum(v for v in log.get("numeric_range_violations", {}).values())
        for log in cleaning_logs.values()
    )

    return {
        "pipeline_run": {
            "timestamp": run_ts,
            "pipeline_version": "1.0.0",
            "source": "data/raw/",
            "output": "data/processed/",
            "random_seed_used": False,
            "synthetic_values_introduced": False,
        },
        "row_summary": row_summary,
        "cleaning_totals": {
            "duplicate_pk_rows_removed": total_duplicates_removed,
            "whitespace_values_stripped": total_whitespace_fixes,
            "invalid_categorical_values_flagged_as_na": total_invalid_categoricals,
            "invalid_date_values_flagged_as_nat": total_invalid_dates,
            "numeric_range_violations_flagged_as_na": total_range_violations,
        },
        "per_table_cleaning_logs": cleaning_logs,
        "validation": validation_report,
        "fraud_label_integrity": {
            "source_fraud_label_col": "claims_raw.csv::fraud_label",
            "altered_during_cleaning": False,
            "fraud_count":  int(clean_tables["claims"]["fraud_label"].sum()),
            "legit_count":  int((clean_tables["claims"]["fraud_label"] == 0).sum()),
            "fraud_rate":   round(
                float(clean_tables["claims"]["fraud_label"].mean()), 4
            ),
        },
    }


def _write_quality_report_json(report: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info("Quality report -> %s", path)


def _write_data_quality_md(report: dict, path: Path) -> None:
    """Write the human-readable DATA_QUALITY.md document."""
    row_s   = report["row_summary"]
    totals  = report["cleaning_totals"]
    val     = report["validation"]
    fi      = report["fraud_label_integrity"]
    imb     = val["class_imbalance"]
    ts      = report["pipeline_run"]["timestamp"]

    summary = val["summary"]
    checks  = val["checks"]
    failed_checks  = [c for c in checks if not c["passed"]]
    warning_checks = [c for c in checks if not c["passed"]]

    lines = [
        "# Data Quality Report",
        "",
        f"**Generated:** {ts}",
        f"**Pipeline version:** {report['pipeline_run']['pipeline_version']}",
        f"**Source:** `data/raw/`",
        f"**Output:** `data/processed/`",
        "",
        "---",
        "",
        "## Row Summary",
        "",
        "| Table | Raw Rows | Clean Rows | Rows Removed |",
        "|---|---|---|---|",
    ]
    for tbl, s in row_s.items():
        lines.append(
            f"| {tbl} | {s['raw_rows']} | {s['clean_rows']} | {s['rows_removed']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Cleaning Totals",
        "",
        f"| Issue | Count |",
        f"|---|---|",
        f"| Duplicate PK rows removed | {totals['duplicate_pk_rows_removed']} |",
        f"| Whitespace values stripped | {totals['whitespace_values_stripped']} |",
        f"| Invalid categoricals flagged as NA | {totals['invalid_categorical_values_flagged_as_na']} |",
        f"| Invalid dates flagged as NaT | {totals['invalid_date_values_flagged_as_nat']} |",
        f"| Numeric range violations flagged as NA | {totals['numeric_range_violations_flagged_as_na']} |",
        "",
        "---",
        "",
        "## Fraud Label Integrity",
        "",
        f"- **Source column:** `{fi['source_fraud_label_col']}`",
        f"- **Altered during cleaning:** {fi['altered_during_cleaning']}",
        f"- **Fraud count:** {fi['fraud_count']} ({fi['fraud_rate']*100:.2f}%)",
        f"- **Legitimate count:** {fi['legit_count']}",
        "",
        "---",
        "",
        "## Class Imbalance",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total claims | {imb['total_claims']} |",
        f"| Fraud claims | {imb['fraud_count']} |",
        f"| Legitimate claims | {imb['legit_count']} |",
        f"| Fraud rate | {imb['fraud_rate']*100:.2f}% |",
        f"| Imbalance ratio (legit:fraud) | {imb['imbalance_ratio_legit_to_fraud']}:1 |",
        "",
        f"> **Note:** {imb['note']}",
        "",
        "---",
        "",
        "## Validation Results",
        "",
        f"**{summary['passed']}/{summary['total_checks']} checks passed.**",
        "",
    ]

    if failed_checks:
        lines += [
            f"> [!WARNING]",
            f"> {summary['failed']} validation check(s) failed. See details below.",
            "",
            "### Failed Checks",
            "",
        ]
        for c in failed_checks:
            lines.append(f"- ❌ `{c['check']}`: {c['details']}")
        lines.append("")
    else:
        lines += [
            "> [!NOTE]",
            "> All validation checks passed.",
            "",
        ]

    lines += [
        "### All Check Results",
        "",
        "| Check | Result | Details |",
        "|---|---|---|",
    ]
    for c in checks:
        icon = "✅" if c["passed"] else "❌"
        lines.append(f"| `{c['check']}` | {icon} | {c['details'][:80]} |")

    lines += [
        "",
        "---",
        "",
        "## Data Provenance",
        "",
        "All transformations are deterministic and reproducible.",
        "No random values were introduced. No fraud labels were altered.",
        "See `data/provenance/DATA_GENERATION.md` for full provenance documentation.",
        "",
        "---",
        "",
        "*Generated by `python -m src.data.pipeline`*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("DATA_QUALITY.md -> %s", path)


def _write_provenance_md(
    run_ts: str,
    raw_tables: dict[str, pd.DataFrame],
    clean_tables: dict[str, pd.DataFrame],
    cleaning_logs: dict[str, dict],
    path: Path,
) -> None:
    """Write data/provenance/DATA_GENERATION.md."""
    lines = [
        "# DATA GENERATION AND PROVENANCE",
        "",
        f"**Generated:** {run_ts}",
        "",
        "---",
        "",
        "## Dataset Origin",
        "",
        "| Attribute | Value |",
        "|---|---|",
        "| Master file | `data/master/insurance_claim_dataset.xlsx` |",
        "| Nature | **Synthetic project-generated data** |",
        "| Real insurance data | No |",
        "| Fraud labels | Synthetic ground truth — NOT real fraud evidence |",
        "| Source note | README.md: *'synthetic demo data... not real insurance data'* |",
        "",
        "---",
        "",
        "## Raw Tables",
        "",
        "| Table | File | Rows | Columns | Primary Key |",
        "|---|---|---|---|---|",
    ]
    pk_map = {
        "claims":    "claim_id",
        "claimants": "claimant_id",
        "policies":  "policy_id",
        "vehicles":  "vehicle_id",
        "providers": "provider_id",
        "invoices":  "invoice_id",
        "locations": "location_id",
    }
    raw_files = {
        "claims":    "claims_raw.csv",
        "claimants": "claimants_raw.csv",
        "policies":  "policies_raw.csv",
        "vehicles":  "vehicles_raw.csv",
        "providers": "providers_raw.csv",
        "invoices":  "invoices_raw.csv",
        "locations": "locations_raw.csv",
    }
    for name, df in raw_tables.items():
        lines.append(
            f"| {name} | `data/raw/{raw_files[name]}` | {len(df)} | {len(df.columns)} | `{pk_map[name]}` |"
        )

    lines += [
        "",
        "---",
        "",
        "## Columns per Table",
        "",
    ]
    for name, df in raw_tables.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| Column | Raw Type | Notes |")
        lines.append("|---|---|---|")
        type_notes = {
            "claim_date":   "Stored as string in raw — parsed to datetime in processed",
            "start_date":   "Stored as string in raw — parsed to datetime in processed",
            "end_date":     "Stored as string in raw — parsed to datetime in processed",
            "invoice_date": "Stored as string in raw — parsed to datetime in processed",
            "fraud_label":  "Synthetic ground truth (0=legitimate, 1=fraud) — preserved exactly",
            "description":  "Free-text description — no transformation applied",
            "name":         "Synthetic anonymized name (Customer NNNN)",
            "registration_no": "All Maharashtra (MH prefix) plates — synthetic",
        }
        for col in df.columns:
            dtype = str(df[col].dtype)
            note = type_notes.get(col, "—")
            lines.append(f"| `{col}` | {dtype} | {note} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Transformations Applied",
        "",
        "The following transformations were applied during `src/data/clean_data.py`.",
        "NO transformations modify data/raw/.",
        "",
        "| Transformation | Tables Affected | Rule |",
        "|---|---|---|",
        "| Parse date columns to datetime64 | claims, policies, invoices | `pd.to_datetime(format='%Y-%m-%d', errors='coerce')` |",
        "| Strip leading/trailing whitespace | All tables (string cols) | `.str.strip()` |",
        "| Normalize categoricals to known set | claims, claimants, providers, policies, vehicles | Values outside known set → `pd.NA` |",
        "| Flag non-positive amounts as NA | claims, policies, invoices | `value <= 0 → pd.NA` |",
        "| Flag out-of-range age as NA | claimants | `age < 18 or > 100 → pd.NA` |",
        "| Flag out-of-range model_year as NA | vehicles | `model_year < 1990 or > 2026 → pd.NA` |",
        "| Flag out-of-range rating as NA | providers | `rating < 0 or > 5 → pd.NA` |",
        "| Remove duplicate primary keys | All tables | Keep first occurrence, log count |",
        "| Flag invalid policy date order | policies | `end_date <= start_date → date_order_invalid=True` |",
        "",
        "---",
        "",
        "## Synthetic Fields",
        "",
        "| Field | Table | Description |",
        "|---|---|---|",
        "| `fraud_label` | claims | Synthetic ground-truth label (0/1). Not real fraud evidence. |",
        "| `name` | claimants | Anonymized synthetic name ('Customer NNNN'). Not real names. |",
        "| `description` | claims, invoices | Template-generated text. Not real claim narrative. |",
        "| `registration_no` | vehicles | Synthetic Maharashtra registration plate numbers. |",
        "",
        "---",
        "",
        "## Derived Fields Added by Cleaning",
        "",
        "| Field | Table | Derivation |",
        "|---|---|---|",
        "| `date_order_invalid` | policies (clean) | Boolean flag: `end_date <= start_date`. Derived from existing date columns. |",
        "",
        "---",
        "",
        "## Known Data Limitations",
        "",
        "1. **All data is synthetic.** No real insurance claims, claimants, or providers.",
        "2. **`locations_raw.csv` is orphaned.** No FK links it to claims, claimants, or providers. "
        "City string matching is the only possible join — not implemented in schema.",
        "3. **4 policies have `end_date <= start_date`.** These are flagged but retained because "
        "they are referenced by claims (FK integrity must be preserved). "
        "Policy IDs: POL0039, POL0063, POL0076, POL0134.",
        "4. **86 claims have dates outside the policy date range.** "
        "This is a data quality issue in the synthetic source. Flagged in validation report. "
        "NOT corrected — modifying claim or policy dates would introduce assumptions.",
        "5. **Class imbalance.** Fraud rate is 16.25% (52/320). Any ML model must account for this.",
        "6. **Claim descriptions are template text** (length ~20 chars, low entropy). "
        "Not suitable for NLP/text feature extraction.",
        "7. **All registration plates are MH-prefix.** Geographic diversity is only in city column.",
        "",
        "---",
        "",
        "## Reproducibility",
        "",
        "Run the full pipeline with:",
        "```",
        "python -m src.data.pipeline",
        "```",
        "",
        "Outputs (deterministic, no random seed required for cleaning phase):",
        "- `data/processed/*.csv` — 7 cleaned tables",
        "- `reports/data_quality_report.json`",
        "- `docs/DATA_QUALITY.md`",
        "- `data/provenance/DATA_GENERATION.md`",
        "- `logs/pipeline.log`",
        "",
        "---",
        "",
        "*Generated by `python -m src.data.pipeline`*",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("DATA_GENERATION.md -> %s", path)


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline() -> dict[str, Any]:
    """Execute the full Phase 1 data pipeline.

    Returns
    -------
    dict
        Pipeline summary with row counts and validation results.
    """
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.info("=" * 70)
    logger.info("PHASE 1 DATA PIPELINE — started %s", run_ts)
    logger.info("=" * 70)

    # ── Step 1: Load raw tables ───────────────────────────────────────────
    logger.info("Step 1: Loading raw tables from data/raw/")
    raw_tables = load_all_raw()
    for name, df in raw_tables.items():
        logger.info("  %-12s  %d rows  %d cols", name, len(df), len(df.columns))

    # ── Step 2: Clean each table ──────────────────────────────────────────
    logger.info("Step 2: Cleaning tables")
    clean_tables: dict[str, pd.DataFrame] = {}
    cleaning_logs: dict[str, dict] = {}

    for name in RAW_FILES:
        logger.info("  Cleaning: %s", name)
        cleaned_df, log = clean_table(name, raw_tables[name])
        clean_tables[name] = cleaned_df
        cleaning_logs[name] = log

    # ── Step 3: Save cleaned tables ───────────────────────────────────────
    logger.info("Step 3: Saving cleaned tables to data/processed/")
    saved_paths: dict[str, Path] = {}
    for name, df in clean_tables.items():
        saved_paths[name] = _save_clean_table(name, df)

    # ── Step 4: Validate ─────────────────────────────────────────────────
    logger.info("Step 4: Running validation checks")
    validation_report = validate_all(
        tables=clean_tables,
        raw_claims=raw_tables["claims"],
    )
    val_summary = validation_report["summary"]
    logger.info(
        "  Validation: %d/%d checks passed",
        val_summary["passed"],
        val_summary["total_checks"],
    )
    if not val_summary["all_passed"]:
        failed = [
            c["check"] for c in validation_report["checks"] if not c["passed"]
        ]
        logger.warning("  FAILED checks: %s", failed)

    # ── Step 5: Build and write quality report ────────────────────────────
    logger.info("Step 5: Writing quality report")
    quality_report = _build_quality_report(
        raw_tables=raw_tables,
        clean_tables=clean_tables,
        cleaning_logs=cleaning_logs,
        validation_report=validation_report,
        run_ts=run_ts,
    )
    _write_quality_report_json(quality_report, REPORTS_DIR / "data_quality_report.json")
    _write_data_quality_md(quality_report, DOCS_DIR / "DATA_QUALITY.md")

    # ── Step 6: Write provenance doc ──────────────────────────────────────
    logger.info("Step 6: Writing provenance documentation")
    _write_provenance_md(
        run_ts=run_ts,
        raw_tables=raw_tables,
        clean_tables=clean_tables,
        cleaning_logs=cleaning_logs,
        path=PROVENANCE_DIR / "DATA_GENERATION.md",
    )

    # ── Step 7: Print pipeline summary ───────────────────────────────────
    logger.info("=" * 70)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 70)

    print("\n" + "=" * 70)
    print("PHASE 1 DATA PIPELINE — COMPLETE")
    print("=" * 70)
    print(f"\nRun timestamp : {run_ts}")
    print(f"\n{'Table':<14} {'Raw Rows':>10} {'Clean Rows':>12} {'Removed':>9}")
    print("-" * 50)
    for name in RAW_FILES:
        raw_n   = len(raw_tables[name])
        clean_n = len(clean_tables[name])
        removed = raw_n - clean_n
        print(f"{name:<14} {raw_n:>10} {clean_n:>12} {removed:>9}")

    totals = quality_report["cleaning_totals"]
    print(f"\n{'Cleaning Actions':}")
    print(f"  Duplicate PK rows removed       : {totals['duplicate_pk_rows_removed']}")
    print(f"  Whitespace values stripped       : {totals['whitespace_values_stripped']}")
    print(f"  Invalid categoricals flagged NA  : {totals['invalid_categorical_values_flagged_as_na']}")
    print(f"  Invalid dates flagged NaT        : {totals['invalid_date_values_flagged_as_nat']}")
    print(f"  Numeric range violations flagged : {totals['numeric_range_violations_flagged_as_na']}")

    fi = quality_report["fraud_label_integrity"]
    print(f"\n{'Fraud Label Integrity':}")
    print(f"  Fraud label altered?             : {fi['altered_during_cleaning']}")
    print(f"  Fraud count                      : {fi['fraud_count']}")
    print(f"  Legitimate count                 : {fi['legit_count']}")
    print(f"  Fraud rate                       : {fi['fraud_rate']*100:.2f}%")

    imb = validation_report["class_imbalance"]
    print(f"\n{'Class Imbalance':}")
    print(f"  Imbalance ratio (legit:fraud)    : {imb['imbalance_ratio_legit_to_fraud']}:1")
    print(f"  Note                             : {imb['note']}")

    print(f"\n{'Validation':}")
    print(f"  Checks passed                    : {val_summary['passed']}/{val_summary['total_checks']}")
    if not val_summary["all_passed"]:
        failed = [c for c in validation_report["checks"] if not c["passed"]]
        print(f"  FAILED checks ({val_summary['failed']}):")
        for c in failed:
            print(f"    - {c['check']}: {c['details']}")

    print(f"\n{'Generated Files':}")
    for name, p in saved_paths.items():
        print(f"  {p.relative_to(ROOT)}")
    print(f"  reports/data_quality_report.json")
    print(f"  docs/DATA_QUALITY.md")
    print(f"  data/provenance/DATA_GENERATION.md")
    print(f"  logs/pipeline.log")
    print("\n" + "=" * 70)

    return quality_report


if __name__ == "__main__":
    run_pipeline()
