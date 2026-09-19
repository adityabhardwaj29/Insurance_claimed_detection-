# Supabase PostgreSQL Database Architecture & Migrations

## 1. Overview

FraudShield AI uses **Supabase PostgreSQL** as its primary production relational store, with full support for local SQLite for developer ergonomics, CI/CD automated test suites, and offline resilience.

All schemas are version-controlled under `database/migrations/`:
1. `001_initial_schema.sql` — Core business entities.
2. `002_fraud_analytics.sql` — ML feature vectors, anomaly outputs, graph topology, and risk scores.
3. `003_case_management.sql` — SIU investigation cases, evidence files, case notes, and audit trails.
4. `004_rls_policies.sql` — Supabase Row-Level Security (RLS) policies.

---

## 2. Entity Relationship Summary

```
+---------------+       +---------------+       +---------------+
|   claimants   | <---< |   policies    | <---< |    claims     |
+---------------+       +---------------+       +---------------+
       |                                                |
       |                                                | 1:1
       v                                                v
+---------------+                             +-------------------+
|   vehicles    |                             |  risk_scores      |
+---------------+                             +-------------------+
                                                        |
                                                        | 1:1 (conditional)
                                                        v
                                              +-------------------+
                                              |investigation_cases|
                                              +-------------------+
                                                        |
                                           +------------+------------+
                                           |                         |
                                           v                         v
                                    +--------------+          +--------------+
                                    |  case_notes  |          |case_evidence |
                                    +--------------+          +--------------+
```

---

## 3. Migration Scripts Breakdown

### Migration 001: Initial Core Schema (`001_initial_schema.sql`)
- `roles`: Role definitions (`ADMIN`, `CLAIMS_OFFICER`, `INVESTIGATOR`, `SUPERVISOR`, `ANALYST`).
- `profiles`: User accounts, hashed passwords, department, badge number.
- `claimants`: Master customer identity records.
- `providers`: Medical clinics, body shops, attorneys, and rental agencies.
- `policies`: Underwriting policies, coverage limits, deductibles, and effective dates.
- `vehicles`: Insured vehicle records with VIN, make, model, year, and license plate.
- `claims`: Core loss events, damage amounts, collision circumstances, and status.

### Migration 002: Fraud Analytics & Models (`002_fraud_analytics.sql`)
- `claim_features`: 38 normalized ML feature values for every claim.
- `duplicate_matches`: Matched claim pairs, similarity scores, and match justifications.
- `anomaly_results`: Isolation Forest anomaly scores and outlier classifications.
- `fraud_predictions`: Supervised XGBoost probabilities and prediction timestamps.
- `graph_nodes` & `graph_edges`: Network topology representing bipartite relationship clusters.
- `risk_scores`: Blended hybrid risk scores (0.0 to 1.0), risk tier, and automated recommendations.

### Migration 003: Case Management & Auditing (`003_case_management.sql`)
- `documents`: Uploaded corroborating evidence files and filesystem metadata.
- `investigation_cases`: SIU case dockets automatically generated for claims with risk >= 0.50.
- `case_notes`: Forensic annotations and investigator findings.
- `case_evidence`: Evidence items tied to SIU dockets.
- `case_events`: Disposition timeline and milestone tracker.
- `audit_logs`: Immutable, append-only regulatory audit log stream.

### Migration 004: Row-Level Security (`004_rls_policies.sql`)
- Enables PostgreSQL `ROW LEVEL SECURITY` across all tables.
- Implements granular `SELECT`, `INSERT`, `UPDATE` policies tied to authenticated JWT user roles.

---

## 4. Migrating from SQLite to Supabase

The platform includes an automated migration CLI: `database/migrate_to_supabase.py`.

### Execution:
```powershell
# Set your Supabase connection strings in .env:
# DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres

python database/migrate_to_supabase.py
```

### Verification:
The migration CLI automatically executes post-migration table row counts and schema constraint validation to guarantee complete data fidelity.
