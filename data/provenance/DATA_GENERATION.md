# DATA GENERATION AND PROVENANCE

**Generated:** 2026-09-16T12:19:14Z

---

## Dataset Origin

| Attribute | Value |
|---|---|
| Master file | `data/master/insurance_claim_dataset.xlsx` |
| Nature | **Synthetic project-generated data** |
| Real insurance data | No |
| Fraud labels | Synthetic ground truth — NOT real fraud evidence |
| Source note | README.md: *'synthetic demo data... not real insurance data'* |

---

## Raw Tables

| Table | File | Rows | Columns | Primary Key |
|---|---|---|---|---|
| claims | `data/raw/claims_raw.csv` | 320 | 12 | `claim_id` |
| claimants | `data/raw/claimants_raw.csv` | 120 | 6 | `claimant_id` |
| policies | `data/raw/policies_raw.csv` | 140 | 6 | `policy_id` |
| vehicles | `data/raw/vehicles_raw.csv` | 130 | 6 | `vehicle_id` |
| providers | `data/raw/providers_raw.csv` | 25 | 5 | `provider_id` |
| invoices | `data/raw/invoices_raw.csv` | 220 | 5 | `invoice_id` |
| locations | `data/raw/locations_raw.csv` | 60 | 4 | `location_id` |

---

## Columns per Table

### claims

| Column | Raw Type | Notes |
|---|---|---|
| `claim_id` | object | — |
| `claimant_id` | object | — |
| `policy_id` | object | — |
| `vehicle_id` | object | — |
| `provider_id` | object | — |
| `invoice_id` | object | — |
| `claim_date` | object | Stored as string in raw — parsed to datetime in processed |
| `claim_amount` | int64 | — |
| `claim_type` | object | — |
| `status` | object | — |
| `fraud_label` | Int64 | Synthetic ground truth (0=legitimate, 1=fraud) — preserved exactly |
| `description` | object | Free-text description — no transformation applied |

### claimants

| Column | Raw Type | Notes |
|---|---|---|
| `claimant_id` | object | — |
| `name` | object | Synthetic anonymized name (Customer NNNN) |
| `age` | Int64 | — |
| `city` | object | — |
| `gender` | object | — |
| `marital_status` | object | — |

### policies

| Column | Raw Type | Notes |
|---|---|---|
| `policy_id` | object | — |
| `claimant_id` | object | — |
| `start_date` | object | Stored as string in raw — parsed to datetime in processed |
| `end_date` | object | Stored as string in raw — parsed to datetime in processed |
| `policy_type` | object | — |
| `premium` | int64 | — |

### vehicles

| Column | Raw Type | Notes |
|---|---|---|
| `vehicle_id` | object | — |
| `claimant_id` | object | — |
| `make` | object | — |
| `vehicle_type` | object | — |
| `registration_no` | object | All Maharashtra (MH prefix) plates — synthetic |
| `model_year` | Int64 | — |

### providers

| Column | Raw Type | Notes |
|---|---|---|
| `provider_id` | object | — |
| `provider_name` | object | — |
| `city` | object | — |
| `provider_type` | object | — |
| `rating` | float64 | — |

### invoices

| Column | Raw Type | Notes |
|---|---|---|
| `invoice_id` | object | — |
| `provider_id` | object | — |
| `invoice_amount` | int64 | — |
| `invoice_date` | object | Stored as string in raw — parsed to datetime in processed |
| `description` | object | Free-text description — no transformation applied |

### locations

| Column | Raw Type | Notes |
|---|---|---|
| `location_id` | object | — |
| `city` | object | — |
| `latitude` | float64 | — |
| `longitude` | float64 | — |

---

## Transformations Applied

The following transformations were applied during `src/data/clean_data.py`.
NO transformations modify data/raw/.

| Transformation | Tables Affected | Rule |
|---|---|---|
| Parse date columns to datetime64 | claims, policies, invoices | `pd.to_datetime(format='%Y-%m-%d', errors='coerce')` |
| Strip leading/trailing whitespace | All tables (string cols) | `.str.strip()` |
| Normalize categoricals to known set | claims, claimants, providers, policies, vehicles | Values outside known set → `pd.NA` |
| Flag non-positive amounts as NA | claims, policies, invoices | `value <= 0 → pd.NA` |
| Flag out-of-range age as NA | claimants | `age < 18 or > 100 → pd.NA` |
| Flag out-of-range model_year as NA | vehicles | `model_year < 1990 or > 2026 → pd.NA` |
| Flag out-of-range rating as NA | providers | `rating < 0 or > 5 → pd.NA` |
| Remove duplicate primary keys | All tables | Keep first occurrence, log count |
| Flag invalid policy date order | policies | `end_date <= start_date → date_order_invalid=True` |

---

## Synthetic Fields

| Field | Table | Description |
|---|---|---|
| `fraud_label` | claims | Synthetic ground-truth label (0/1). Not real fraud evidence. |
| `name` | claimants | Anonymized synthetic name ('Customer NNNN'). Not real names. |
| `description` | claims, invoices | Template-generated text. Not real claim narrative. |
| `registration_no` | vehicles | Synthetic Maharashtra registration plate numbers. |

---

## Derived Fields Added by Cleaning

| Field | Table | Derivation |
|---|---|---|
| `date_order_invalid` | policies (clean) | Boolean flag: `end_date <= start_date`. Derived from existing date columns. |

---

## Known Data Limitations

1. **All data is synthetic.** No real insurance claims, claimants, or providers.
2. **`locations_raw.csv` is orphaned.** No FK links it to claims, claimants, or providers. City string matching is the only possible join — not implemented in schema.
3. **4 policies have `end_date <= start_date`.** These are flagged but retained because they are referenced by claims (FK integrity must be preserved). Policy IDs: POL0039, POL0063, POL0076, POL0134.
4. **86 claims have dates outside the policy date range.** This is a data quality issue in the synthetic source. Flagged in validation report. NOT corrected — modifying claim or policy dates would introduce assumptions.
5. **Class imbalance.** Fraud rate is 16.25% (52/320). Any ML model must account for this.
6. **Claim descriptions are template text** (length ~20 chars, low entropy). Not suitable for NLP/text feature extraction.
7. **All registration plates are MH-prefix.** Geographic diversity is only in city column.

---

## Reproducibility

Run the full pipeline with:
```
python -m src.data.pipeline
```

Outputs (deterministic, no random seed required for cleaning phase):
- `data/processed/*.csv` — 7 cleaned tables
- `reports/data_quality_report.json`
- `docs/DATA_QUALITY.md`
- `data/provenance/DATA_GENERATION.md`
- `logs/pipeline.log`

---

*Generated by `python -m src.data.pipeline`*