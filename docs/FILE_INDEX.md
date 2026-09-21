# FraudShield AI — Master File Index

This catalog indexes every production file in the repository, explaining its purpose, incoming callers/consumers, and architectural role.

---

## 1. Backend & API (`api/`)

| File Path | Description / Responsibility | Consumers | Criticality |
| :--- | :--- | :--- | :--- |
| [`api/main.py`](file:///c:/graph_enhanced_build/api/main.py) | Application entrypoint, FastAPI instance, CORS, router mounting, exception handlers | Uvicorn, Docker, `run.py` | Critical |
| [`api/db.py`](file:///c:/graph_enhanced_build/api/db.py) | Database connection abstraction for Supabase PostgreSQL & SQLite fallback | All routes and services | Critical |
| [`api/routes/analytics.py`](file:///c:/graph_enhanced_build/api/routes/analytics.py) | Portfolio-level fraud analytics, KPI metrics, risk band distribution | Frontend Dashboard, Streamlit | High |
| [`api/routes/cases.py`](file:///c:/graph_enhanced_build/api/routes/cases.py) | SIU case lifecycle, status transitions, investigator assignment, audit notes | Frontend Case Manager | High |
| [`api/routes/claims.py`](file:///c:/graph_enhanced_build/api/routes/claims.py) | Claim search, detail retrieval, relational entity inspection | Frontend Claims Explorer | High |
| [`api/routes/graph.py`](file:///c:/graph_enhanced_build/api/routes/graph.py) | Subgraph extraction, neighbor lookup, collusion ring network visualization | Frontend Graph Explorer | High |
| [`api/routes/scoring.py`](file:///c:/graph_enhanced_build/api/routes/scoring.py) | Real-time multi-model claim scoring & SHAP feature contribution | Frontend Real-Time Scoring | High |
| [`api/schemas/claim.py`](file:///c:/graph_enhanced_build/api/schemas/claim.py) | Pydantic schema contracts for claim entities, requests, and scoring responses | API routes, Frontend | Medium |
| [`api/services/scoring_service.py`](file:///c:/graph_enhanced_build/api/services/scoring_service.py) | Orchestrates ML, anomaly, duplicate, and graph models for incoming claims | `api/routes/scoring.py` | Critical |
| [`api/services/graph_service.py`](file:///c:/graph_enhanced_build/api/services/graph_service.py) | Extracts subgraphs and Ego networks using NetworkX | `api/routes/graph.py` | High |

---

## 2. Core Analytical & ML Pipeline (`src/`)

| File Path | Description / Responsibility | Consumers | Criticality |
| :--- | :--- | :--- | :--- |
| [`src/pipeline.py`](file:///c:/graph_enhanced_build/src/pipeline.py) | Master pipeline orchestrator & single-claim journey verification | CLI `run.py --pipeline` | Critical |
| [`src/cases/case_manager.py`](file:///c:/graph_enhanced_build/src/cases/case_manager.py) | Case creation, state transitions, investigator notes, immutable audit events | `api/routes/cases.py` | High |
| [`src/data/clean_data.py`](file:///c:/graph_enhanced_build/src/data/clean_data.py) | Missing value imputation, datatype casting, outlier winsorization | `src/pipeline.py` | High |
| [`src/data/load_data.py`](file:///c:/graph_enhanced_build/src/data/load_data.py) | Ground truth CSV loader with validation | `src/pipeline.py` | High |
| [`src/data/relational_builder.py`](file:///c:/graph_enhanced_build/src/data/relational_builder.py) | Normalizes raw denormalized claims into 7 3NF relational tables | Database seeder, Pipeline | High |
| [`src/data/validate_data.py`](file:///c:/graph_enhanced_build/src/data/validate_data.py) | 41 schema, foreign key, and domain range validation checks | Scripts, Tests | High |
| [`src/duplicate/duplicate_detector.py`](file:///c:/graph_enhanced_build/src/duplicate/duplicate_detector.py) | Fuzzy similarity matching across claimant, provider, location, and amounts | Scoring engine | High |
| [`src/explainability/shap_explainer.py`](file:///c:/graph_enhanced_build/src/explainability/shap_explainer.py) | TreeSHAP calculation and human-readable risk reason generation | API, Dashboard | High |
| [`src/features/build_features.py`](file:///c:/graph_enhanced_build/src/features/build_features.py) | Derives behavioral, velocity, ratio, and temporal features | Pipeline | High |
| [`src/features/merge_features.py`](file:///c:/graph_enhanced_build/src/features/merge_features.py) | Merges tabular features with network graph centrality metrics | Pipeline | High |
| [`src/graph/build_graph.py`](file:///c:/graph_enhanced_build/src/graph/build_graph.py) | Constructs heterogeneous bipartite knowledge graph from relational tables | Pipeline, Graph Service | High |
| [`src/graph/graph_features.py`](file:///c:/graph_enhanced_build/src/graph/graph_features.py) | Computes PageRank, Degree, Betweenness, and Collusion Ring metrics | Feature pipeline | High |
| [`src/graph/statistics.py`](file:///c:/graph_enhanced_build/src/graph/statistics.py) | Computes network density, diameter, connected components, and community clusters | Analytics routes | Medium |
| [`src/models/train.py`](file:///c:/graph_enhanced_build/src/models/train.py) | Trains XGBoost classifier with SMOTE and cross-validation | Training pipeline | High |
| [`src/models/evaluate.py`](file:///c:/graph_enhanced_build/src/models/evaluate.py) | Computes PR-AUC, ROC-AUC, F1, and cost-benefit trade-off curves | Model reports | Medium |
| [`src/models/anomaly/anomaly_detector.py`](file:///c:/graph_enhanced_build/src/models/anomaly/anomaly_detector.py) | Unsupervised Isolation Forest outlier detector | Scoring engine | High |
| [`src/scoring/composite_scorer.py`](file:///c:/graph_enhanced_build/src/scoring/composite_scorer.py) | Weighted fusion of ML probability, anomaly score, duplicate score, and graph risk | All scoring APIs | Critical |

---

## 3. Database Layer (`database/`)

| File Path | Description / Responsibility | Consumers | Criticality |
| :--- | :--- | :--- | :--- |
| [`database/schema.sql`](file:///c:/graph_enhanced_build/database/schema.sql) | DDL schema for 7 relational entities, risk scores, and case management | PostgreSQL, SQLite | Critical |
| [`database/views.sql`](file:///c:/graph_enhanced_build/database/views.sql) | Analytical views for high-risk claimants, suspicious providers, and collusion clusters | Supabase, BI tools | Medium |
| [`database/indexes.sql`](file:///c:/graph_enhanced_build/database/indexes.sql) | B-tree performance indexes on foreign keys, dates, and risk scores | Database engines | High |
| [`database/seed.py`](file:///c:/graph_enhanced_build/database/seed.py) | Reproducible database seeder loading 7 CSVs in dependency order | `scripts/seed.py`, `setup.bat` | High |
| [`database/migrate_to_supabase.py`](file:///c:/graph_enhanced_build/database/migrate_to_supabase.py) | Automated transfer engine syncing SQLite to Supabase PostgreSQL | `scripts/migrate.py` | High |

---

## 4. Frontend Application (`frontend/`)

| File Path | Description / Responsibility | Consumers | Criticality |
| :--- | :--- | :--- | :--- |
| [`frontend/src/App.tsx`](file:///c:/graph_enhanced_build/frontend/src/App.tsx) | Client-side routing, navigation layout, theme provider | Browser | Critical |
| [`frontend/src/pages/Dashboard.tsx`](file:///c:/graph_enhanced_build/frontend/src/pages/Dashboard.tsx) | Executive KPI dashboard, risk distribution, recent high-risk claims | End users | High |
| [`frontend/src/pages/Claims.tsx`](file:///c:/graph_enhanced_build/frontend/src/pages/Claims.tsx) | Searchable claim registry with filtering, status tags, and detail view | Investigators | High |
| [`frontend/src/pages/Graph.tsx`](file:///c:/graph_enhanced_build/frontend/src/pages/Graph.tsx) | Interactive network graph visualizer for collusion rings and entity clusters | Fraud Analysts | High |
| [`frontend/src/pages/Cases.tsx`](file:///c:/graph_enhanced_build/frontend/src/pages/Cases.tsx) | SIU case triage, status changes, investigator notes, and event audit trails | SIU Leads | High |
| [`frontend/src/pages/Scoring.tsx`](file:///c:/graph_enhanced_build/frontend/src/pages/Scoring.tsx) | Real-time claim submission and live scoring breakdown with SHAP explanation | Adjusters | High |

---

## 5. Automation & DevOps Root Scripts

| File Path | Description / Responsibility | Target OS | Criticality |
| :--- | :--- | :--- | :--- |
| [`run.bat`](file:///c:/graph_enhanced_build/run.bat) | One-click platform launcher (FastAPI + React UI + auto browser open) | Windows | High |
| [`setup.bat`](file:///c:/graph_enhanced_build/setup.bat) | One-click environment installer (virtualenv, python, npm packages, config) | Windows | High |
| [`stop.bat`](file:///c:/graph_enhanced_build/stop.bat) | One-click clean service shutdown releasing ports 8000, 3000, 5173, 8501 | Windows | High |
| [`test.bat`](file:///c:/graph_enhanced_build/test.bat) | One-click test runner (pytest suite + frontend build + health check) | Windows | High |
| [`run.py`](file:///c:/graph_enhanced_build/run.py) | Cross-platform master CLI runner | Cross-platform | High |
| [`docker-compose.yml`](file:///c:/graph_enhanced_build/docker-compose.yml) | Root container orchestration wiring API, Frontend, and Streamlit | Docker | High |
