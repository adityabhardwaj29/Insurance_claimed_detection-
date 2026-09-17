# Relational Entity-Relationship (ER) Architecture

## 1. Database Schema Overview

The relational database is implemented using **SQLite** (`database/fraud_detection.db`) with strict enforcement of referential integrity (`PRAGMA foreign_keys = ON;`). All entities are normalized into 3rd Normal Form (3NF) to eliminate data redundancy and prevent update anomalies.

---

## 2. Entity-Relationship Diagram

```
+------------------+             +-------------------+             +------------------+
|    claimants     | 1         * |     policies      | 1         * |      claims      |
+------------------+-------------+-------------------+-------------+------------------+
| PK claimant_id   |             | PK policy_id      |             | PK claim_id      |
|    name          |             | FK claimant_id    |             | FK claimant_id   |
|    age           |             |    policy_type    |             | FK policy_id     |
|    gender        |             |    premium        |             | FK vehicle_id    |
|    marital_status|             |    start_date     |             | FK provider_id   |
|    city          |             |    end_date       |             | FK invoice_id    |
+------------------+             +-------------------+             |    claim_date    |
         | 1                                                       |    claim_amount  |
         |                                                         |    claim_type    |
         | *                                                       |    status        |
+------------------+                                               |    fraud_label   |
|    vehicles      | 1                                           * |    description   |
+------------------+-----------------------------------------------+------------------+
| PK vehicle_id    |                                                       | *
| FK claimant_id   |                                                       |
|    make          |                                                       |
|    vehicle_type  |                                                       | 1
|    model_year    |                                               +------------------+
+------------------+                                               |    providers     |
                                                                   +------------------+
                                                                   | PK provider_id   |
                                                                   |    provider_name |
                                                                   |    provider_type |
                                                                   |    rating        |
                                                                   |    city          |
                                                                   +------------------+
                                                                           | 1
                                                                           |
                                                                           | *
+------------------+                                               +------------------+
|    locations     |                                               |     invoices     |
+------------------+                                               +------------------+
| PK location_id   |                                               | PK invoice_id    |
|    city          |                                               | FK provider_id   |
|    state         |                                               |    invoice_date  |
|    latitude      |                                               |    invoice_amount|
|    longitude     |                                               +------------------+
+------------------+
```

---

## 3. Investigation & Audit Subsystem (Phase 9)

```
+------------------------------------+
|        investigation_cases         |
+------------------------------------+
| PK case_id                         |
| FK claim_id -> claims(claim_id)    |
|    risk_score                      |
|    risk_band                       |
|    priority                        |
|    status                          |
|    assigned_to                     |
|    reason                          |
|    notes                           |
|    resolution                      |
|    created_at                      |
|    updated_at                      |
+------------------------------------+
         | 1                       | 1
         |                         |
         | *                       | *
+--------------------+   +--------------------+
|     case_notes     |   |    case_events     |
+--------------------+   +--------------------+
| PK note_id         |   | PK event_id        |
| FK case_id         |   | FK case_id         |
|    author          |   |    event_type      |
|    note_text       |   |    actor           |
|    created_at      |   |    old_value       |
+--------------------+   |    new_value       |
                         |    details         |
                         |    timestamp       |
                         +--------------------+
```

---

## 4. Table Definitions and Row Counts

| Table Name | Description | Primary Key | Foreign Keys | Row Count |
| :--- | :--- | :--- | :--- | :---: |
| `claims` | Central insurance claim transactions | `claim_id` | `claimant_id`, `policy_id`, `vehicle_id`, `provider_id`, `invoice_id` | 320 |
| `claimants` | Individual policyholders filing claims | `claimant_id` | None | 120 |
| `policies` | Insurance coverage contracts | `policy_id` | `claimant_id` | 140 |
| `vehicles` | Insured automobiles and assets | `vehicle_id` | `claimant_id` | 130 |
| `providers` | Auto repair shops and medical providers | `provider_id` | None | 25 |
| `invoices` | Billing line items issued by providers | `invoice_id` | `provider_id` | 220 |
| `locations` | Geographic territory and coordinates | `location_id` | None | 60 |
| `investigation_cases` | SIU fraud review cases | `case_id` | `claim_id` | Active Queue |
| `case_notes` | Running notes logged by investigators | `note_id` | `case_id` | Dynamic |
| `case_events` | Immutable chronological audit trail | `event_id` | `case_id` | Dynamic |

---

## 5. Analytical SQL Views

1. **`v_claim_summary`**:
   - Denormalizes claim records with claimant name, provider name, policy type, vehicle make, and invoice amount for rapid dashboard querying.
2. **`v_high_risk_claims`**:
   - Filters claims with high risk scores or flagged fraud patterns for SIU investigator assignment.
3. **`v_provider_analytics`**:
   - Aggregates claim frequency, average claim amount, and fraud-association ratios grouped by repair provider.
