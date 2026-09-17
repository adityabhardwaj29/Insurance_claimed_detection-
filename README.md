# Graph-Enhanced Insurance Claim Fraud Detection

> **Academic Research & Decision Intelligence Platform**  
> Multimodal synthesis of **Supervised Machine Learning (XGBoost)**, **Unsupervised Anomaly Detection (Isolation Forest + LOF)**, **Heterogeneous Knowledge Graphs (NetworkX)**, **Explainable AI (TreeSHAP)**, and **Human-in-the-Loop Case Management**.

---

## ⚖️ Academic Integrity & Ethical Data Statement

1. **Synthetic Data Provenance:** The dataset utilized in this project is explicitly synthetic and derived for academic research, algorithm evaluation, and decision intelligence prototyping. It does not represent real-world confidential policyholder records.
2. **Deterministic & Evidence-Based:** Zero random numbers, simulated metrics, or fabricated KPIs are utilized in model evaluations, API endpoints, or the Streamlit dashboard.
3. **Human-in-the-Loop Safeguard:** High-risk claims entering the Special Investigation Unit (SIU) triage workflow are **never** automatically declared fraudulent. Final adjudication requires explicit human investigator review and documentation.

---

## 🏗️ End-to-End System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                 1. RELATIONAL DATA CORE (Phases 1 & 2)                            |
|     [Claimants] <---> [Policies] <---> [Claims] <---> [Invoices] <---> [Providers / Vehicles]    |
+---------------------------------------------------------------------------------------------------+
                                                  |
        +-----------------------------------------+-----------------------------------------+
        |                                         |                                         |
        v                                         v                                         v
+-------------------+                     +-------------------+                     +-------------------+
| Phase 3: Duplicate|                     | Phase 4: XGBoost  |                     | Phase 5: Isolation|
| Detection Engine  |                     | Supervised Model  |                     | Forest + LOF      |
+-------------------+                     +-------------------+                     +-------------------+
        |                                         |                                         |
        +-----------------------------------------+-----------------------------------------+
                                                  |
                                                  v
                                  +-------------------------------+
                                  | Phases 6 & 7: Knowledge Graph |
                                  | 1,020 Nodes, 2,615 Edges      |
                                  +-------------------------------+
                                                  |
                                                  v
                                  +-------------------------------+
                                  | Phase 8: Hybrid Risk Engine   |
                                  | Calibrated Multi-Signal Score |
                                  +-------------------------------+
                                                  |
                                                  v
                                  +-------------------------------+
                                  | Phase 9 & 10: Case Management |
                                  | & Production FastAPI Backend  |
                                  +-------------------------------+
                                                  |
                                                  v
                                  +-------------------------------+
                                  | Phase 11 & 12: Streamlit Hub  |
                                  | & SHAP + Graph Explainability |
                                  +-------------------------------+
                                                  |
                                                  v
                                  +===============================+
                                  | PHASE 13: FULL INTEGRATION    |
                                  | (run.py one-command startup)  |
                                  +===============================+
```

---

## 🚀 Quickstart & One-Command Local Startup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- SQLite 3

### 2. Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/adityabhardwaj29/Insurance_claimed_detection-.git
cd Insurance_claimed_detection-

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. One-Command Master CLI (`run.py`)

The platform includes a unified master CLI (`run.py`):

| Command | Action | URL / Port |
| :--- | :--- | :--- |
| **`python run.py --all`** | **Launch both API & Dashboard concurrently** | API: `8000`, Dashboard: `8501` |
| `python run.py --api` | Start FastAPI Backend server | `http://localhost:8000/docs` |
| `python run.py --dashboard` | Start Streamlit Analytics Portal | `http://localhost:8501` |
| `python run.py --pipeline` | Execute complete reproducible pipeline from scratch | Terminal output |
| `python run.py --journey CLM00001` | Trace complete end-to-end claim journey | Terminal output |
| `python run.py --test` | Execute full 340-test automated test suite | Terminal output |

---

## 🔍 Single Claim Journey Verification

To verify that any claim traverses the entire pipeline without missing dependencies or fabricated steps, run:
```bash
python run.py --journey CLM00001
```

**Verified Output Trace:**
```
===========================================================================
VERIFYING END-TO-END CLAIM JOURNEY: CLM00001
===========================================================================
[1. Relational Facts] Amount: $132,760.00 | Type: Theft | Ground Truth: YES (Fraud)
[2. Features] Days Since Policy Start: 6 | Amount/Premium Ratio: 1.8772
[3. ML Prediction] Model: XGBoost | Fraud Probability: 0.8472
[4. Anomaly Score] Calibrated Score: 0.3716 | Is Outlier: False
[5. Duplicate Detection] Similarity: 0.4903 | Category: SIMILAR
[6. Graph Network] Provider Claim Count: 14 | Fraud Neighbor Ratio: 0.3333
[7. Final Risk Engine] Composite Score: 0.6143 | Risk Band: HIGH
[8. Explainability] Top Risk Driver: ['Days Since Policy Inception (6)', 'Claimant City: Ahmedabad']
    Narrative: Claim exhibits CRITICAL fraud probability of 84.7%, driven by strong supervised signals...
[9. Investigation Case] Case ID: CASE-API-6a6f8abd | Status: UNDER_REVIEW | Priority: HIGH
===========================================================================
CLAIM JOURNEY TRACED AND VERIFIED END-TO-END.
===========================================================================
```

---

## 🌐 FastAPI Production Endpoints

The API is fully documented via interactive Swagger UI at `http://localhost:8000/docs`.

### Key Endpoints:
- `GET /health` : System health & database connectivity
- `GET /claims` : Paginated claims browser with multi-attribute filtering & sorting
- `GET /claims/{claim_id}` : Complete relational claim record
- `GET /claims/{claim_id}/risk` : Multi-signal composite risk score & trigger breakdown
- `GET /claims/{claim_id}/graph` : Ego-network graph nodes & edges
- `GET /claims/{claim_id}/duplicates` : Pairwise similarity scores and matched attributes
- `GET /claims/{claim_id}/explanation` : Phase 12 SHAP factors and 4-quadrant graph evidence
- `GET /dashboard/summary` : Live executive business and fraud metrics
- `POST /predict` : Live supervised XGBoost inference
- `POST /anomaly-score` : Live unsupervised Isolation Forest scoring
- `POST /cases` & `PATCH /cases/{case_id}` : SIU case management workflow with audit trail

---

## 🛡️ Streamlit Dashboard Portal

Accessible at `http://localhost:8501`. Features 9 analytical modules:
1. **Executive Overview (`overview.py`):** 6 key metrics (Total Claims: 320, Flagged Claims: 27, High Risk Claims: 27, Investigation Cases: 27, Fraud Rate: 16.25%, Average Risk Score: 0.2998).
2. **Duplicate Claim Analysis (`duplicates.py`):** Pairwise similarity histogram and cluster distribution.
3. **Graph Relationship Network (`network.py`):** Interactive NetworkX/Plotly multi-entity knowledge graph with node inspector and provider collusion tables.
4. **360° Claim Investigation Dossier (`investigation.py`):** Complete relational entity profiles, SHAP factor attribution waterfall, 4-quadrant graph evidence, and case management actions.
5. **Investigation Cases Queue (`cases.py`):** Operational SIU worklist with priority filtering.
6. **Model Performance & Benchmarks (`model_performance.py`):** Empirical test metrics, confusion matrix, and model comparison table.
7. **Claims Explorer (`claims.py`):** Filterable, searchable data table with CSV export.
8. **Audit Logs (`audit_logs.py`):** Immutable log of all case events, transitions, and notes.
9. **System Monitoring (`monitoring.py`):** Live database and model artifact integrity checks.

---

## 🧪 Automated Test Suite

Run all automated tests across all 14 test modules:
```bash
python -m pytest tests/ -v
```

**Status:**
- **340 tests passing (100% passing rate, 0 failures, 0 errors)**
- Modules tested:
  - `tests/test_anomaly.py`
  - `tests/test_api.py`
  - `tests/test_cases.py`
  - `tests/test_dashboard.py`
  - `tests/test_data.py`
  - `tests/test_duplicate.py`
  - `tests/test_e2e.py`
  - `tests/test_explainability.py`
  - `tests/test_features.py`
  - `tests/test_graph.py`
  - `tests/test_graph_features.py`
  - `tests/test_model.py`
  - `tests/test_relational.py`
  - `tests/test_scoring.py`

---

## 📂 Repository Structure

```
.
├── api/                            # Production FastAPI Backend (routes, schemas, services)
├── dashboard/                      # Multi-Page Streamlit Analytics & Investigation Portal
├── data/
│   ├── raw/                        # Original source datasets (immutable)
│   ├── processed/                  # Validated and cleaned tables
│   ├── relational/                 # Normalized 3NF relational CSVs
│   ├── graph/                      # Knowledge graph nodes and edges
│   └── features/                   # Feature store & precomputed explanations
├── database/                       # SQLite schema DDL, views, and seed scripts
├── models/                         # Persisted ML model weights & metadata
├── notebooks/                      # Exploratory & academic Jupyter research notebooks (01 - 12)
├── reports/                        # Detailed academic phase reports & experimental metrics
├── src/
│   ├── cases/                      # Case management & audit trail domain logic
│   ├── data/                       # Ingestion, validation, and cleaning pipelines
│   ├── duplicate/                  # Pairwise string and numeric similarity engine
│   ├── explainability/             # SHAP TreeExplainer & Graph evidence synthesizers
│   ├── features/                   # Relational & temporal feature engineering
│   ├── graph/                      # NetworkX knowledge graph construction & centrality
│   ├── models/                     # Supervised training & unsupervised anomaly detection
│   ├── scoring/                    # Multi-signal hybrid risk engine
│   └── pipeline.py                 # Master pipeline runner & single claim journey verifier
├── tests/                          # Automated unit, integration, and E2E test suite (340 tests)
├── run.py                          # Master CLI for one-command local startup
└── README.md                       # Comprehensive platform documentation
```
