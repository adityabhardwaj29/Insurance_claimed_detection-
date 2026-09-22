# 🗺️ Complete Project Directory & Architecture Guide

Welcome to the **Graph-Enhanced Insurance Claim Fraud Detection Platform**.

This guide provides a crystal-clear, beginner-friendly, and professional breakdown of every directory, file, and subsystem in the project. Any developer, reviewer, or hiring manager can look at this guide and immediately understand **where every file is located and why it is used**.

---

## 🏛️ High-Level Project Directory Tree

```text
c:\graph_enhanced_build\
│
├── ⚙️ backend/               # Complete Python Backend & Intelligence Engine
│   ├── main.py              # Direct FastAPI startup script (python backend/main.py)
│   ├── api/                 # Production FastAPI REST Web Layer (Routes, Schemas, Services)
│   ├── src/                 # Multi-signal analytical engine (ML, Anomaly, Graph, Scoring)
│   └── README.md            # In-depth backend architecture guide
│
├── 🖥️ frontend/              # Enterprise React 18 + TypeScript + Vite Web Application
│   ├── src/                 # React components, pages, design system & API client
│   ├── public/              # Static assets, branding logos & favicons
│   ├── package.json         # Node.js dependencies & scripts
│   └── vite.config.ts       # Vite build configuration & proxy settings
│
├── 🗄️ database/              # Relational Database Management Layer
│   ├── fraud_detection.db   # Active SQLite relational database (320 claims)
│   ├── schema.sql           # Complete 3NF DDL schema with primary & foreign keys
│   ├── seed.py              # Database seeding and population pipeline
│   ├── views.sql            # Pre-computed SQL views (fraud overview, provider stats)
│   └── migrations/          # Incremental database migration scripts
│
├── 🧠 models/                # Persisted Machine Learning Model Artifacts
│   ├── xgboost_model/       # Trained XGBoost model binary (model.joblib & metadata.json)
│   ├── anomaly_model/       # Trained Isolation Forest model binary & feature scalers
│   └── README.md            # Model performance cards, PR-AUC, and ROC-AUC metrics
│
├── 📊 dashboard/             # Streamlit SIU Research & Advanced Analytics Console
│   ├── app.py               # Main Streamlit portal entrypoint
│   ├── pages/               # Multi-page analytics (overview, claims, network, etc.)
│   ├── components/          # Reusable UI cards, headers, charts, and metrics
│   ├── styles/theme.css     # Enterprise White & Blue design tokens
│   └── utils/               # Real-time live sync controller & database loaders
│
├── 📁 data/                  # Data Storage & Feature Engineering Tiers
│   ├── raw/                 # Immutable source dataset (synthetic ground-truth claims)
│   ├── relational/          # 3NF normalized tables (claims, claimants, policies, etc.)
│   └── features/            # Precomputed feature matrices, duplicate scores & risk bands
│
├── 🧪 tests/                 # Automated Quality & Test Suite (380 Tests)
│   ├── test_api.py          # FastAPI endpoint integration tests
│   ├── test_model.py        # Supervised ML model accuracy & validation
│   ├── test_anomaly.py      # Isolation Forest anomaly scoring tests
│   ├── test_graph.py        # Knowledge graph topology & collusion tests
│   └── test_scoring.py      # Hybrid multi-signal risk calculation tests
│
├── 📚 docs/                  # In-Depth System Documentation & Architecture Specs
│   ├── architecture.md      # Comprehensive end-to-end multi-signal design doc
│   └── api_reference.md     # Full OpenAPI / Swagger endpoint specification
│
├── 🚀 One-Click Run Scripts
│   ├── run.py               # Master CLI entrypoint (python run.py --platform)
│   ├── run.bat              # Windows double-click platform launcher
│   ├── test.bat             # Automated quality test suite gate (pytest + build)
│   ├── stop.bat             # Windows one-click process termination script
│   └── setup.bat            # One-click environment bootstrap & dependency installer
│
├── Dockerfile.backend       # Docker production container definition for FastAPI
├── Dockerfile.frontend      # Docker production container definition for React
├── docker-compose.yml       # Multi-container orchestration (FastAPI + React + DB)
├── pyproject.toml           # Python package metadata, dependency versions & pytest config
└── README.md                # Primary project overview & quickstart instructions
```

---

## 🔍 Detailed Component Directory Breakdown

### 1. ⚙️ `backend/` — The Brain of the Platform
* **Purpose**: Houses the entire server-side application: HTTP APIs, machine learning inference, graph traversal, and case management.
* **Key Contents**:
  - **`backend/main.py`**: Standalone runner to boot up the FastAPI server on port 8000.
  - **`backend/api/`**:
    - `routes/`: All HTTP endpoints (`claims.py`, `cases.py`, `analytics.py`, `predictions.py`, `audit_logs.py`, `health.py`).
    - `schemas/`: Strict Pydantic models ensuring all incoming and outgoing data is strongly typed and validated.
    - `services/`: Business logic services, including `fraud_pipeline.py` which coordinates the 4 detection signals.
    - `db.py`: Dual-mode database manager (SQLite local fallback + Supabase PostgreSQL ready).
  - **`backend/src/`**:
    - `models/`: Machine learning training code (`train.py`, `evaluate.py`, `anomaly/anomaly_detector.py`).
    - `graph/`: Heterogeneous network graph construction and graph metric computation (`build_graph.py`, `graph_features.py`).
    - `duplicate/`: Pairwise string and fuzzy duplicate claim detector (`duplicate_detector.py`).
    - `scoring/`: The 4-signal hybrid weighted risk calculator (`risk_score.py`, `thresholds.py`).
    - `explainability/`: SHAP tree attribution and network graph subnetwork explainers.

### 2. 🖥️ `frontend/` — Enterprise React Web Application
* **Purpose**: Modern, responsive, enterprise White & Blue single-page application built for Special Investigation Unit (SIU) officers and claims managers.
* **Tech Stack**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Cytoscape.js.
* **Key Contents**:
  - `src/pages/`: Full application screens:
    - `DashboardPage.tsx`: Executive surveillance, KPI ribbon, and risk queues.
    - `ClaimsListPage.tsx`: Relational claims browser with multi-dimensional filtering.
    - `ClaimDossier.tsx`: 360° investigative case file with SHAP charts and entity graph.
    - `NewClaimWizard.tsx`: Multi-step claim intake wizard with automated fraud scoring.
    - `FraudIntelligencePage.tsx`: Interactive full-network graph collusion explorer.
    - `CasesPage.tsx`: SIU case work queue with state transitions (NEW -> UNDER_REVIEW -> RESOLVED).
  - `src/services/api.ts`: Centralized API client connecting to FastAPI on port 8000.

### 3. 🗄️ `database/` — Relational Data & Storage
* **Purpose**: Ground-truth relational database storage following Third Normal Form (3NF).
* **Key Contents**:
  - `fraud_detection.db`: Active SQLite database file storing 320 claims, claimants, policies, vehicles, providers, invoices, and audit logs.
  - `schema.sql`: Full SQL DDL creating all primary keys, foreign key constraints, and indices.
  - `seed.py`: Automated idempotent seeding script that populates the database from CSVs.
  - `views.sql`: Analytical SQL views for fast query aggregation.

### 4. 🧠 `models/` — Persisted ML Artifacts
* **Purpose**: Stores trained model weights, parameters, and serialization artifacts.
* **Key Contents**:
  - `xgboost_model/`: Serialized supervised XGBoost binary (`model.joblib`), label encodings, and feature list.
  - `anomaly_model/`: Serialized unsupervised Isolation Forest binary (`isolation_forest.joblib`) and StandardScaler.
  - `README.md`: Model performance cards, PR-AUC benchmarks, and evaluation reports.

### 5. 📊 `dashboard/` — Streamlit Analytics & Research Console
* **Purpose**: Complementary analytical console tailored for data scientists, risk officers, and academic research.
* **Key Contents**:
  - `app.py`: Main portal entrypoint with multi-page navigation.
  - `pages/`: Dedicated analytics views:
    - `overview.py`: Executive surveillance and risk distributions.
    - `claims.py`: High-speed data explorer.
    - `investigation.py`: Deep-dive SHAP feature attributions and connected graph entities.
    - `network.py`: PyVis interactive physics graph explorer.
    - `model_performance.py`: Model benchmarks (XGBoost vs. Random Forest vs. HistGradientBoosting).
  - `utils/live_sync.py`: Real-time auto-refresh controller syncing live with SQLite and FastAPI.

### 6. 📁 `data/` — Storage Tiers
* **Purpose**: Clean separation of data during each transformation phase.
* **Key Contents**:
  - `raw/`: Unmodified synthetic master dataset (`raw_claims.csv`).
  - `relational/`: Normalized 3NF tables (`claims.csv`, `claimants.csv`, `policies.csv`, `vehicles.csv`, `providers.csv`, `invoices.csv`).
  - `features/`: Engineered matrices (`final_claim_features.csv`, `graph_features.csv`, `anomaly_features.csv`, `final_risk_scores.csv`).

### 7. 🧪 `tests/` — Automated Testing Gates
* **Purpose**: Continuous quality assurance with **380 automated tests**.
* **Key Contents**:
  - `test_api.py`: Tests all REST endpoints, pagination, and error codes.
  - `test_model.py`: Validates model inference bounds and classification metrics.
  - `test_anomaly.py`: Verifies Isolation Forest score calibration and feature independence.
  - `test_graph.py`: Validates graph node/edge integrity, degree metrics, and PageRank.
  - `test_scoring.py`: Tests hybrid weight summation, monotonicity, and risk band classification.
  - `test_security_validation.py`: Security tests for SQL injection prevention and input sanitization.

---

## 🎯 Quick-Lookup Table: "Where Do I Find...?"

| What are you looking for? | Exact File / Directory Path |
| :--- | :--- |
| **FastAPI REST Endpoints** | [`backend/api/routes/`](file:///c:/graph_enhanced_build/api/routes) |
| **FastAPI Main App** | [`backend/main.py`](file:///c:/graph_enhanced_build/backend/main.py) |
| **Supervised XGBoost Training** | [`backend/src/models/train.py`](file:///c:/graph_enhanced_build/src/models/train.py) |
| **Isolation Forest Anomaly Code** | [`backend/src/models/anomaly/anomaly_detector.py`](file:///c:/graph_enhanced_build/src/models/anomaly/anomaly_detector.py) |
| **Knowledge Graph Collusion Code** | [`backend/src/graph/build_graph.py`](file:///c:/graph_enhanced_build/src/graph/build_graph.py) |
| **Multi-Signal Risk Score Engine** | [`backend/src/scoring/risk_score.py`](file:///c:/graph_enhanced_build/src/scoring/risk_score.py) |
| **React UI Pages & Components** | [`frontend/src/pages/`](file:///c:/graph_enhanced_build/frontend/src/pages) |
| **SQLite Database File** | [`database/fraud_detection.db`](file:///c:/graph_enhanced_build/database/fraud_detection.db) |
| **SQL Schema DDL** | [`database/schema.sql`](file:///c:/graph_enhanced_build/database/schema.sql) |
| **Trained Model Weights (`.pkl`)** | [`models/xgboost_model/`](file:///c:/graph_enhanced_build/models/xgboost_model) |
| **Streamlit Research Dashboard** | [`dashboard/app.py`](file:///c:/graph_enhanced_build/dashboard/app.py) |
| **One-Click Startup Script** | [`run.bat`](file:///c:/graph_enhanced_build/run.bat) or [`run.py`](file:///c:/graph_enhanced_build/run.py) |
| **Automated Test Gate** | [`test.bat`](file:///c:/graph_enhanced_build/test.bat) |

---

## 🌐 Network Ports & Service Map

| Service | Port | Local URL | Primary Audience |
| :--- | :---: | :--- | :--- |
| **React Enterprise Web App** | `3000` | `http://localhost:3000` | SIU Investigators, Claims Adjusters |
| **FastAPI REST Backend** | `8000` | `http://localhost:8000/docs` | Developers, External API Clients |
| **Streamlit Research Console** | `8501` | `http://localhost:8501` | Data Scientists, Fraud Analysts |
