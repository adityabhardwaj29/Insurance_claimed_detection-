# Data Dictionary
## Graph-Enhanced Insurance Claim Fraud Detection

**Version:** 1.0.0
**Generated:** Phase 2 Relational Model
**Source data:** Synthetic project-generated data. Not real insurance data.

---

## Table of Contents

1. [Dataset Overview](#dataset-overview)
2. [Entity Relationship Summary](#entity-relationship-summary)
3. [claimants](#claimants)
4. [policies](#policies)
5. [vehicles](#vehicles)
6. [providers](#providers)
7. [invoices](#invoices)
8. [claims](#claims)
9. [locations](#locations)
10. [Analytical Views](#analytical-views)
11. [Known Limitations](#known-limitations)

---

## Dataset Overview

| Attribute | Value |
|---|---|
| Nature | **Synthetic project-generated data** |
| Real insurance data | No |
| Master source | `data/master/insurance_claim_dataset.xlsx` |
| Cleaned source | `data/processed/` |
| Relational layer | `data/relational/` |
| Total entities | 7 tables |
| Total claims | 320 |
| Total claimants | 120 |
| Fraud rate | 16.25% (52/320) — synthetic ground truth |

> [!IMPORTANT]
> The `fraud_label` field is a **synthetic ground-truth label** created for this project. It does not reflect real fraud investigation outcomes.

---

## Entity Relationship Summary

```
claimants (120)
    ├── policies (140)      1:N  claimant has many policies
    ├── vehicles (130)      1:N  claimant owns many vehicles
    └── claims  (320)       1:N  claimant files many claims

providers (25)
    ├── invoices (220)      1:N  provider issues many invoices
    └── claims  (320)       1:N  provider handles many claims

claims (320)  — CENTRAL FACT TABLE
    ├── → claimant_id    M:1  → claimants
    ├── → policy_id      M:1  → policies
    ├── → vehicle_id     M:1  → vehicles
    ├── → provider_id    M:1  → providers
    └── → invoice_id     M:1  → invoices  [NOT 1:1; invoices may be shared]

locations (60)  — ORPHANED
    No FK reference from any other table.
    Join only via city string match (documented limitation).
```

**Key cardinalities (computed from data):**
- Policies per claimant: 1–4 (mean 1.67)
- Vehicles per claimant: 1–4 (mean 1.65)
- Claims per claimant: 1–7 (mean 2.83)
- Claims per policy: 1–7 (mean 2.67)
- Invoice reuse: 153 of 320 claims share their invoice_id with ≥1 other claim

---

## claimants

**Source:** `data/raw/claimants_raw.csv` → `data/processed/claimants_clean.csv` → `data/relational/claimants.csv`
**Rows:** 120
**Primary key:** `claimant_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `claimant_id` | VARCHAR(10) | Unique claimant identifier | Source | No | CLT0001 – CLT0120 (format: CLT + 4 digits) |
| `name` | VARCHAR(120) | Claimant name | Source | No | Synthetic names: "Customer 0001" etc. Not real names. |
| `age` | SMALLINT | Age in years at time of dataset generation | Source | Yes (if invalid) | 18–100. Values outside range flagged as NULL during cleaning. |
| `city` | VARCHAR(40) | City of residence | Source | Yes (if unknown) | Mumbai, Pune, Delhi, Ahmedabad, Surat |
| `gender` | CHAR(1) | Gender | Source | Yes | M (Male), F (Female) |
| `marital_status` | VARCHAR(10) | Marital status | Source | Yes | Married, Single |

**Notes:**
- `name` values are synthetic anonymized placeholders ("Customer NNNN"). Not real personal data.
- 120 unique claimants; not all claimants have claims (some may be policy holders only).
- 84 of 120 claimants are referenced in at least one policy.
- 113 of 120 claimants are referenced in at least one claim.

---

## policies

**Source:** `data/raw/policies_raw.csv` → `data/processed/policies_clean.csv` → `data/relational/policies.csv`
**Rows:** 140
**Primary key:** `policy_id`
**Foreign key:** `claimant_id → claimants.claimant_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `policy_id` | VARCHAR(10) | Unique policy identifier | Source | No | POL0001 – POL0140 (format: POL + 4 digits) |
| `claimant_id` | VARCHAR(10) | FK to policy holder | Source | No | Valid claimant_id |
| `start_date` | DATE | Policy coverage start | Source (parsed) | Yes | ISO-8601 date. Raw was stored as string. |
| `end_date` | DATE | Policy coverage end | Source (parsed) | Yes | ISO-8601 date. Raw was stored as string. |
| `policy_type` | VARCHAR(20) | Type of coverage | Source | Yes | Comprehensive, Zero Dep, Third Party |
| `premium` | DECIMAL(12,2) | Annual premium amount (INR) | Source | Yes | > 0. Observed range: 15,150–89,691. |
| `date_order_invalid` | BOOLEAN | Quality flag from Phase 1 cleaning | Derived | No | TRUE if end_date ≤ start_date. Default FALSE. |

**Notes:**
- 4 policies have `date_order_invalid = TRUE`: POL0039, POL0063, POL0076, POL0134. These are a synthetic data quality issue; the rows are retained because they are referenced by claims (FK preservation).
- `date_order_invalid` is a **derived field** added during Phase 1 cleaning. It is not in the original source dataset.
- 120 of 140 policies are referenced by at least one claim.

---

## vehicles

**Source:** `data/raw/vehicles_raw.csv` → `data/processed/vehicles_clean.csv` → `data/relational/vehicles.csv`
**Rows:** 130
**Primary key:** `vehicle_id`
**Foreign key:** `claimant_id → claimants.claimant_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `vehicle_id` | VARCHAR(10) | Unique vehicle identifier | Source | No | VEH0001 – VEH0130 (format: VEH + 4 digits) |
| `claimant_id` | VARCHAR(10) | FK to vehicle owner | Source | No | Valid claimant_id |
| `make` | VARCHAR(20) | Vehicle manufacturer | Source | Yes | Tata, Maruti, Hyundai, Mahindra, Honda |
| `vehicle_type` | VARCHAR(20) | Vehicle body type | Source | Yes | MUV, Sedan, Hatchback, SUV |
| `registration_no` | VARCHAR(20) | Vehicle registration plate | Source | Yes | All MH-prefix (Maharashtra). Synthetic. Not real plates. |
| `model_year` | SMALLINT | Year of manufacture | Source | Yes | 1990–2026. Observed range: 2018–2025. |

**Notes:**
- All `registration_no` values are synthetic Maharashtra (MH) plates; they do not correspond to real vehicles.
- Multiple vehicles per claimant is allowed (observed: up to 4 per claimant).

---

## providers

**Source:** `data/raw/providers_raw.csv` → `data/processed/providers_clean.csv` → `data/relational/providers.csv`
**Rows:** 25
**Primary key:** `provider_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `provider_id` | VARCHAR(10) | Unique provider identifier | Source | No | PRV001 – PRV025 (format: PRV + 3 digits) |
| `provider_name` | VARCHAR(120) | Provider display name | Source | No | Synthetic: "Provider 001" etc. |
| `city` | VARCHAR(40) | Provider location city | Source | Yes | Mumbai, Pune, Delhi, Ahmedabad, Surat |
| `provider_type` | VARCHAR(20) | Category of service | Source | Yes | Surveyor, Dealer, Garage, Hospital |
| `rating` | DECIMAL(3,1) | Provider quality rating | Source | Yes | 0.0–5.0. Observed range: 3.1–4.8. |

**Notes:**
- 25 providers handle 320 claims (avg 12.8 claims/provider).
- Provider names are synthetic placeholders ("Provider 001").
- Surveyors and Garages are the most common provider types.

---

## invoices

**Source:** `data/raw/invoices_raw.csv` → `data/processed/invoices_clean.csv` → `data/relational/invoices.csv`
**Rows:** 220
**Primary key:** `invoice_id`
**Foreign key:** `provider_id → providers.provider_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `invoice_id` | VARCHAR(12) | Unique invoice identifier | Source | No | INV00001 – INV00220 (format: INV + 5 digits) |
| `provider_id` | VARCHAR(10) | FK to issuing provider | Source | No | Valid provider_id |
| `invoice_amount` | DECIMAL(12,2) | Invoice value (INR) | Source | Yes | > 0. Observed range: 8,910–179,959. |
| `invoice_date` | DATE | Date invoice was issued | Source (parsed) | Yes | ISO-8601 date. Raw stored as string. |
| `description` | TEXT | Invoice description text | Source | Yes | Template text ("Invoice description N"). Low entropy. |

> [!WARNING]
> **Invoice reuse:** 167 unique `invoice_id` values appear in 320 claims. 153 claims share an invoice with at least one other claim. The maximum reuse is **7 claims per invoice**. This is a **source-data characteristic**, not a data error. It is preserved as-is and documented as a potential fraud signal for graph analysis.

---

## claims

**Source:** `data/raw/claims_raw.csv` → `data/processed/claims_clean.csv` → `data/relational/claims.csv`
**Rows:** 320
**Primary key:** `claim_id`
**Foreign keys:** `claimant_id`, `policy_id`, `vehicle_id`, `provider_id`, `invoice_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `claim_id` | VARCHAR(12) | Unique claim identifier | Source | No | CLM00001 – CLM00320 (format: CLM + 5 digits) |
| `claimant_id` | VARCHAR(10) | FK to claimant who filed the claim | Source | No | Valid claimant_id |
| `policy_id` | VARCHAR(10) | FK to policy under which claim is filed | Source | No | Valid policy_id |
| `vehicle_id` | VARCHAR(10) | FK to vehicle involved in claim | Source | No | Valid vehicle_id |
| `provider_id` | VARCHAR(10) | FK to provider who handled the claim | Source | No | Valid provider_id |
| `invoice_id` | VARCHAR(12) | FK to invoice for the claim | Source | No | Valid invoice_id. May be shared across claims. |
| `claim_date` | DATE | Date claim was filed | Source (parsed) | Yes | ISO-8601. Observed range: 2026-01-03 – 2026-09-07. |
| `claim_amount` | DECIMAL(12,2) | Claimed amount (INR) | Source | Yes | > 0. Observed range: 5,024–299,077. |
| `claim_type` | VARCHAR(30) | Category of claim | Source | Yes | Theft, Glass Damage, Fire, Accident, Natural Disaster |
| `status` | VARCHAR(20) | Current status of claim | Source | Yes | Open, Approved, Under Review, Rejected |
| `fraud_label` | SMALLINT | Ground-truth fraud label | Source | No | **0** = Legitimate, **1** = Fraud |
| `description` | TEXT | Claim description text | Source | Yes | Template text ("Claim description N"). Low entropy. |

> [!IMPORTANT]
> `fraud_label` is a **synthetic ground-truth label** generated with the dataset. It is **not** derived from real fraud investigation outcomes. Distribution: 268 legitimate (83.75%), 52 fraud (16.25%). Class imbalance ratio: 5.15:1.

**Additional notes:**
- 86 claims have `claim_date` outside the `[start_date, end_date]` range of their referenced policy. This is a synthetic data quality issue, not corrected (would require inventing dates).
- `description` text is extremely low entropy (length ~20 chars, template generated). Not suitable for NLP features.

---

## locations

**Source:** `data/raw/locations_raw.csv` → `data/processed/locations_clean.csv` → `data/relational/locations.csv`
**Rows:** 60
**Primary key:** `location_id`

| Field | Type | Description | Source | Nullable | Allowed Values |
|---|---|---|---|---|---|
| `location_id` | VARCHAR(8) | Unique location identifier | Source | No | LOC001 – LOC060 (format: LOC + 3 digits) |
| `city` | VARCHAR(40) | City name | Source | Yes | Mumbai (16), Delhi (13), Surat (13), Ahmedabad (10), Pune (8) |
| `latitude` | DECIMAL(9,6) | Geographic latitude (decimal degrees) | Source | Yes | India bounding box: 6–36. Observed: 18.49–28.68. |
| `longitude` | DECIMAL(9,6) | Geographic longitude (decimal degrees) | Source | Yes | India bounding box: 68–98. Observed: 72.86–77.45. |

> [!WARNING]
> **Orphaned table.** `locations` has no foreign key from any other table. The only possible join is via `city` string matching with `claimants.city`, `providers.city`, or location-level coordinates. This is a source-data limitation. The table is retained as-is and documented.

---

## Analytical Views

These views are defined in `database/views.sql` and computed from the relational tables. All values are derived from actual data.

| View | Description |
|---|---|
| `claim_risk_base` | Denormalized claim-level view joining all dimension tables. Input for scoring pipeline. |
| `provider_summary` | Per-provider: total claims, unique claimants, total/avg claim amount, fraud count, fraud rate. |
| `claimant_summary` | Per-claimant: total claims, total/avg claim amount, date range, fraud claims, policies/providers used. |
| `fraud_overview` | Dataset-level: total claims, fraud/legit counts, fraud rate, total/avg amounts. |
| `invoice_reuse` | Invoices referenced by more than one claim; potential fraud signal. |

---

## Known Limitations

| ID | Limitation | Affected Entities | Impact |
|---|---|---|---|
| L1 | All data is synthetic | All | No real-world fraud patterns; label validity is assumed |
| L2 | 4 policies have end_date ≤ start_date | policies | Flagged; not corrected (FK constraint) |
| L3 | 86 claims are outside their policy date range | claims, policies | Synthetic artefact; not corrected |
| L4 | locations table is orphaned (no FK) | locations | Can only join via city string |
| L5 | invoice_ids shared across multiple claims | invoices, claims | Preserved; documented as fraud signal |
| L6 | claim/invoice description is template text | claims, invoices | Not suitable for NLP |
| L7 | All registration plates are MH-prefix | vehicles | No geographic diversity in plates |
| L8 | Class imbalance 5.15:1 (legit:fraud) | claims | ML models must use class balancing |
| L9 | previous_rejections in old feature files is uniformly distributed | data/features/ (Phase 1 legacy) | Legacy synthetic feature files are invalid |

---

*This data dictionary was generated as part of Phase 2: Relational Insurance Data Model.*
*All transformations are reproducible via `python -m src.data.relational_builder`.*
