# Phase 11: Fraud Analytics Dashboard Report

## Executive Summary

Phase 11 implements the **Fraud Analytics Decision Intelligence & Investigation Dashboard** in Streamlit, providing interactive visualization, triage workflows, multi-signal evidence synthesis, and knowledge graph exploration for human-in-the-loop fraud adjusters and SIU investigators.

In strict compliance with the **Global Project Rules**:
- **Zero Hallucinated / Fabricated Numbers:** All dashboard KPIs, distributions, and metrics are calculated live from actual database records (`database/fraud_detection.db`), Phase 8 risk score outputs (`data/features/final_risk_scores.csv`), and verified model experiment metadata (`reports/`, `models/`).
- **Human-in-the-Loop Integrity:** Case operations update triage workflows in SQLite (`investigation_cases`, `case_notes`, `case_events`) with an immutable audit trail, without modifying the underlying synthetic ground-truth dataset (`claims.fraud_label`).
- **Reproducible Pipelines:** All components are fully deterministic and covered by an automated test suite.

---

## 1. Dashboard Architecture & Navigation

The dashboard is structured as a multi-page Streamlit portal (`dashboard/app.py`) with specialized domain pages in `dashboard/pages/`:

```
dashboard/
├── app.py                          # Executive Portal Hub & Architecture Overview
├── utils/
│   ├── data_loader.py              # Cached SQLite, risk scores, graph & report loaders
│   └── filters.py                  # Reusable 8-dimensional sidebar filter component
└── pages/
    ├── overview.py                 # Executive Overview & 6 Primary KPIs
    ├── duplicates.py               # Pairwise Duplicate Claim Similarity Analysis
    ├── network.py                  # Interactive Knowledge Graph Ego-Network Visualizer
    ├── investigation.py            # 360° Claim Investigation Dossier & Case Actions
    ├── cases.py                    # Operational SIU Triage Worklist
    ├── model_performance.py        # Supervised, Anomaly & Graph Empirical Benchmarks
    ├── claims.py                   # Claims Explorer & Full CSV Export
    ├── audit_logs.py               # Immutable State Transition & Activity Logs
    └── monitoring.py               # Pipeline Health & Artifact Integrity Checks
```

---

## 2. Core Requirements & Implementations

### A. Executive Overview & The 6 Required KPIs
Implemented in `dashboard/pages/overview.py`:
1. **Total Claims:** 320 claims (complete dataset)
2. **Flagged Claims:** 27 claims (categorized in `HIGH` or `CRITICAL` risk bands)
3. **High Risk Claims:** 27 claims (Final Composite Risk Score $\ge 0.50$)
4. **Investigation Cases:** 27 active cases (`NEW`, `UNDER_REVIEW`, `ESCALATED`)
5. **Fraud Rate:** 16.25% (exact ground-truth confirmed fraud: 52 / 320)
6. **Average Risk Score:** 0.2998 (mean composite score across all claims)

### B. Multi-Signal Score Distributions
- **Composite Risk Distribution:** Histogram partitioned by operational bands (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) with marginal box plots.
- **Supervised Fraud Probability:** Probability distribution mapped against actual ground truth (0 = Legitimate, 1 = Fraud).
- **Calibrated Anomaly Distribution:** Continuous score distribution $[0.0, 1.0]$ from Isolation Forest + LOF.
- **High-Risk Claims Table:** Multi-signal triage table displaying Claim ID, Claim Amount, Fraud Probability, Anomaly Score, Graph Risk, Final Risk, Risk Band, Claim Status, and Case Status.

### C. Duplicate Claim Analysis
Implemented in `dashboard/pages/duplicates.py`:
- Pairwise similarity score distribution with elevated risk threshold ($0.50$).
- Duplicate detection clusters (Opportunistic, Organized, Recycled).
- Side-by-side attribute matching across invoice amounts, incident dates, and entity identifiers.

### D. Graph Relationship & Network Visualizer
Implemented in `dashboard/pages/network.py`:
- Interactive multi-entity network visualizer built with NetworkX and Plotly.
- Renders:
  $$\text{Claim} \longleftrightarrow \text{Claimant} \longleftrightarrow \text{Policy} \longleftrightarrow \text{Vehicle} \longleftrightarrow \text{Provider} \longleftrightarrow \text{Location}$$
- Multiple layout algorithms: Force-directed Spring layout, Circular layout, Kamada-Kawai layout.
- Node Inspector: Select any node in the rendered subgraph to inspect entity attributes and immediate relational neighbors.
- Provider Hubs table highlighting providers servicing multiple claims to uncover collusion patterns.

### E. 360° Claim Investigation Dossier
Implemented in `dashboard/pages/investigation.py`:
- Comprehensive dossier assembling Claim Facts, Policy terms, Claimant demographics, Vehicle characteristics, Provider details, and Invoice audit (with discrepancy detection).
- Multi-signal risk decomposition horizontal bar chart and explainable risk reason triggers.
- Interactive SIU case actions:
  - Transition status (`NEW`, `UNDER_REVIEW`, `ESCALATED`, `RESOLVED`, `FALSE_POSITIVE`)
  - Assign investigator
  - Record timestamped inquiry notes
  - View full chronological audit trail

### F. Multi-Dimensional Filtering
Implemented in `dashboard/utils/filters.py`:
Supports filtering across:
1. Operational Risk Band (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)
2. Claim Amount Range ($)
3. Incident Date Range
4. Provider Filter
5. Claimant City / Location Filter
6. Fraud Probability Threshold
7. Anomaly Score Threshold
8. Investigation Case Status

---

## 3. Verification & Test Suite

The dashboard was validated using automated tests in `tests/test_dashboard.py`:
- `test_load_all_claims_data_returns_dataframe`: PASSED (verifies 320 unique claims with risk scores)
- `test_compute_executive_kpis_accuracy`: PASSED (verifies all 6 KPIs match ground truth exactly)
- `test_compute_executive_kpis_empty_df`: PASSED (verifies safe zero-handling)
- `test_load_duplicate_records`: PASSED (verifies feature store columns and aliases)
- `test_load_investigation_cases`: PASSED (verifies operational cases loaded)
- `test_build_claim_network_graph_structure`: PASSED (verifies multi-entity topology and relations)
- `test_build_claim_network_graph_nonexistent_claim`: PASSED (verifies graceful fallback)
- `test_load_claim_investigation_dossier_found`: PASSED (verifies full 360° entity assembly)
- `test_load_claim_investigation_dossier_not_found`: PASSED (verifies error handling)
- `test_create_or_update_case_and_audit_log`: PASSED (verifies SQLite case mutations and audit logs)
- `test_load_experiment_reports_contains_real_data`: PASSED (verifies real metrics loaded from `reports/`)

**Full Repository Test Suite Result:**
`329 passed, 1 warning in 20.36s` across all 12 test suites.
