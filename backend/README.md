# FraudShield AI — Backend Architecture & Intelligence Engine

Welcome to the **Backend & Intelligence Engine** of the Graph-Enhanced Insurance Claim Fraud Detection Platform.

This directory serves as the centralized home for all Python-based server-side operations, REST API routing, machine learning inference, unsupervised anomaly scoring, heterogeneous knowledge graph construction, and multi-signal risk calculation.

---

## 🏛️ Architecture Overview

The backend is composed of two primary sub-systems working in unison:

```text
backend/
├── main.py                    # Direct FastAPI entrypoint (python backend/main.py)
├── README.md                  # This architecture guide
│
├── api/                       # Production FastAPI REST Web Layer
│   ├── routes/                # HTTP Endpoint handlers
│   │   ├── claims.py          # Claim query, risk analysis, subnetwork, duplicate endpoints
│   │   ├── cases.py           # SIU investigation case lifecycle & state transitions
│   │   ├── analytics.py       # Executive overview metrics & KPI endpoints
│   │   ├── predictions.py     # Live ML & Anomaly scoring on-demand
│   │   ├── customers.py       # Claimant demographic & history management
│   │   ├── policies.py        # Insurance policy registry & premium lookups
│   │   ├── providers.py       # Repair shops & healthcare provider networks
│   │   ├── audit_logs.py      # Immutable regulatory audit trails
│   │   └── health.py          # System diagnostic & dependency health probes
│   ├── schemas/               # Strict Pydantic v2 request/response validation contracts
│   ├── services/              # Business logic services (fraud_pipeline, claim_service, etc.)
│   ├── db.py                  # Dual SQLite & Supabase PostgreSQL connection layer
│   └── main.py                # Underlying FastAPI app configuration & CORS
│
└── src/                       # Core Analytical & Machine Learning Engine
    ├── data/                  # 3NF relational data cleaning & SQLite ingestion
    ├── features/              # Feature engineering & temporal causality pipelines
    ├── models/                # Supervised ML training (XGBoost, Random Forest) & Anomaly (Isolation Forest)
    ├── graph/                 # Heterogeneous insurance knowledge graph (NetworkX)
    ├── duplicate/             # Fuzzy text similarity & attribute recycling detector
    ├── scoring/               # Multi-signal hybrid risk calculator & thresholds
    ├── explainability/        # Tree SHAP feature attribution & graph subnetwork explainers
    ├── cases/                 # Case state machine (NEW -> UNDER_REVIEW -> RESOLVED)
    └── pipeline.py            # Automated end-to-end analytical pipeline orchestrator
```

---

## 🚀 How to Run the Backend

### Option 1: Direct Backend Runner (FastAPI only)
```bash
# From workspace root:
python backend/main.py
```

### Option 2: Using the Global CLI Runner
```bash
python run.py --api
```

### Option 3: Using Uvicorn Directly
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 API Endpoints Summary

Once started, the interactive OpenAPI documentation is live at **`http://localhost:8000/docs`** (Swagger UI) and **`http://localhost:8000/redoc`** (ReDoc).

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Comprehensive health check (DB, models, memory) |
| `GET` | `/api/claims` | Paginated, filtered, and sorted insurance claims |
| `GET` | `/api/claims/{id}` | Complete relational claim dossier |
| `POST` | `/api/claims` | Submit a new claim for automated fraud evaluation |
| `POST` | `/api/claims/{id}/analyze` | Execute the 4-signal multi-layer fraud pipeline |
| `GET` | `/api/claims/{id}/risk` | 4-signal risk breakdown & operational risk band |
| `GET` | `/api/claims/{id}/graph` | Ego subnetwork showing collusion and linked entities |
| `GET` | `/api/claims/{id}/explanation` | SHAP feature attributions and root-cause reasons |
| `GET` | `/api/cases` | Active SIU investigation work queue |
| `PATCH` | `/api/cases/{id}` | Update case status, assign investigator, add audit notes |
| `GET` | `/api/dashboard/summary` | Executive high-level KPI ribbon and risk distributions |

---

## 🧠 The 4 Multi-Signal Fraud Detection Engines

The backend calculates a calibrated composite risk score `[0.00, 1.00]` using four independent analytical signals:

1. **Supervised ML Classification (45% Weight)**:
   - Evaluates XGBoost and Random Forest ensembles trained on temporal, behavioral, and claim attributes.
   - Outputs: `fraud_probability` $\in [0, 1]$.
2. **Unsupervised Anomaly Detection (25% Weight)**:
   - Uses an **Isolation Forest** to isolate multivariate financial outliers without needing historical labels.
   - Flags abnormal claim-to-premium ratios and sudden post-policy filings.
   - Outputs: `anomaly_score` $\in [0, 1]$.
3. **Duplicate & Recycled Attribute Detection (15% Weight)**:
   - Combines Levenshtein string distances, Jaccard token similarities, and numeric proximity.
   - Flags recycled garage/hospital invoices and identity cloning.
   - Outputs: `duplicate_score` $\in [0, 1]$.
4. **Knowledge Graph Collusion & Ring Detection (15% Weight)**:
   - Constructs a heterogeneous graph linking Claimants, Policies, Claims, Providers, Vehicles, and Invoices.
   - Computes Degree Centrality, PageRank, and Fraud Neighbor Proximity.
   - Flags suspicious provider concentrations and multi-party syndicates.
   - Outputs: `graph_risk_score` $\in [0, 1]$.

---

## 🧪 Testing the Backend

To execute the complete 380 automated backend tests:
```bash
# Windows
test.bat

# Or direct pytest:
pytest tests/ -v
```
