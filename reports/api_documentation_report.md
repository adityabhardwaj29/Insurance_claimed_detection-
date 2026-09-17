# Phase 10: FastAPI Backend API Documentation Report

## Executive Summary

Phase 10 provides a clean, production-grade REST API built using **FastAPI**. All 15 endpoints are fully wired to active SQLite tables, trained supervised ML pipelines (XGBoost), unsupervised anomaly detectors (Isolation Forest), graph topological features, and the Phase 8 hybrid fraud risk engine.

In accordance with the **Global Project Rules**:
- Database credentials and file locations are configurable via environment variables (`DATABASE_URL`, `FRAUD_MODEL_PATH`, `CORS_ORIGINS`) and never hardcoded.
- All predictions, scores, and statistics are evaluated live from persisted models and databases; no values are simulated or randomly generated.
- Full interactive OpenAPI documentation is exposed via Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 1. API Architecture & Configuration

- **Core Module**: [`api/main.py`](file:///c:/graph_enhanced_build/api/main.py)
- **Settings**: [`src/utils/config.py`](file:///c:/graph_enhanced_build/src/utils/config.py)
- **Middleware**:
  - `CORSMiddleware`: Configurable via `CORS_ORIGINS` environment variable.
  - Request Timing and Logging: Logs method, path, HTTP status, and latency (ms).
  - Global Exception Handlers: Handles `sqlite3.IntegrityError` (HTTP 400) and general unhandled exceptions (HTTP 500) with JSON envelopes.

---

## 2. Implemented Endpoints Reference

### System & Health
| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service status, SQLite connection, model readiness, claim count. |
| `GET` | `/openapi.json` | OpenAPI 3.1 specification schema. |
| `GET` | `/docs` | Interactive Swagger UI. |
| `GET` | `/redoc` | ReDoc API documentation. |

### Claims & Analytical Intelligence
| Method | Path | Description |
|---|---|---|
| `GET` | `/claims` | List claims with pagination (`limit`, `offset`), filtering (`status`, `claim_type`, `fraud_label`, `min_amount`, `max_amount`), and sorting (`sort_by`, `sort_order`). |
| `GET` | `/claims/{claim_id}` | Relational claim details with claimant, provider, policy, vehicle, and invoice objects. |
| `GET` | `/claims/{claim_id}/risk` | Multi-signal composite risk score, operational risk band, component scores, and reason triggers. |
| `GET` | `/claims/{claim_id}/graph` | Subnetwork surrounding the claim: nodes (claimant, provider, policy, vehicle, sibling claims) and edges. |
| `GET` | `/claims/{claim_id}/duplicates` | Pairwise duplicate similarity score, duplicate cluster type, and matching attributes. |
| `GET` | `/claims/{claim_id}/explanation` | Explainable AI factor contributions, signal weights, and narrative explanation. |

### Case Management (Investigation Queue)
| Method | Path | Description |
|---|---|---|
| `GET` | `/cases` | List investigation cases with filtering (`status`, `priority`, `assigned_to`, `min_risk`). |
| `POST` | `/cases` | Create new case for triage queue with initial priority and notes. |
| `GET` | `/cases/{case_id}` | Retrieve individual case record. |
| `PATCH` | `/cases/{case_id}` | Partially update case status, priority, investigator assignment, notes, or resolution. |
| `POST` | `/cases/{case_id}/status` | Transition case status following strict lifecycle rules. |
| `POST` | `/cases/{case_id}/assign` | Assign investigator (auto-transitions `NEW` to `UNDER_REVIEW`). |
| `POST` | `/cases/{case_id}/notes` | Add timestamped investigator inquiry note. |
| `GET` | `/cases/{case_id}/history` | Chronological audit trail of all state mutations and notes. |
| `POST` | `/cases/{case_id}/resolve` | Record human review resolution (`RESOLVED` or `FALSE_POSITIVE`). |
| `GET` | `/cases/{case_id}/dossier` | Complete evidence dossier assembling all claim data for investigator review. |

### Dashboard & Real-Time Inference
| Method | Path | Description |
|---|---|---|
| `GET` | `/dashboard/summary` | Real-time business KPIs, fraud rates, active queue counts, and mean risk score. |
| `POST` | `/predict` | Live supervised inference using trained XGBoost model pipeline for arbitrary features or claim IDs. |
| `POST` | `/anomaly-score` | Live anomaly score using calibrated Isolation Forest ensemble. |
| `POST` | `/graph-analysis` | Topological network analysis for claims, claimants, or providers. |

---

## 3. Verification & Test Results

- **API Test Suite**: **22 passed in `tests/test_api.py`**
- **Full Project Test Suite**: **318 passed in 17.59s** (0 failed, 0 errors across 11 test modules)
- **Response Validation**: Validated via Pydantic V2 schemas with strict typing and input coercion.
