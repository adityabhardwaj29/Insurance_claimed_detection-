# PROJECT AUDIT - Graph Enhanced Insurance Claim Fraud Detection

**Audit Date:** 2026-09-16
**Project Root:** c:\graph_enhanced_build
**Status:** Pre-implementation scaffold - NOT a functioning system

---

## 1. Current Architecture

### Intended Pipeline

`
Raw Data -> Cleaning -> Feature Engineering -> Duplicate Detection
         -> ML (Baseline + XGBoost) + Anomaly Detection
         -> Graph Construction + Graph Features
         -> Risk Scoring -> Investigation Cases
         -> FastAPI -> Streamlit Dashboard
`

### Actual State

| Layer | Intended | Actual State |
|---|---|---|
| Raw data | 7 CSV tables | PRESENT and internally consistent |
| Processed data | Cleaned CSVs | IDENTICAL byte-for-byte copies of raw |
| Feature files | Engineered features | Present but NOT derived from src/ code |
| ML models | Trained model artifacts | No saved models exist |
| Graph | NetworkX graph from claims | No persisted graph; builder is a stub |
| API | FastAPI with 6 route groups | All routes are empty stubs |
| Dashboard | 9-page Streamlit app | All pages are 2-line headers only |
| Database | PostgreSQL schema | SQL files only; no connection code |
| Tests | 7 test files | All tests are assert True placeholders |
| Notebooks | 12 Jupyter notebooks | All contain only a single print() cell |

---

## 2. Dataset Inventory

### 2.1 Master Source

| File | Type | Provenance |
|---|---|---|
| data/master/insurance_claim_dataset.xlsx | XLSX 7 sheets | SYNTHETIC - README explicitly states this |

NOTE: README states the dataset is synthetic demo data, not real insurance data.
The fraud_label field is a synthetic ground-truth label.

XLSX sheets: Claims, Claims1 (duplicate of Claims), Policies, Vehicles, Providers, Invoices, Locations.
Claims == Claims1 verified identically.

### 2.2 Raw Data Files (data/raw/)

| File | Rows | Cols | Primary Key | Notes |
|---|---|---|---|---|
| claims_raw.csv | 320 | 12 | claim_id | Contains fraud_label (synthetic) |
| claimants_raw.csv | 120 | 6 | claimant_id | |
| policies_raw.csv | 140 | 6 | policy_id | |
| vehicles_raw.csv | 130 | 6 | vehicle_id | |
| providers_raw.csv | 25 | 5 | provider_id | |
| invoices_raw.csv | 220 | 5 | invoice_id | |
| locations_raw.csv | 60 | 4 | location_id | NOT linked via FK to any table |

Column details:
- claims: claim_id, claimant_id, policy_id, vehicle_id, provider_id, invoice_id, claim_date(str), claim_amount(int), claim_type(str), status(str), fraud_label(int), description(str)
- claimants: claimant_id, name, age(int), city, gender, marital_status
- policies: policy_id, claimant_id, start_date(str), end_date(str), policy_type, premium(int)
- vehicles: vehicle_id, claimant_id, make, vehicle_type, registration_no, model_year(int)
- providers: provider_id, provider_name, city, provider_type, rating(float)
- invoices: invoice_id, provider_id, invoice_amount(int), invoice_date(str), description(str)
- locations: location_id, city, latitude(float), longitude(float)

Categorical values in claims:
- claim_type: Theft, Glass Damage, Fire, Accident, Natural Disaster
- status: Open, Approved, Under Review, Rejected
- fraud_label: 0=268 records (83.75%), 1=52 records (16.25%), fraud rate=16.25%

### 2.3 Processed Data (data/processed/)

FINDING: All 7 processed files are byte-for-byte identical to raw counterparts.
No cleaning transformations have been applied. data/processed/ is a mirror of data/raw/.

### 2.4 Feature Files (data/features/)

WARNING: These files are pre-generated and NOT reproducible via src/ code.
All feature engineering functions in src/features/ are return df.copy() stubs.

| File | Rows | Cols | Claim Coverage | Status |
|---|---|---|---|---|
| claim_features.csv | 320 | 8 | 320/320 | SYNTHETIC - not from code |
| graph_features.csv | 320 | 9 | 320/320 | SYNTHETIC - not from code |
| claimant_features.csv | 120 | 6 | N/A (claimant-level) | SYNTHETIC |
| provider_features.csv | 25 | 6 | N/A (provider-level) | SYNTHETIC |
| duplicate_features.csv | 120 | 9 | 92/320 unique claims | SYNTHETIC - covers only 29% |
| final_ml_dataset.csv | 320 | 13 | 320/320 | SYNTHETIC - merge source unknown |

Feature-derivation validation results (computed against raw data):
- claim_amount: MATCHES raw (320/320)
- claim_age_days: DOES NOT MATCH (0/320) - values are 0-6 but true date range is 0-247 days
- claimant_degree: DOES NOT MATCH (13/320)
- provider_degree: DOES NOT MATCH (15/320)
- claim_frequency: DOES NOT MATCH (41/320)
- previous_rejections: uniform 0-5 distribution (48-64 per value) - statistically implausible

Synthetic generation evidence:
- previous_rejections is perfectly uniform 0-5 - statistically improbable from any derivation
- claim_age_days mean=2.88 days (max=6) vs actual date differences averaging 118 days
- claimant_degree mean=10.27 despite only 120 claimants / 320 claims = avg 2.67 claims/claimant
- community_id ranges 1-30 with uniform sizes 5-19 members
- amount_anomaly_score spans 0.012-0.999 uniformly - not typical IsolationForest output

### 2.5 Synthetic Ground Truth (data/synthetic/)

| File | Rows | Cols | Notes |
|---|---|---|---|
| ground_truth.csv | 320 | 2 | IDENTICAL to claims_raw.fraud_label - redundant |

---

## 3. Data Quality Findings

### 3.1 Missing Values
All 7 raw CSVs: ZERO missing values.
All 6 feature files: ZERO missing values.
NOTE: Zero missing values everywhere is itself a synthetic data signature.

### 3.2 Duplicate Rows
All raw files: 0 duplicate rows.

### 3.3 Data Type Issues
- claim_date (claims): stored as string, never parsed to datetime
- start_date, end_date (policies): stored as string, never parsed
- invoice_date (invoices): stored as string, never parsed
- model_year (vehicles): int64, no range validation

### 3.4 Referential Integrity - ALL INTACT
claims->claimants: 0 orphans
claims->policies: 0 orphans
claims->vehicles: 0 orphans
claims->providers: 0 orphans
claims->invoices: 0 orphans
policies->claimants: 0 orphans
vehicles->claimants: 0 orphans
invoices->providers: 0 orphans

### 3.5 Orphaned Table
locations_raw.csv (60 rows) has no FK in any other table.
Only connection is via city string match - not modelled in schema or code.

### 3.6 Excel Redundancy
- Claims and Claims1 sheets are identical (verified).
- Claimants sheet is missing from XLSX (only exists as CSV).

---

## 4. Entity Mapping

### 4.1 Primary Keys
- Claim: claim_id (e.g. CLM001)
- Claimant: claimant_id (e.g. CLT001)
- Policy: policy_id (e.g. POL001)
- Vehicle: vehicle_id (e.g. VEH001)
- Provider: provider_id (e.g. PRV001)
- Invoice: invoice_id (e.g. INV001)
- Location: location_id (e.g. LOC001)

### 4.2 Foreign Keys
| Table | FK Column | References |
|---|---|---|
| claims | claimant_id | claimants.claimant_id |
| claims | policy_id | policies.policy_id |
| claims | vehicle_id | vehicles.vehicle_id |
| claims | provider_id | providers.provider_id |
| claims | invoice_id | invoices.invoice_id |
| policies | claimant_id | claimants.claimant_id |
| vehicles | claimant_id | claimants.claimant_id |
| invoices | provider_id | providers.provider_id |

### 4.3 Unmodelled Relationships
- Claimant or Provider to Location via city string match (no FK)
- Vehicle to Policy (indirect through claimant_id)

---

## 5. Graph Mapping

### 5.1 Candidate Nodes
| Node Type | Source | Count |
|---|---|---|
| Claim | claims | 320 |
| Claimant | claimants | 120 |
| Policy | policies | 140 |
| Vehicle | vehicles | 130 |
| Provider | providers | 25 |
| Invoice | invoices | 220 |
| Location | locations | 60 (optional, via city) |
Total candidate nodes: ~995

### 5.2 Candidate Edges
| Edge | Direction | Join | Semantics |
|---|---|---|---|
| FILED_BY | Claim->Claimant | claims.claimant_id | Claimant filed claim |
| COVERED_BY | Claim->Policy | claims.policy_id | Claim under policy |
| INVOLVES_VEHICLE | Claim->Vehicle | claims.vehicle_id | Vehicle in claim |
| SERVICED_BY | Claim->Provider | claims.provider_id | Provider handled claim |
| HAS_INVOICE | Claim->Invoice | claims.invoice_id | Invoice for claim |
| HAS_POLICY | Policy->Claimant | policies.claimant_id | Policy owner |
| OWNS_VEHICLE | Vehicle->Claimant | vehicles.claimant_id | Vehicle owner |
| ISSUED_BY | Invoice->Provider | invoices.provider_id | Invoice issuer |

### 5.3 Detectable Fraud Signals via Graph
- Shared provider: high provider node degree
- Ring fraud: claimants in same connected component sharing vehicles/policies
- Provider concentration: high provider betweenness/PageRank
- Serial claimant: high claimant degree
- Invoice reuse: invoice node with degree > 1
- Community clustering: community detection on projected graph

### 5.4 Current Graph Implementation Gap
- graph_builder.py correctly builds heterogeneous NetworkX graph from merged DataFrame
- Does NOT handle locations
- graph_features.py returns {degree: dict, components: list} - NOT a per-claim feature vector
- centrality.py returns only degree_centrality - no betweenness, closeness, PageRank
- No code connects graph_builder -> graph_features -> final_ml_dataset.csv

---

## 6. ML Readiness

### 6.1 Target Variable
- Column: fraud_label
- Type: binary int 0/1
- Distribution: 268 negatives / 52 positives (16.25% fraud rate)
- Class imbalance: ~5:1 - requires class_weight=balanced or SMOTE
- Provenance: SYNTHETIC

### 6.2 Features in final_ml_dataset.csv (11 features)
claim_amount, claim_frequency, claim_age_days, amount_anomaly_score,
claimant_degree, provider_degree, vehicle_degree,
connected_claim_count, shared_entity_count, cluster_size, provider_centrality

Missing from final_ml (in other files but not joined):
- days_since_previous_claim, previous_rejections (claim_features)
- total_claims, avg_claim_amount, max_claim_amount, claims_last_30_days (claimant_features)
- provider_total_claims, provider_avg_amount, suspicious_claim_rate (provider_features)
- duplicate_similarity_score (duplicate_features - only 29% coverage)
- community_id (graph_features - not joined)
- claim_type, policy_type, vehicle_type, provider_type - NO categoricals encoded anywhere

### 6.3 Model Status
| Model | File | Structurally OK | Pipeline Wired |
|---|---|---|---|
| LogisticRegression | src/models/baseline.py | YES | NO |
| XGBoost | src/models/xgboost_model.py | YES | NO |
| IsolationForest | src/models/anomaly.py | YES | NO |
| train() | src/models/train.py | Trivial .fit() wrapper | N/A |
| predict() | src/models/predict.py | Trivial .predict() wrapper | N/A |
| evaluate() | src/models/evaluate.py | Correct sklearn metrics | NO saved output |

No end-to-end training pipeline exists. No saved model .pkl files.

### 6.4 Risk Scoring Problem
Current formula: risk_score = mean(ml_probability, anomaly_score, duplicate_score, graph_risk)
PROBLEM: IsolationForest anomaly_score range is [-1, +1] (negative = anomaly).
Averaging with probabilities [0,1] is mathematically incorrect.
No calibration, no normalisation, no documented weights.

---

## 7. API Readiness

### 7.1 Route Status
| File | Prefix | Endpoints | Status |
|---|---|---|---|
| analytics.py | /analytics | 0 | Empty router |
| cases.py | /cases | 0 | Empty router |
| claims.py | /claims | 0 | Empty router |
| duplicates.py | /duplicates | 0 | Empty router |
| network.py | /network | 0 | Empty router |
| predictions.py | /predict | 0 | Empty router |

Only working endpoint: GET /health returns {status: ok}.
None of the 6 routers are registered in api/main.py.

### 7.2 Service Problems
| Service | Returns | Problem |
|---|---|---|
| claim_service.get_claim() | {claim_id: id} | No DB lookup |
| prediction_service.predict_claim() | {risk_score: 0.0} | HARDCODED ZERO |
| graph_service.get_network() | {nodes: [], edges: []} | Always empty |
| case_service.create_case() | {status: OPEN} | No persistence |

### 7.3 Schema Gaps
- ClaimRequest: only claim_id (no feature input fields)
- PredictionResponse: missing fraud_probability, component_scores, explanation
- CaseResponse: missing priority, risk_score, investigation_signals

---

## 8. Dashboard Readiness

All 9 pages (overview, claims, network, model_performance, cases, duplicates, investigation, monitoring, audit_logs):
- Contain ONLY: import streamlit as st / st.header( ...)
- No data, no charts, no KPIs, no filters

dashboard/app.py renders only a title and st.info() message.
Pages are NOT registered with Streamlit multi-page navigation.

---

## 9. Problems Found

### 9.1 Critical Problems (Blockers)
| ID | Problem | Location | Impact |
|---|---|---|---|
| C1 | Feature files pre-generated, NOT reproducible from code | data/features/, src/features/ | Violates academic reproducibility |
| C2 | claim_age_days fabricated (range 0-6; true date range 0-247 days) | data/features/claim_features.csv | Incorrect feature |
| C3 | All API routes have ZERO registered endpoints | api/routes/*.py, api/main.py | API non-functional |
| C4 | prediction_service hardcodes risk_score=0.0 | api/services/prediction_service.py | All predictions fake |
| C5 | No trained model artifacts exist anywhere | src/models/ | Cannot score any claim |
| C6 | All 12 notebooks are empty scaffolds | notebooks/*.ipynb | No documented experiments |
| C7 | All 7 test files are assert True | tests/*.py | Zero test coverage |
| C8 | Risk score averages incompatible scales (probability [0,1] + IF [-1,+1]) | src/scoring/risk_score.py | Formula incorrect |

### 9.2 Major Problems
| ID | Problem | Location |
|---|---|---|
| M1 | data/processed/ identical to data/raw/ - no cleaning applied | src/data/cleaning.py |
| M2 | All feature engineering functions return df.copy() | src/features/*.py |
| M3 | graph_features.py does NOT produce per-claim feature vector | src/graph/ |
| M4 | locations_raw.csv orphaned - no FK to any table | schema |
| M5 | duplicate_features.csv covers only 29% of claims (92/320) | data/features/ |
| M6 | No routers registered in api/main.py | api/main.py |
| M7 | Dashboard pages not in Streamlit multi-page setup | dashboard/app.py |
| M8 | No database connection code exists anywhere | entire codebase |
| M9 | Claims1 sheet in XLSX is duplicate of Claims | data/master/ |

### 9.3 Minor Problems
| ID | Problem | Location |
|---|---|---|
| m1 | Date columns stored as strings, never parsed | claims_raw, policies_raw, invoices_raw |
| m2 | ground_truth.csv 100% redundant with claims_raw.fraud_label | data/synthetic/ |
| m3 | centrality.py only computes degree_centrality | src/graph/centrality.py |
| m4 | communities.py applied to full heterogeneous graph | src/graph/communities.py |
| m5 | configs/logging.yaml not loaded anywhere | configs/ |
| m6 | run.py only prints a string | run.py |
| m7 | .env.example references PostgreSQL but no connection code | .env.example |
| m8 | deployment/nginx.conf is a single comment | deployment/ |
| m9 | reports/README.md is a placeholder | reports/ |
| m10 | dashboard/assets/ is empty | dashboard/assets/ |
| m11 | previous_rejections uniform 0-5 - statistically implausible | data/features/claim_features.csv |
| m12 | src/utils/config.py only defines ROOT - YAML never loaded | src/utils/config.py |

---

## 10. Recommended Implementation Order

### Phase 1 - Data Foundation (START HERE)
Goal: Reproducible, validated datasets from synthetic master source.
1. Extend src/data/loader.py to load all 7 tables
2. Implement src/data/cleaning.py: parse dates, normalise strings, validate ranges
3. Implement src/data/validation.py: FK integrity, date range, label distribution checks
4. Run pipeline, save verified CSVs to data/processed/
5. Populate Notebooks 01 and 02 with real EDA and cleaning analysis

### Phase 2 - Feature Engineering
Goal: Reproducible features from data/processed/ via src/features/.
1. src/features/claim_features.py: claim_age_days from actual dates, claim_frequency from groupby
2. src/features/claimant_features.py: total_claims, avg_claim_amount, claims_last_N_days
3. src/features/provider_features.py: provider_total_claims, unique_customers
4. src/features/duplicate_features.py: numeric + text similarity between claim pairs
5. src/features/feature_pipeline.py: full merge producing final_ml_dataset.csv
6. Populate Notebooks 03, 04, 05

### Phase 3 - Graph Construction and Features
Goal: Reproducible NetworkX graph + per-claim graph feature vectors.
1. src/graph/graph_builder.py: extend to all node types with attributes
2. src/graph/centrality.py: add betweenness centrality and PageRank
3. src/graph/communities.py: community detection on claim-projected subgraph
4. src/graph/graph_features.py: produce per-claim DataFrame
5. Integrate graph features into feature_pipeline.py
6. Populate Notebooks 08, 09

### Phase 4 - ML Training and Evaluation
Goal: Trained persisted model artifacts with real metrics.
1. Wire src/data/preprocessing.py to actual feature columns
2. Implement src/models/train.py: load -> preprocess -> train -> save .pkl
3. Train LogisticRegression (baseline) and XGBoost
4. Fit IsolationForest, normalise output to [0,1]
5. Save metrics (ROC-AUC, F1, PR-AUC) to reports/
6. Fix src/scoring/risk_score.py: normalise all components, document weights
7. Populate Notebooks 06, 07, 10, 11, 12

### Phase 5 - Database Layer
Goal: Functional SQLite/PostgreSQL backend.
1. Extend database/schema.sql: add cases, audit_logs, predictions tables
2. Implement database/seed.sql: load from data/processed/
3. Create src/utils/db.py: SQLAlchemy engine + session factory
4. Extend database/indexes.sql and database/views.sql

### Phase 6 - API Implementation
Goal: Working FastAPI endpoints backed by real data and model.
1. Register all 6 routers in api/main.py
2. Implement all endpoints in api/routes/*.py
3. Implement real DB lookups in api/services/*.py
4. Expand schemas in api/schemas/*.py

### Phase 7 - Dashboard
Goal: Functional 9-page Streamlit dashboard from real data.
1. Implement multi-page navigation in dashboard/app.py
2. Implement all 9 dashboard pages with charts, KPIs, tables, filters

### Phase 8 - Tests and Documentation
Goal: Verified test coverage and complete academic documentation.
1. Implement all 7 test files (data, features, graph, model, scoring, API, duplicate)
2. Rewrite all stub docs in docs/ with real content

---

## Appendix A - Audit Summary

This project is a well-structured scaffold with NO functioning implementation.
Architecture, SQL schema, route structure, page structure all reflect a coherent design.

BUT:
- No trained models exist
- No reproducible feature engineering pipeline exists
- Pre-generated feature files do NOT match raw data derivations
- All API routes return stubs or hardcoded zeros
- All dashboard pages are empty headers
- All tests are assert True
- All notebooks contain only print('scaffold ready')

The synthetic dataset is internally consistent (zero nulls, zero FK orphans, correct schema).
It is suitable as a development base IF consistently documented as synthetic.

---

## Appendix B - Critical Problems

| ID | Problem | Files |
|---|---|---|
| C1 | Feature files pre-generated, not reproducible | data/features/, src/features/*.py |
| C2 | claim_age_days fabricated (0-6 days vs true 0-247 days) | data/features/claim_features.csv |
| C3 | Zero API endpoints functional | api/routes/*.py, api/main.py |
| C4 | prediction_service hardcodes risk_score=0.0 | api/services/prediction_service.py |
| C5 | No model artifacts exist | src/models/ |
| C6 | All 12 notebooks are empty scaffolds | notebooks/*.ipynb |
| C7 | All 7 test files are assert True | tests/*.py |
| C8 | Risk score averages incompatible scales | src/scoring/risk_score.py |

---

## Appendix C - Recommended Next Phase

BEGIN PHASE 1: Data Foundation.

Every subsequent phase depends on trustworthy, reproducible data.
Phase 1 deliverables:
- data/processed/*.csv with parsed dates, validated FKs, documented transformations
- Working src/data/cleaning.py and src/data/validation.py
- Notebook 01_data_understanding.ipynb with real EDA outputs
- Notebook 02_data_cleaning.ipynb with documented cleaning decisions

---

## Appendix D - Exact Files Requiring Modification

Must Modify (Broken or Placeholder):
- src/data/cleaning.py: implement date parsing, normalisation, validation
- src/data/validation.py: add FK checks, date range, label distribution
- src/features/claim_features.py: implement claim-level calculations
- src/features/claimant_features.py: implement aggregations
- src/features/provider_features.py: implement aggregations
- src/features/duplicate_features.py: implement similarity calculations
- src/features/feature_pipeline.py: implement full merge
- src/graph/graph_features.py: produce per-claim DataFrame
- src/graph/centrality.py: add betweenness, PageRank
- src/scoring/risk_score.py: fix formula, normalise components
- src/models/train.py: full pipeline load->preprocess->train->save
- src/utils/config.py: load YAML configs
- api/main.py: register all 6 routers
- api/routes/claims.py, predictions.py, network.py, duplicates.py, cases.py, analytics.py: implement endpoints
- api/services/prediction_service.py: implement real inference (not hardcoded 0.0)
- api/services/claim_service.py: implement DB lookup
- api/services/graph_service.py: implement subgraph extraction
- api/services/case_service.py: implement DB persistence
- api/schemas/prediction_schema.py: add fraud_probability, component_scores, explanation
- api/schemas/claim_schema.py: add full claim fields
- api/schemas/case_schema.py: add priority, risk_score, signals
- dashboard/app.py: implement multi-page navigation
- dashboard/pages/*.py: implement all 9 pages
- run.py: implement real entry point
- tests/test_*.py: implement real tests (all 7 files)
- notebooks/*.ipynb: implement all 12 notebooks

Must Create (Missing):
- src/utils/db.py: SQLAlchemy connection + session factory
- models/ directory: saved .pkl model artifacts
- src/models/pipeline.py: end-to-end training script
- reports/metrics/ directory: saved evaluation metric JSON files

Must Validate (Suspicious Pre-Generated Content):
- data/features/claim_features.csv: claim_age_days wrong, previous_rejections uniform
- data/features/graph_features.csv: degree values do not match derivations
- data/features/duplicate_features.csv: only 29% claim coverage, method unknown
- data/features/final_ml_dataset.csv: merge provenance unknown, missing features

---

End of Audit
