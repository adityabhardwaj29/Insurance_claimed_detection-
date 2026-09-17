# System Architecture

## 1. Overview

The **Graph-Enhanced Insurance Claim Fraud Detection Platform** is an end-to-end, multi-signal research framework designed to detect fraudulent insurance claims through the synergistic combination of:
1. **Relational Database Management** (SQLite in 3rd Normal Form)
2. **Deterministic Duplicate Detection** (TF-IDF & Cosine Similarity)
3. **Supervised Machine Learning** (XGBoost, Random Forest, HistGradientBoosting, Logistic Regression)
4. **Unsupervised Anomaly Detection** (Isolation Forest + Local Outlier Factor ensemble)
5. **Heterogeneous Knowledge Graph Analysis** (NetworkX bipartite projections, degree centrality, fraud-neighbor clustering)
6. **Multi-Signal Hybrid Risk Engine** (Calibrated weighted aggregation and 4-tier risk bands)
7. **Explainable AI (XAI)** (SHAP TreeExplainer feature attributions synthesized with graph structural evidence)
8. **Human-in-the-Loop Case Management** (Audited investigation lifecycle without automated ground-truth mutation)
9. **Production Serving & Visualization** (FastAPI REST backend and Streamlit intelligence dashboard)

---

## 2. Tiered Architectural Model

```
+---------------------------------------------------------------------------------------------------+
|                                   PRESENTATION & INTERFACE TIER                                   |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |   Streamlit Analytics Portal       |             |   FastAPI Production Backend           |   |
|   |   (Port 8501)                      |             |   (Port 8000 /docs, /redoc)            |   |
|   |   - Executive Overview KPIs        | <---------> |   - 15 REST Endpoints                  |   |
|   |   - Fraud Investigation Queue      |   HTTP/REST |   - Pydantic v2 Schema Validation      |   |
|   |   - Knowledge Graph Subnetwork     |             |   - Structured Request Timing Logger   |   |
|   |   - Explainability & SHAP Waterfall|             |   - CORS & Exception Handlers          |   |
|   +------------------------------------+             +----------------------------------------+   |
+---------------------------------------------------------------------------------------------------+
                                                  ^
                                                  |
+---------------------------------------------------------------------------------------------------+
|                                    APPLICATION & INFERENCE TIER                                   |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |   Hybrid Risk Engine               |             |   Explainability Engine                |   |
|   |   (src/scoring/risk_calculator.py) |             |   (src/explainability/explainer.py)    |   |
|   |   - Multi-signal calibration       |             |   - SHAP TreeExplainer                 |   |
|   |   - Rule catalog & reason codes    |             |   - Graph Evidence Subnetworks         |   |
|   |   - 4-tier risk band assignments   |             |   - Evidence Synthesis Narrative       |   |
|   +------------------------------------+             +----------------------------------------+   |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |   Supervised ML Inference          |             |   Unsupervised Anomaly Detection       |   |
|   |   (models/fraud_model/model.joblib)|             |   (models/anomaly_model/iforest.joblib)|   |
|   |   - ColumnTransformer Preprocessing|             |   - Behavioral Outlier Scoring         |   |
|   |   - XGBoost Classifier (P(Fraud))  |             |   - Contamination Calibration          |   |
|   +------------------------------------+             +----------------------------------------+   |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |   Duplicate Detection Engine       |             |   Case Management Engine               |   |
|   |   (src/duplicate/similarity.py)    |             |   (src/cases/case_manager.py)          |   |
|   |   - TF-IDF Vectorizer & Cosine Sim |             |   - SIU Investigation Queue            |   |
|   |   - Cluster & Pair Matching        |             |   - Audited Status Transitions         |   |
|   +------------------------------------+             +----------------------------------------+   |
+---------------------------------------------------------------------------------------------------+
                                                  ^
                                                  |
+---------------------------------------------------------------------------------------------------+
|                                      DATA & GRAPH ENGINE TIER                                     |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |   Relational Database (SQLite)     |             |   Heterogeneous Knowledge Graph        |   |
|   |   (database/fraud_detection.db)    |             |   (data/graph/nodes.csv, edges.csv)    |   |
|   |   - 7 Tables: claims, claimants,   |             |   - 765 Nodes: Claim, Claimant,        |   |
|   |     policies, vehicles, providers, |             |     Provider, Policy, Vehicle, etc.    |   |
|   |     invoices, locations            |             |   - 1,770 Edges: 10 Relationships      |   |
|   |   - 3 SQL Analytical Views         |             |   - NetworkX Graph Topology            |   |
|   |   - 3 Case Management Tables       |             |   - Degree, Centrality & Fraud Neighbor|   |
|   +------------------------------------+             +----------------------------------------+   |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Subsystem Breakdown

### 3.1. Ingestion and Normalization Tier
- **Input**: Raw flat/simulated CSV tables.
- **Normalization**: Cleaned, validated, and normalized into 3NF SQLite database tables with strict foreign key constraints (`PRAGMA foreign_keys = ON`).
- **Data Provenance**: Strict partition between source data (`data/raw`), normalized data (`data/relational`), and relational database (`database/fraud_detection.db`).

### 3.2. Feature Engineering & Signal Extraction
- **Tabular Features**: Derived chronological features without look-ahead bias (cumulative frequency counts using `cumcount() + 1`).
- **Text & Financial Similarity**: Claim descriptions tokenized and vectorised with TF-IDF for duplicate detection.
- **Network Topology**: Heterogeneous graph loaded into NetworkX; nodes and relationships projected to calculate local density, degree centrality, shared provider volume, and fraud neighbor ratios.

### 3.3. Multi-Signal Hybrid Scoring Engine
- Computes normalized individual signals $S \in [0, 1]$:
  $$\text{Final Risk Score} = 0.40 \cdot S_{\text{ML}} + 0.20 \cdot S_{\text{Anomaly}} + 0.15 \cdot S_{\text{Duplicate}} + 0.25 \cdot S_{\text{Graph}}$$
- Maps composite score to operational bands:
  - **LOW**: $[0.00, 0.30)$
  - **MEDIUM**: $[0.30, 0.55)$
  - **HIGH**: $[0.55, 0.75)$
  - **CRITICAL**: $[0.75, 1.00]$
- Evaluates rule catalog to generate deterministic, human-readable reason codes.

### 3.4. Human-in-the-Loop Case Management (SIU)
- Claims in HIGH or CRITICAL bands trigger automatic case creation in SQLite.
- SIU investigators can review dossiers, assign investigators, add timestamped notes, and update statuses (`NEW` $\rightarrow$ `UNDER_REVIEW` $\rightarrow$ `ESCALATED` $\rightarrow$ `RESOLVED` / `FALSE_POSITIVE`).
- **Global Academic Constraint**: Ground-truth fraud label (`claims.fraud_label`) is strictly immutable; investigator decisions are recorded exclusively in `investigation_cases.resolution`.

### 3.5. Serving and Presentation
- **FastAPI**: Asynchronous REST service exposing 15 endpoints for CRUD operations, batch predictions, subnetwork retrieval, and real-time claim scoring.
- **Streamlit**: Multi-page portal offering real-time KPI aggregations, interactive subnetwork rendering, SHAP waterfall plots, and live case review tools.

---

## 4. Communication and Data Contracts

| Boundary | Protocol / Interface | Data Format | Contract / Schema |
| :--- | :--- | :--- | :--- |
| Database $\leftrightarrow$ Services | SQLite Python Driver (`sqlite3`) | SQL Rows / Tuples | `database/schema.sql` |
| Pipeline $\leftrightarrow$ Filesystem | Joblib & Pandas IO | Binary `.joblib`, CSV | Preprocessing Pipeline & Feature Schemas |
| API $\leftrightarrow$ Clients | HTTP / 1.1 | JSON | Pydantic Schemas (`api/schemas/*.py`) |
| Dashboard $\leftrightarrow$ API / DB | Direct SQLite & HTTP REST | DataFrames & JSON | Typed dictionaries & Pydantic response models |
