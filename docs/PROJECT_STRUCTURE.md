# FraudShield AI — Project Directory Structure & Organization

This document provides a comprehensive map of the FraudShield AI codebase, detailing the purpose of every top-level directory, key architectural components, and developer navigation workflows.

---

## 1. High-Level Directory Overview

```text
graph_enhanced_build/
├── api/                  # Production FastAPI REST Backend
│   ├── routes/           # REST endpoints (claims, analytics, cases, graph, etc.)
│   ├── schemas/          # Pydantic request/response validation contracts
│   ├── services/         # Business logic layer connecting routes to algorithms
│   ├── db.py             # Dual-engine database adapter (Supabase PG + SQLite fallback)
│   └── main.py           # FastAPI application entrypoint & middleware configuration
│
├── configs/              # System YAML configurations & model thresholds
│   ├── app_config.yaml   # Port, logging, risk score weights, threshold settings
│   └── model_config.yaml # Hyperparameters, feature subsets, graph thresholds
│
├── dashboard/            # Streamlit Fraud Analytics Console
│   ├── app.py            # Streamlit multi-page application entrypoint
│   ├── pages/            # Interactive analytics & investigation views
│   ├── components/       # Reusable Streamlit UI widgets
│   ├── styles/           # CSS customizations & styling
│   └── utils/            # Data formatting and session helpers
│
├── data/                 # Data Assets & Storage
│   ├── raw/              # Ground truth raw CSV datasets
│   ├── relational/       # 3NF relational tables (claimants, policies, providers, etc.)
│   ├── processed/        # Preprocessed, cleaned, and encoded data
│   ├── features/         # Extracted feature matrices & scored claims
│   ├── graph/            # Knowledge graph node and edge CSV tables
│   └── demo/             # Sample claims for quick testing
│
├── database/             # Database Schemas & Migrations
│   ├── migrations/       # Sequential SQL migrations (001 to 004)
│   ├── schema.sql        # Core DDL schema definitions
│   ├── views.sql         # Analytical SQL view definitions
│   ├── indexes.sql       # Performance index definitions
│   ├── seed.py           # Reproducible SQLite seeder
│   └── migrate_to_supabase.py # Production SQLite-to-Supabase migration engine
│
├── deployment/           # Containerization & Web Server Configurations
│   ├── Dockerfile        # Backend container definition
│   ├── Dockerfile.frontend # Multi-stage Nginx frontend container definition
│   ├── docker-compose.yml# Deployment service orchestration
│   └── nginx.conf        # Production reverse proxy configuration
│
├── docs/                 # System, Architecture & Engineering Documentation
│   ├── ARCHITECTURE.md   # System and layered architecture specification
│   ├── CLEANUP_REPORT.md # Refactoring audit & removed dead-code manifest
│   ├── DATA_FLOW.md      # Ingestion-to-scoring dataflow diagrams
│   ├── ER_DIAGRAM.md     # Relational database entity-relationship documentation
│   ├── FILE_INDEX.md     # Master catalog of every production file
│   ├── GRAPH.md          # Heterogeneous graph & collusion ring methodology
│   ├── ML_PIPELINE.md    # Multi-stage ML scoring engine documentation
│   ├── PROJECT_STRUCTURE.md # This guide
│   └── TROUBLESHOOTING.md# Developer setup & runtime troubleshooting guide
│
├── frontend/             # Modern Enterprise React Web Application
│   ├── src/              # React 19 + TypeScript + Tailwind source code
│   │   ├── components/   # UI components (Navbar, Sidebar, Charts, Modals)
│   │   ├── pages/        # Views (Dashboard, Claims, Graph, Cases, Settings)
│   │   ├── services/     # Typed API client services
│   │   └── types/        # TypeScript interfaces for API models
│   ├── package.json      # Node.js dependencies
│   ├── vite.config.ts    # Vite bundler & reverse proxy configuration
│   └── tsconfig.json     # Strict TypeScript configuration
│
├── models/               # Serialized ML Model Artifacts & Weights
│   ├── fraud_model/      # XGBoost supervised classifier & scaler joblibs
│   ├── anomaly_model/    # Isolation Forest unsupervised detector joblibs
│   └── graph_enhanced_model/ # Graph-augmented ensemble model weights
│
├── notebooks/            # Jupyter Exploratory & Research Notebooks
│   ├── 05_baseline_model.ipynb
│   ├── 06_graph_construction.ipynb
│   ├── 07_graph_features.ipynb
│   ├── 08_ml_model.ipynb
│   ├── 09_anomaly_detection.ipynb
│   └── 12_explainability.ipynb
│
├── reports/              # Automated Audit & Data Validation Reports
├── scripts/              # Operational & DevOps CLI Utilities
│   ├── health_check.py   # Diagnostic suite for Python, DB, models, data
│   ├── migrate.py        # Database migration CLI runner
│   ├── seed.py           # Database seeder runner
│   └── validate_data.py  # Comprehensive relational integrity validator
│
├── src/                  # Core Analytical, ML, & Feature Pipeline Engine
│   ├── cases/            # Investigation case creation & audit log tracking
│   ├── data/             # Relational data extraction, cleaning & validation
│   ├── duplicate/        # Fuzzy matching & claim duplication detection
│   ├── explainability/   # SHAP value extraction & human-readable risk reason generation
│   ├── features/         # Feature engineering & matrix merging
│   ├── graph/            # Heterogeneous graph construction & network centrality
│   ├── models/           # XGBoost training, inference & anomaly detection
│   ├── scoring/          # Multi-component composite risk score calculation
│   └── pipeline.py       # Master pipeline orchestrator & claim journey tracer
│
├── tests/                # Automated Pytest Test Suites (380 tests)
│   ├── test_anomaly.py   # Isolation Forest tests
│   ├── test_api.py       # FastAPI REST endpoint tests
│   ├── test_cases.py     # Investigation case management tests
│   ├── test_dashboard.py # Streamlit view tests
│   ├── test_data.py      # Data cleaning & loading tests
│   ├── test_duplicate.py # Duplicate detection tests
│   ├── test_e2e.py       # End-to-end integration tests
│   ├── test_explainability.py # SHAP explainability tests
│   ├── test_features.py  # Feature engineering tests
│   ├── test_graph.py     # Graph construction tests
│   ├── test_graph_features.py # Network metric calculation tests
│   ├── test_model.py     # ML model inference tests
│   ├── test_relational.py# Relational database & FK tests
│   └── test_scoring.py   # Composite scoring & risk band tests
│
├── .env.example          # Template environment variable file
├── docker-compose.yml    # Root-level container orchestration
├── Dockerfile.backend    # Root backend container
├── Dockerfile.frontend   # Root frontend container
├── LICENSE               # MIT License
├── pyproject.toml        # Standardized Python packaging configuration
├── requirements.txt      # Core Python production dependencies
├── run.py                # Python master CLI runner
├── run.bat               # Windows one-click platform launcher
├── setup.bat             # Windows one-click environment installer
├── stop.bat              # Windows one-click service shutdown utility
└── test.bat              # Windows one-click automated verification runner
```

---

## 2. "Where Do I Make Changes?" — Developer Guide

| If you want to... | Look in this directory / file |
| :--- | :--- |
| **Add a new REST API endpoint** | [`api/routes/`](file:///c:/graph_enhanced_build/api/routes/) and register in [`api/main.py`](file:///c:/graph_enhanced_build/api/main.py) |
| **Modify API request / response models** | [`api/schemas/`](file:///c:/graph_enhanced_build/api/schemas/) |
| **Change the composite risk score formula** | [`src/scoring/composite_scorer.py`](file:///c:/graph_enhanced_build/src/scoring/composite_scorer.py) and [`configs/app_config.yaml`](file:///c:/graph_enhanced_build/configs/app_config.yaml) |
| **Tune XGBoost or Isolation Forest parameters** | [`configs/model_config.yaml`](file:///c:/graph_enhanced_build/configs/model_config.yaml) and [`src/models/train.py`](file:///c:/graph_enhanced_build/src/models/train.py) |
| **Add new graph node types or relationship edges** | [`src/graph/build_graph.py`](file:///c:/graph_enhanced_build/src/graph/build_graph.py) |
| **Change graph centrality metrics or collusion ring detection** | [`src/graph/graph_features.py`](file:///c:/graph_enhanced_build/src/graph/graph_features.py) |
| **Adjust fuzzy duplicate detection thresholds** | [`src/duplicate/duplicate_detector.py`](file:///c:/graph_enhanced_build/src/duplicate/duplicate_detector.py) |
| **Modify case management lifecycle or events** | [`src/cases/case_manager.py`](file:///c:/graph_enhanced_build/src/cases/case_manager.py) |
| **Add or update React UI pages** | [`frontend/src/pages/`](file:///c:/graph_enhanced_build/frontend/src/pages/) |
| **Update React UI theme, navigation, or layout** | [`frontend/src/components/`](file:///c:/graph_enhanced_build/frontend/src/components/) and [`frontend/src/App.tsx`](file:///c:/graph_enhanced_build/frontend/src/App.tsx) |
| **Change database schema or add migrations** | [`database/migrations/`](file:///c:/graph_enhanced_build/database/migrations/) and [`database/schema.sql`](file:///c:/graph_enhanced_build/database/schema.sql) |
| **Run diagnostics or health check** | [`scripts/health_check.py`](file:///c:/graph_enhanced_build/scripts/health_check.py) |
