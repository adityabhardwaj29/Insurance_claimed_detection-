# Phase 9: Fraud Investigation Case Management Report

## Executive Summary

Phase 9 establishes the **Fraud Investigation Case Management** subsystem, providing an operational queue, investigator workflow, state transitions, running notes, evidence dossiers, and an immutable audit trail.

In accordance with the **Global Project Rules** and specific phase constraints:
> **Human-in-the-Loop Guarantee**: High-risk claims entering the investigation queue are **never** automatically declared fraudulent. The investigator workflow is strictly decision-support; determinations (`RESOLVED` vs `FALSE_POSITIVE`) require explicit investigator sign-off and documented justification. The underlying synthetic ground-truth dataset (`claims.fraud_label`) remains immutable and unaltered.

---

## 1. Database Architecture & Relational Schema

Three dedicated relational tables were added to both `database/schema.sql` (PostgreSQL / ANSI SQL) and SQLite DDL:

### Table Definitions

1. **`investigation_cases`**:
   - `case_id` (PK, e.g. `CASE-CLM00001`)
   - `claim_id` (FK $\to$ `claims.claim_id`)
   - `risk_score` (Numeric $[0, 1]$ from Phase 8)
   - `risk_band` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
   - `priority` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
   - `status` (`NEW`, `UNDER_REVIEW`, `ESCALATED`, `RESOLVED`, `FALSE_POSITIVE`)
   - `assigned_to` (Investigator name/ID)
   - `reason` (Explainable risk trigger codes)
   - `notes` (Latest summary notes)
   - `resolution` (Investigator final findings)
   - `created_at`, `updated_at` (ISO8601 UTC timestamps)

2. **`case_notes`**:
   - `note_id` (Primary Key, Auto-increment)
   - `case_id` (FK $\to$ `investigation_cases.case_id`)
   - `author` (Investigator name)
   - `note_text` (Detailed inquiry comments)
   - `created_at` (ISO8601 UTC timestamp)

3. **`case_events` (Immutable Audit Trail)**:
   - `event_id` (Primary Key, Auto-increment)
   - `case_id` (FK $\to$ `investigation_cases.case_id`)
   - `event_type` (`CASE_CREATED`, `STATUS_CHANGED`, `INVESTIGATOR_ASSIGNED`, `NOTE_ADDED`, `CASE_RESOLVED`, `PRIORITY_CHANGED`)
   - `actor` (User/service that initiated the action)
   - `old_value`, `new_value`, `details`
   - `timestamp` (ISO8601 UTC timestamp)

---

## 2. Investigation Lifecycle & Transition Rules

```
                      ┌───────────────┐
                      │      NEW      │
                      └───────┬───────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       ┌───────────────┐             ┌────────────────┐
       │ UNDER_REVIEW  │◄────────────┤ FALSE_POSITIVE │
       └───────┬───────┘ (re-open)   └────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌───────────────┐  ┌───────────┐
│   ESCALATED   │  │ RESOLVED  │
└───────┬───────┘  └─────▲─────┘
        │                │
        └────────────────┘
```

- **Direct resolution from `NEW` is forbidden**; claims must first be assigned and placed `UNDER_REVIEW`.
- Reopening a resolved or dismissed case transitions it back to `UNDER_REVIEW` for supplementary inquiry.
- Every state mutation writes a permanent record into `case_events`.

---

## 3. Seeded Case Queue Status (from Phase 8 Empirical Scores)

Claims from `data/features/final_risk_scores.csv` crossing the threshold (`risk_band IN ('HIGH', 'CRITICAL')`) were automatically queued:

| Metric | Count | Description |
|---|---|---|
| **Total Cases Queued** | **27** | Exactly matches the 27 HIGH + CRITICAL claims from Phase 8 |
| **CRITICAL Priority** | **1** | Score $\ge 0.75$ |
| **HIGH Priority** | **26** | Score $0.50 \le S < 0.75$ |
| **Initial Status** | **27 NEW** | Ready for investigator assignment |
| **Audit Events Logged** | **27** | `CASE_CREATED` events recorded |

---

## 4. API Service & Endpoints

Implemented in `src/cases/`, `api/services/case_service.py`, and `api/routes/cases.py`:

- `GET /cases`: Filter by `status`, `priority`, `assigned_to`, `min_risk`
- `GET /cases/{case_id}`: Retrieve case metadata
- `POST /cases`: Create new case
- `POST /cases/{case_id}/status`: Transition status with reason and actor
- `POST /cases/{case_id}/assign`: Assign investigator (auto-moves `NEW` to `UNDER_REVIEW`)
- `POST /cases/{case_id}/notes`: Add timestamped investigation notes
- `GET /cases/{case_id}/history`: Chronological events and notes timeline
- `POST /cases/{case_id}/resolve`: Document final findings and close case
- `GET /cases/{case_id}/dossier`: Full evidence dossier (claim, claimant, provider, policy, vehicle, invoice, Phase 8 risk decomposition, notes, history)
- `GET /cases/stats/summary`: Operational workload and queue metrics

---

## 5. Verification & Test Results

- **Phase 9 Unit & Route Tests**: **16 passed in `tests/test_cases.py`**
- **Full Project Test Suite**: **297 passed in 13.09s** (0 failed, 0 errors)
