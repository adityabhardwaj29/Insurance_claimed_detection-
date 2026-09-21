# FraudShield AI — Enterprise Insurance Fraud Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-green.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-emerald.svg)](https://supabase.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-orange.svg)](https://xgboost.readthedocs.io/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.0%2B-blueviolet.svg)](https://networkx.org/)
[![Tests Passing](https://img.shields.io/badge/tests-380%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Production-Ready Enterprise Platform**: FraudShield AI is an end-to-end insurance claim processing, multi-signal fraud detection, and Special Investigation Unit (SIU) platform. It provides automated underwriting validation, a guided claim intake wizard, real-time 4-pillar fraud scoring (XGBoost, Isolation Forest, Lexical Duplicate Hashing, Bipartite Graph Syndicates), 360° forensic dossiers with SHAP explanations, investigator case management, and immutable audit logs.

---

## ⚡ 5-Minute One-Click Quick Start (Windows)

The platform includes production-ready one-click scripts for instant Windows setup:

| Script | Purpose | Command |
| :--- | :--- | :--- |
| **`setup.bat`** | Creates virtual environment, installs Python + npm dependencies, creates `.env`, and runs health checks. | Double-click or run `setup.bat` |
| **`run.bat`** | Starts FastAPI (port 8000) & React UI (port 3000), and auto-opens default web browser. | Double-click or run `run.bat` |
| **`test.bat`** | Runs full 380 backend tests, builds frontend TypeScript, and verifies system health. | Run `test.bat` |
| **`stop.bat`** | Safely frees ports 8000, 3000, 5173, and 8501. | Run `stop.bat` |

```cmd
# 1. Setup everything (runs once):
setup.bat

# 2. Launch the full application:
run.bat

# 3. (Optional) Launch with Streamlit Research Console included:
run.bat --with-dashboard
```

---

## 📖 Comprehensive Documentation Library

- **[Project Directory Structure & Guide](docs/PROJECT_STRUCTURE.md)** — Folder map and "Where do I edit X?" guide
- **[System Architecture](docs/ARCHITECTURE.md)** — Layered architecture, API gateway, and hybrid risk engine
- **[Codebase Cleanup & Audit Report](docs/CLEANUP_REPORT.md)** — Full audit manifest of retained vs safely removed files
- **[Master File Catalog](docs/FILE_INDEX.md)** — Exhaustive index of every production file, caller, and criticality
- **[Graph Analytics & Collusion Rings](docs/GRAPH.md)** — Heterogeneous knowledge graph methodology & metrics
- **[Database Schema & Migrations](database/README.md)** — Relational tables, SQLite seeder, and Supabase sync
- **[Troubleshooting & Operations](docs/TROUBLESHOOTING.md)** — Fast solutions for ports, virtualenvs, and Node.js
- **[Machine Learning Pipeline](docs/ML_PIPELINE.md)** — Training, feature engineering, and calibration
- **[Operational SIU Workflow](docs/FRAUD_WORKFLOW.md)** — Investigator triage, case lifecycle, and audit logs
- **[REST API Reference](docs/API.md)** — FastAPI endpoint contracts and schemas
- **[Docker Deployment Guide](docs/DEPLOYMENT.md)** — Multi-stage container instructions

---

## 1. Project Overview

Insurance claim fraud constitutes a multi-billion-dollar challenge globally, imposing severe financial losses on carriers and inflating premium costs for legitimate policyholders. Traditional automated fraud detection workflows rely primarily on isolated tabular heuristics or point-in-time classification models. These methods evaluate each claim as an independent event ($i.i.d.$ assumption), leaving carriers vulnerable to coordinated fraud syndicates, shared repair facility collusion, duplicate opportunistic claims, and novel behavioral anomalies.

The **Graph-Enhanced Insurance Claim Fraud Detection Platform** introduces a holistic, multi-signal architecture that blends:
- Relational schema normalization (SQLite 3NF)
- Lexical duplicate detection (TF-IDF & Cosine Similarity)
- Supervised gradient boosting (XGBoost)
- Unsupervised anomaly detection (Isolation Forest)
- Heterogeneous knowledge graph topology (NetworkX)
- Calibrated hybrid risk scoring and reason code generation
- Multimodal explainability (SHAP TreeExplainer & ego-network evidence)
- Human-in-the-loop investigation case management (SIU lifecycle)

---

## 2. Problem Statement

Modern insurance fraud operates across multiple dimensions that cannot be adequately characterized by a single modeling modality:
1. **Collusion Networks**: Dishonest policyholders frequently collaborate with specific repair shops, medical clinics, or legal intermediaries. Tabular models treating records independently cannot see these shared hubs.
2. **Duplicate Invoicing & Serial Claims**: Opportunistic claimants submit near-identical invoices or alter incident descriptions across policies to extract multiple payouts.
3. **Emerging & Zero-Day Typologies**: Supervised models trained on historical labels fail to detect novel fraud methods that have no precedent in training data.
4. **The Black-Box Dilemma**: Complex statistical models often fail in operational Special Investigation Units (SIU) because investigators cannot justify audits without clear, transparent evidence.

---

## 3. Objectives

The primary research and engineering goals of this platform are:
1. **Relational Integrity**: Construct a 3rd Normal Form relational schema modeling claims, policyholders, policies, vehicles, providers, invoices, and territories with strict foreign key constraints.
2. **Deterministic Duplicate Resolution**: Implement text vectorization and cosine similarity to detect duplicate and near-duplicate claims.
3. **Leakage-Free Predictive Modeling**: Establish a supervised classification pipeline with chronological train/test splitting to eliminate future-data leakage.
4. **Outlier Detection**: Formulate an unsupervised anomaly detector calibrated to identify unusual multivariate deviations.
5. **Graph Topological Enrichment**: Model entities as a heterogeneous graph, deriving degree centrality, clustering coefficients, and fraud neighbor ratios.
6. **Unified Hybrid Risk Scoring**: Synthesize individual signals into a calibrated composite score $[0, 1]$ partitioned into four actionable risk bands.
7. **Transparent Explainability**: Deliver local feature attributions via SHAP alongside subnetwork visual graphs for SIU triage.
8. **Production-Grade Delivery**: Provide a high-performance FastAPI REST service and an interactive Streamlit analytics portal.

---

## 4. Architecture

The system operates across a 9-tier unidirectional pipeline:

```
[SOURCE DATA] -> [3NF NORMALIZATION] -> [FEATURE EXTRACTION & DUPLICATES]
                                                |
                       +------------------------+------------------------+
                       |                                                 |
                       v                                                 v
           [SUPERVISED XGBOOST]                               [KNOWLEDGE GRAPH]
           - Probability P(Fraud)                             - NetworkX Topology
                       |                                      - Fraud Neighbor Ratio
                       +------------------------+------------------------+
                                                |
                                                v
                                    [ANOMALY DETECTION]
                                    - Isolation Forest Outliers
                                                |
                                                v
                                    [HYBRID RISK ENGINE]
                                    - Weighted Aggregation (0.40/0.20/0.15/0.25)
                                    - 4-Tier Risk Bands & Reason Codes
                                                |
                                                v
                                   [SIU CASE MANAGEMENT]
                                   - Investigation Queue in SQLite
                                                |
                                                v
                               [SERVING & PRESENTATION TIER]
                               - FastAPI REST API (Port 8000)
                               - Streamlit Analytics Portal (Port 8501)
```

---

## 5. Dataset Sources

The project utilizes a simulated automotive insurance dataset engineered to model realistic relational patterns:
- **Total Claims**: 320 transactions
- **Total Claimants**: 120 policyholders
- **Total Policies**: 140 underwriting policies
- **Total Vehicles**: 130 insured vehicles
- **Total Providers**: 25 repair shops / service facilities
- **Total Invoices**: 220 billing documents
- **Total Locations**: 60 municipal territories across 5 major urban hubs (Mumbai, Delhi, Pune, Ahmedabad, Surat)

---

## 6. Data Provenance

In compliance with academic research integrity:

| Category | Definition | Repository Location |
| :--- | :--- | :--- |
| **SOURCE DATA** | Raw synthetic flat files representing uncleaned claims. | `data/raw/` |
| **PROCESSED DATA** | Validated, type-cast relational tables normalized in 3NF. | `data/relational/` |
| **DERIVED DATA** | Engineered feature matrices, cosine matrices, and graph metrics. | `data/features/`, `data/graph/` |
| **MODEL OUTPUT** | Machine learning predictions, anomaly scores, and risk classifications. | `models/`, `data/features/final_risk_scores.csv` |

> [!IMPORTANT]
> **Academic Disclosure**: All records are synthetic project-generated research data. They do not represent real policyholder records, nor are they sourced from IBM or proprietary corporate repositories. Ground-truth `fraud_label` prevalence is **16.25%** (52 fraud claims, 268 legitimate claims).

---

## 7. Data Preprocessing

Data normalization follows strict relational rules:
1. **Cleaning**: Explicit type casting (ISO-8601 timestamps, 64-bit floats for financial values).
2. **Referential Integrity**: 100% of foreign keys resolve without orphan records (`PRAGMA foreign_keys = ON;`).
3. **Primary Key Uniqueness**: Confirmed 0 duplicate primary keys across all 7 relational tables.
4. **Preserved Signals**: Shared invoice references across multiple claims are preserved as a legitimate fraud indicator rather than filtered out.

---

## 8. Feature Engineering

Features are computed with strict preservation of temporal causality to eliminate look-ahead bias:
- **Financial Ratios**: `amount_to_premium_ratio`, `invoice_to_claim_ratio`.
- **Temporal Intervals**: `days_since_policy_start` (claims filed shortly post-inception).
- **Causal Frequency Tracking**: `claimant_claim_frequency` and `provider_claim_volume` are computed using `cumcount() + 1` over chronologically sorted claims, ensuring features reflect only past events.

---

## 9. Duplicate Detection

- **Algorithm**: TF-IDF tokenization ($n$-gram range 1 to 2) with cosine similarity.
- **Matrix Calculation**: $320 \times 320$ pairwise similarity matrix with self-match diagonal zeroed.
- **Thresholds**:
  - Similarity $\ge 0.85$: Confirmed Duplicate (`DUPLICATE_CLAIM_DETECTED`).
  - Similarity $\ge 0.50$: Suspected Duplicate (`HIGH_SIMILARITY_MATCH`).
- Persisted Artifact: `data/features/duplicate_features.csv`.

---

## 10. ML Methodology

- **Data Split**: Chronological split (70% train / 30% test). Maximum train date (`2026-06-29`) strictly precedes minimum test date (`2026-07-01`).
- **Preprocessors**: Imputation and scaling encapsulated within a scikit-learn `Pipeline` to prevent test-set contamination.
- **Candidate Models Evaluated**:
  - Logistic Regression (Baseline)
  - Random Forest
  - HistGradientBoosting
  - **XGBoost Classifier (Selected)**: Achieved highest PR-AUC (`0.2348`) on held-out test data with Brier calibration score of `0.1906`.
- Persisted Artifact: `models/fraud_model/model.joblib`.

---

## 11. Anomaly Detection

- **Architecture**: `IsolationForest` configured with `contamination=0.10` and 100 estimators.
- **Features Evaluated**: Multivariate financial and behavioral ratios (`claim_amount`, `amount_to_premium_ratio`, `invoice_to_claim_ratio`, `days_since_policy_start`, `vehicle_age`).
- **Calibration**: Decision function inverted and min-max scaled into $[0, 1]$.
- Persisted Artifact: `models/anomaly_model/isolation_forest.joblib`.

---

## 12. Graph Methodology

- **Topology**: Heterogeneous knowledge graph consisting of 1,020 nodes (7 entity types) and 2,615 edges (10 relationship types).
- **Engine**: NetworkX in-memory graph analyzer.
- **Extracted Structural Features**:
  - Claimant degree centrality and serial filing counts.
  - Provider throughput volume.
  - Fraud-neighbor ratio (percentage of 1-hop/2-hop neighbors with prior fraud flags).
- Persisted Artifacts: `data/graph/nodes.csv`, `data/graph/edges.csv`, `data/features/graph_features.csv`.

---

## 13. Risk Scoring

The hybrid risk engine fuses all four detection streams into a composite score:
$$\text{Final Risk Score} = 0.40 \cdot S_{\text{ML}} + 0.20 \cdot S_{\text{Anomaly}} + 0.15 \cdot S_{\text{Duplicate}} + 0.25 \cdot S_{\text{Graph}}$$

### Operational Risk Bands
| Risk Band | Score Range | Operational Action |
| :--- | :---: | :--- |
| **CRITICAL** | $[0.75, 1.00]$ | Immediate SIU freeze and expedited investigation |
| **HIGH** | $[0.55, 0.75)$ | Queue for standard SIU forensic audit |
| **MEDIUM** | $[0.30, 0.55)$ | Secondary document verification |
| **LOW** | $[0.00, 0.30)$ | Automated STP (Straight-Through Processing) approval |

---

## 14. Explainability

- **SHAP TreeExplainer**: Computes exact Shapley values for XGBoost inferences, breaking down each prediction into top risk-increasing and risk-mitigating factors.
- **Graph Structural Evidence**: Visualizes ego-subnetworks highlighting shared providers, co-claimants, and clustered fraud neighbors.
- **Evidence Synthesis**: Automatically generates narrative explanations combining both feature attributions and topological relationships.

---

## 15. API

Built with **FastAPI** (`api/main.py`), offering 15 REST endpoints with automatic OpenAPI documentation:
- **Documentation**: `http://localhost:8000/docs`
- **Core Endpoints**:
  - `GET /health`: Service health and model readiness probe.
  - `GET /claims`: Dynamic filtering, pagination, and sorting.
  - `GET /claims/{id}/risk`: Multi-signal risk score and reason codes.
  - `GET /claims/{id}/graph`: Subnetwork ego-graph JSON.
  - `GET /claims/{id}/explanation`: SHAP waterfall attributions and narrative.
  - `POST /predict`: Real-time supervised fraud probability inference.
  - `POST /cases`: Full SIU case management CRUD operations.

---

## 16. Dashboard

An interactive multi-page intelligence portal built with **Streamlit** (`dashboard/app.py`):
- **Executive Overview**: High-level KPIs, fraud rate distributions, and claim volume metrics.
- **Fraud Investigation Queue**: Triage claims filtered by risk band with one-click case creation.
- **Knowledge Graph Explorer**: Force-directed subnetwork visualization of claim relationships.
- **Explainability Studio**: SHAP attribution waterfall charts and rule reason breakdown.
- **SIU Case Management**: Interactive case status updater, investigator assignment, and note logging.

---

## 17. Installation

### Prerequisites
- Python 3.10+
- Git

### Setup Steps
```bash
# 1. Clone repository
git clone https://github.com/adityabhardwaj29/Insurance_claimed_detection-.git
cd Insurance_claimed_detection-

# 2. Create virtual environment
python -m venv venv

# Windows activation:
venv\Scripts\activate
# Linux/macOS activation:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 18. Running Instructions

The platform provides a master CLI runner (`run.py`):

```bash
# Launch both FastAPI (port 8000) and Streamlit (port 8501) concurrently
python run.py --all

# Launch FastAPI Backend only
python run.py --api

# Launch Streamlit Dashboard only
python run.py --dashboard

# Run the complete reproducible pipeline from scratch
python run.py --pipeline

# Trace and verify an individual claim journey end-to-end
python run.py --journey CLM00001

# Run the full automated test suite
python run.py --test
```

---

## 19. Testing

The repository contains 15 automated test suites covering all 11 system domains:
```bash
pytest -v
```
- **Test Result**: **373 passed, 0 failures, 0 errors** in 12.40s.
- **Security Penetration Tests**: Validated SQL injection immunity, zero broken foreign keys, zero dangling graph edges, and zero target leakage.

---

## 20. Limitations

1. **Synthetic Nature**: The dataset is simulated; performance metrics benchmark pattern discovery on this specific formulation and should not be cited as real-world production metrics.
2. **In-Memory Graph**: NetworkX operates in-memory; enterprise production deployment requires distributed graph databases (e.g. Neo4j).
3. **Static Scoring Weights**: Hybrid risk engine weights ($0.40, 0.20, 0.15, 0.25$) are static heuristics rather than dynamically optimized per product line.
4. **CORS Development Default**: Defaults to `*` for local development; must be configured to explicit domains in production.

---

## 21. Future Scope

1. **Graph Neural Networks (GNNs)**: Train inductive representation learning architectures (e.g., GraphSAGE or Relational Graph Convolutional Networks) for end-to-end node and edge classification.
2. **Active Learning Feedback Loops**: Continuously retrain supervised models using investigator case resolution determinations.
3. **Streaming Ingestion**: Integrate Apache Kafka / Flink for real-time claim event ingestion and sub-second fraud scoring.
4. **Multimodal LLM Document Parsing**: Incorporate Vision-Language Models (VLMs) to analyze accident damage photos and repair invoice PDFs directly.
