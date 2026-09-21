# FraudShield AI — Database Architecture & Migrations

This directory contains database DDL schemas, migration scripts, analytical views, and seeders for FraudShield AI. The platform is designed with a **dual-engine architecture**: local SQLite for immediate zero-config development/testing, and Supabase PostgreSQL for cloud production.

---

## 1. Directory Overview

```text
database/
├── migrations/               # Sequential PostgreSQL migration files
│   ├── 001_initial_schema.sql  # 7 relational core entity tables & enums
│   ├── 002_fraud_analytics.sql # Risk score tracking tables & analytics views
│   ├── 003_case_management.sql # SIU case management & audit event logging
│   └── 004_rls_policies.sql    # Row-Level Security policies & role permissions
├── fraud_detection.db        # Pre-seeded local SQLite database (for dev/test)
├── indexes.sql               # B-Tree index definitions for foreign keys & queries
├── migrate_to_supabase.py    # Automated SQLite -> Supabase migration script
├── schema.sql                # Complete consolidated PostgreSQL DDL schema
├── seed.py                   # Deterministic SQLite database seeder
├── seed.sql                  # Sample test SQL insert statements
└── views.sql                 # Analytical SQL view definitions
```

---

## 2. Core Relational Entities

The data model conforms to Third Normal Form (3NF) across 7 normalized entity tables:

1. **`claimants`**: Policyholder demographics, contact information, risk tier.
2. **`policies`**: Insurance policy contracts, coverage limits, effective dates.
3. **`vehicles`**: Insured vehicles, VIN numbers, make, model, odometer readings.
4. **`providers`**: Body shops, medical clinics, towing services, ratings.
5. **`invoices`**: Billing records, line items, submission timestamps.
6. **`claims`**: Central transaction linking claimant, policy, provider, invoice, and vehicle.
7. **`locations`**: Geo-spatial incident and repair shop coordinates.

---

## 3. Investigation & Case Management Entities

* **`risk_scores`**: Composite risk scores, fraud probabilities, anomaly scores, and risk bands.
* **`investigation_cases`**: Special Investigation Unit (SIU) cases, priority levels, assigned investigators, and disposition statuses (`NEW`, `ASSIGNED`, `IN_REVIEW`, `CLOSED_FRAUD`, `CLOSED_CLEAN`).
* **`case_events`**: Append-only immutable audit trail capturing every state change and action.
* **`case_notes`**: Internal notes and evidence logs recorded by investigators.

---

## 4. Seeding Local SQLite

To initialize or re-seed the local SQLite database from `data/relational/*.csv`:
```cmd
python scripts/seed.py
```
This applies the schema, inserts records in dependency order, auto-populates SIU cases from high-risk claims, and prints row count verification.

---

## 5. Migrating to Supabase PostgreSQL

To sync local data and schemas to Supabase PostgreSQL:
1. Ensure `DATABASE_URL` is set in your `.env` file:
   ```env
   DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres
   ```
2. Execute the migration runner:
   ```cmd
   python scripts/migrate.py --target supabase
   ```
The migration script automatically applies table DDL, batch-transfers records, verifies row count equality, and generates `reports/SUPABASE_MIGRATION_REPORT.json`.
