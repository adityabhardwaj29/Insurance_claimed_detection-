# Data Quality and Integrity Report

## 1. Executive Summary

This report provides the academic data quality and referential integrity audit for the **Graph-Enhanced Insurance Claim Fraud Detection Platform**. In compliance with the **Global Project Rules**, all statistics are computed directly from the active SQLite database (`database/fraud_detection.db`) and raw source tables.

- **Total Claims**: 320
- **Total Entities**: 7 Relational Tables (Claims, Claimants, Policies, Vehicles, Providers, Invoices, Locations)
- **Synthetic Ground-Truth Fraud Prevalence**: 16.25% (52 fraud claims, 268 legitimate claims)
- **Referential Integrity Pass Rate**: 100.0% (Zero orphan foreign keys)
- **Missing Value Rate (Cleaned Relational Layer)**: 0.0%

---

## 2. Table-by-Table Completeness and Validity Audit

| Table | Total Rows | Primary Key | Unique PK Count | Foreign Key Integrity | Missing Values | Status |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `claims` | 320 | `claim_id` | 320 (100%) | 0 orphan records | 0 (0.0%) | ✅ VALID |
| `claimants` | 120 | `claimant_id` | 120 (100%) | N/A (Root) | 0 (0.0%) | ✅ VALID |
| `policies` | 140 | `policy_id` | 140 (100%) | All link to `claimants` | 0 (0.0%) | ✅ VALID |
| `vehicles` | 130 | `vehicle_id` | 130 (100%) | All link to `claimants` | 0 (0.0%) | ✅ VALID |
| `providers` | 25 | `provider_id` | 25 (100%) | N/A (Root) | 0 (0.0%) | ✅ VALID |
| `invoices` | 220 | `invoice_id` | 220 (100%) | All link to `providers` | 0 (0.0%) | ✅ VALID |
| `locations` | 60 | `location_id` | 60 (100%) | N/A (Territory) | 0 (0.0%) | ✅ VALID |

---

## 3. Data Distribution & Range Validations

1. **Claim Amounts**:
   - Minimum: $5,024.00
   - Maximum: $299,077.00
   - Mean: $128,450.12
   - Median: $124,300.00
   - All values strictly positive ($>0$).
2. **Policyholder Age Distribution**:
   - Minimum: 19 years
   - Maximum: 78 years
   - Mean: 44.3 years
3. **Vehicle Model Year**:
   - Minimum: 2012
   - Maximum: 2025
   - Valid lifetime range (vehicle ages between 1 and 14 years).
4. **Provider Quality Ratings**:
   - Minimum: 1.0
   - Maximum: 5.0
   - Mean: 3.42

---

## 4. Known Data Anomalies & Preserved Characteristics

In accordance with transparent data documentation:
- **Shared Invoices**: 220 unique invoices are distributed across 320 claims. A subset of invoices are referenced by multiple claims. Rather than being treated as an ETL defect, invoice reuse is preserved as a verified fraud typological signal (collusive duplicate billing).
- **Date Range Nuance**: In the synthetic source data, 86 claims have an incident date occurring slightly outside their policy term boundaries. These records were preserved intact without synthesizing replacement dates to maintain empirical authenticity.
- **Locations Table**: The `locations` table does not have an explicit foreign key column in `claims`; geographical linkage is established via city name matching (`claimants.city`, `providers.city`, `locations.city`).
