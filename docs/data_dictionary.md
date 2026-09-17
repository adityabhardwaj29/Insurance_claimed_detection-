# Data Dictionary
## Graph-Enhanced Insurance Claim Fraud Detection

**Version:** 2.0.0  
**Generated:** Phase 15 Final Documentation  
**Source data:** Synthetic project-generated research data. Not real customer insurance data.

---

## Table of Contents

1. [Dataset Provenance & Classification](#dataset-provenance--classification)
2. [Relational Schema Summary](#relational-schema-summary)
3. [claimants](#claimants)
4. [policies](#policies)
5. [vehicles](#vehicles)
6. [providers](#providers)
7. [invoices](#invoices)
8. [claims](#claims)
9. [locations](#locations)
10. [investigation_cases & audit](#investigation_cases--audit)
11. [Derived Feature Store Tables](#derived-feature-store-tables)
12. [Analytical Views](#analytical-views)
13. [Academic & Practical Limitations](#academic--practical-limitations)

---

## 1. Dataset Provenance & Classification

| Data Tier | Storage Location | Description |
| :--- | :--- | :--- |
| **SOURCE DATA** | `data/raw/` | Raw simulated flat files generated for academic fraud modeling. |
| **PROCESSED DATA**| `data/relational/` | Normalized tables cleaned without mutating synthetic facts. |
| **DERIVED DATA** | `data/features/` | Computed feature matrices (`claim_features.csv`, `duplicate_features.csv`, `graph_features.csv`). |
| **MODEL OUTPUT** | `models/`, `data/features/final_risk_scores.csv` | Verifiable machine learning predictions, anomaly scores, and calibrated hybrid risk scores. |

> [!IMPORTANT]
> The `fraud_label` field is a **synthetic ground-truth label** created for this research project. It does not reflect real insurance company investigation records.
> Observed fraud rate: **16.25%** (52 fraud out of 320 claims).

---

## 2. Relational Schema Summary

```
claimants (120)
    |-- policies (140)      1:N  claimant has many policies
    |-- vehicles (130)      1:N  claimant owns many vehicles
    +-- claims  (320)       1:N  claimant files many claims

providers (25)
    |-- invoices (220)      1:N  provider issues many invoices
    +-- claims  (320)       1:N  provider handles many claims

claims (320) -- CENTRAL FACT TABLE
    |-- claimant_id   M:1  -> claimants
    |-- policy_id     M:1  -> policies
    |-- vehicle_id    M:1  -> vehicles
    |-- provider_id   M:1  -> providers
    +-- invoice_id    M:1  -> invoices

investigation_cases (Active Queue)
    +-- claim_id      M:1  -> claims
```

---

## 3. claimants
**Source:** `data/relational/claimants.csv` | **Rows:** 120 | **PK:** `claimant_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `claimant_id` | TEXT | Primary key identifier | No | Format: `CLT0001` - `CLT0120` |
| `name` | TEXT | Full name of policyholder | No | Synthetic name generator |
| `age` | INTEGER | Age of policyholder | No | 19 - 78 years |
| `gender` | TEXT | Gender | No | Male, Female, Other |
| `marital_status`| TEXT | Marital status | No | Single, Married, Divorced |
| `city` | TEXT | Residential city | No | Mumbai, Delhi, Ahmedabad, Surat, Pune |

---

## 4. policies
**Source:** `data/relational/policies.csv` | **Rows:** 140 | **PK:** `policy_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `policy_id` | TEXT | Primary key identifier | No | Format: `POL0001` - `POL0140` |
| `claimant_id` | TEXT | Foreign key to claimants | No | Valid `claimant_id` |
| `policy_type` | TEXT | Coverage tier | No | Comprehensive, Third Party, Zero Depreciation |
| `premium` | REAL | Annual premium amount | No | $10,000 - $150,000 |
| `start_date` | TEXT | Inception date (ISO 8601) | No | 2025-01-01 to 2026-06-30 |
| `end_date` | TEXT | Policy expiry date (ISO 8601)| No | 2026-01-01 to 2027-06-30 |

---

## 5. vehicles
**Source:** `data/relational/vehicles.csv` | **Rows:** 130 | **PK:** `vehicle_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `vehicle_id` | TEXT | Primary key identifier | No | Format: `VEH0001` - `VEH0130` |
| `claimant_id` | TEXT | Foreign key to claimants | No | Valid `claimant_id` |
| `make` | TEXT | Automobile manufacturer | No | Maruti, Hyundai, Tata, Mahindra, Toyota, Honda |
| `vehicle_type`| TEXT | Body style | No | Sedan, SUV, Hatchback |
| `model_year` | INTEGER | Year of manufacture | No | 2012 - 2025 |

---

## 6. providers
**Source:** `data/relational/providers.csv` | **Rows:** 25 | **PK:** `provider_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `provider_id` | TEXT | Primary key identifier | No | Format: `PRV001` - `PRV025` |
| `provider_name`| TEXT | Facility name | No | Repair shop or authorized dealer |
| `city` | TEXT | Operating city | No | Mumbai, Delhi, Ahmedabad, Surat, Pune |
| `provider_type`| TEXT | Category | No | Authorized, Independent, Body Shop |
| `rating` | REAL | Customer quality score | No | 1.0 - 5.0 |

---

## 7. invoices
**Source:** `data/relational/invoices.csv` | **Rows:** 220 | **PK:** `invoice_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `invoice_id` | TEXT | Primary key identifier | No | Format: `INV0001` - `INV0220` |
| `provider_id` | TEXT | Foreign key to providers | No | Valid `provider_id` |
| `invoice_date`| TEXT | Invoice date (ISO 8601) | No | 2026-01-01 to 2026-09-10 |
| `invoice_amount`| REAL | Billed repair total | No | $3,500 - $320,000 |

---

## 8. claims
**Source:** `data/relational/claims.csv` | **Rows:** 320 | **PK:** `claim_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `claim_id` | TEXT | Primary key identifier | No | Format: `CLM00001` - `CLM00320` |
| `claimant_id` | TEXT | Foreign key to claimants | No | Valid `claimant_id` |
| `policy_id` | TEXT | Foreign key to policies | No | Valid `policy_id` |
| `vehicle_id` | TEXT | Foreign key to vehicles | No | Valid `vehicle_id` |
| `provider_id` | TEXT | Foreign key to providers | No | Valid `provider_id` |
| `invoice_id` | TEXT | Foreign key to invoices | No | Valid `invoice_id` |
| `claim_date` | TEXT | Date claim was filed | No | 2026-01-03 to 2026-09-07 |
| `claim_amount`| REAL | Total claimed amount | No | $5,024 - $299,077 |
| `claim_type` | TEXT | Incident type | No | Theft, Glass Damage, Fire, Accident, Natural Disaster |
| `status` | TEXT | Current operational status | No | Open, Approved, Under Review, Rejected |
| `fraud_label` | INTEGER | Synthetic ground truth | No | `0` = Legitimate (83.75%), `1` = Fraud (16.25%) |
| `description` | TEXT | Textual claim description | Yes | Natural text describing incident |

---

## 9. locations
**Source:** `data/relational/locations.csv` | **Rows:** 60 | **PK:** `location_id`

| Field | Type | Description | Nullable | Domain / Observed Values |
| :--- | :--- | :--- | :---: | :--- |
| `location_id` | TEXT | Primary key identifier | No | Format: `LOC001` - `LOC060` |
| `city` | TEXT | Urban center | No | Mumbai, Delhi, Surat, Ahmedabad, Pune |
| `latitude` | REAL | Latitude coordinate | No | 18.49 - 28.68 |
| `longitude` | REAL | Longitude coordinate | No | 72.86 - 77.45 |

---

## 10. investigation_cases & Audit

### `investigation_cases`
| Field | Type | Description |
| :--- | :--- | :--- |
| `case_id` | TEXT PK | Unique case identifier (`CASE-CLMxxxxx`) |
| `claim_id` | TEXT FK | References `claims(claim_id)` |
| `risk_score` | REAL | Final hybrid risk score $[0, 1]$ |
| `risk_band` | TEXT | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `priority` | TEXT | Triage priority |
| `status` | TEXT | `NEW`, `UNDER_REVIEW`, `ESCALATED`, `RESOLVED`, `FALSE_POSITIVE` |
| `assigned_to`| TEXT | Investigator username or ID |
| `reason` | TEXT | Codified risk engine trigger explanations |
| `notes` | TEXT | Free-text case summary |
| `resolution` | TEXT | Final adjudication determination |

### `case_notes`
| Field | Type | Description |
| :--- | :--- | :--- |
| `note_id` | INTEGER PK | Auto-increment identifier |
| `case_id` | TEXT FK | References `investigation_cases(case_id)` |
| `author` | TEXT | Investigator adding the note |
| `note_text` | TEXT | Content of investigator note |
| `created_at`| TEXT | UTC timestamp (ISO 8601) |

### `case_events`
| Field | Type | Description |
| :--- | :--- | :--- |
| `event_id` | INTEGER PK | Auto-increment identifier |
| `case_id` | TEXT FK | References `investigation_cases(case_id)` |
| `event_type`| TEXT | `STATUS_CHANGED`, `INVESTIGATOR_ASSIGNED`, `PRIORITY_CHANGED`, `NOTE_ADDED` |
| `actor` | TEXT | User or system performing action |
| `old_value` | TEXT | Prior state |
| `new_value` | TEXT | Updated state |
| `details` | TEXT | Transition rationale |
| `timestamp` | TEXT | UTC timestamp (ISO 8601) |

---

## 11. Derived Feature Store Tables

1. **`claim_features.csv`**: 320 claims $\times$ 21 engineered financial, temporal, and categorical attributes.
2. **`duplicate_features.csv`**: Pairwise TF-IDF cosine similarity scores, matched pair IDs, and duplicate flags.
3. **`graph_features.csv`**: Degree centrality, clustering coefficients, provider claim counts, and fraud neighbor ratios.
4. **`final_risk_scores.csv`**: Multi-signal calibrated composite score, assigned operational risk band, component scores, and reason code strings.

---

## 12. Analytical Views

- **`v_claim_summary`**: Joins claim facts with policyholder, vehicle, provider, and invoice details.
- **`v_high_risk_claims`**: Filters claims where `risk_band IN ('HIGH', 'CRITICAL')`.
- **`v_provider_analytics`**: Aggregates claim volume and fraud-association rates per repair shop.

---

## 13. Academic & Practical Limitations

- All data is synthetic and generated for academic demonstration.
- The knowledge graph is processed in-memory via NetworkX.
- Static weights ($0.40, 0.20, 0.15, 0.25$) are used in the hybrid scoring engine.
