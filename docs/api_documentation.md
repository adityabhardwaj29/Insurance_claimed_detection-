# FastAPI Backend API Specification

## 1. Overview

The backend is built using **FastAPI** (`api/main.py`), exposing 15 REST endpoints with automatic OpenAPI v3 documentation, Pydantic v2 data validation, CORS middleware, and request timing logging.

- **Base URL**: `http://localhost:8000`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 2. API Endpoints Catalog

### 2.1. System Health
| Method | Endpoint | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Verifies database connectivity and model artifact readiness | `HealthResponse` |

### 2.2. Claims Management
| Method | Endpoint | Description | Parameters / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/claims` | List claims with pagination, filtering, and sorting | `status`, `claim_type`, `fraud_label`, `min_amount`, `max_amount`, `sort_by`, `sort_order`, `limit`, `offset` |
| `GET` | `/claims/{claim_id}` | Full relational details (claimant, provider, policy, vehicle, invoice) | `claim_id: str` |
| `GET` | `/claims/{claim_id}/risk` | Composite risk score, risk band, 4 sub-signals, and reason codes | `claim_id: str` |
| `GET` | `/claims/{claim_id}/graph` | Ego subnetwork (nodes, edges, metrics, connected claims) | `claim_id: str` |
| `GET` | `/claims/{claim_id}/duplicates`| Duplicate similarity score and matched claim pairing | `claim_id: str` |
| `GET` | `/claims/{claim_id}/explanation`| SHAP factor attributions and synthesized graph evidence | `claim_id: str` |

### 2.3. SIU Investigation Cases (Phase 9)
| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/cases` | Query cases with status, priority, and assignment filters | Query params (`status`, `priority`, `assigned_to`, `limit`, `offset`) |
| `POST` | `/cases` | Create a new case in the investigation queue | `CaseCreateRequest` |
| `GET` | `/cases/{case_id}` | Retrieve case details, investigator notes, and audit history | `case_id: str` |
| `PATCH`| `/cases/{case_id}` | Update case status, priority, investigator, notes, or resolution | `CasePatchRequest` |
| `GET` | `/cases/{case_id}/history`| Retrieve chronological audit event trail | `case_id: str` |

### 2.4. Analytical & Dashboard Views
| Method | Endpoint | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/summary` | Executive summary metrics (total claims, fraud count, fraud rate %, active cases) | `SummaryResponse` |
| `GET` | `/claims/top-risk` | Priority queue of highest-risk claims for SIU triage | `List[ClaimListItem]` |

### 2.5. Real-Time Model Inference
| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `POST` | `/predict` | Real-time supervised XGBoost fraud probability prediction | `PredictionRequest` |
| `POST` | `/anomaly-score` | Real-time unsupervised Isolation Forest anomaly evaluation | `AnomalyRequest` |
| `POST` | `/graph-analysis` | Real-time graph neighbor and topological analysis | `GraphAnalysisRequest` |

---

## 3. Sample Requests and Responses

### 3.1. Health Check
```http
GET /health HTTP/1.1
Host: localhost:8000
```
```json
{
  "status": "ok",
  "database_connected": true,
  "models_ready": {
    "fraud_xgboost": true,
    "anomaly_isolation_forest": true,
    "risk_scores_table": true,
    "graph_features": true
  },
  "total_claims": 320,
  "version": "1.0.0"
}
```

### 3.2. Claim Explanation Endpoint
```http
GET /claims/CLM00001/explanation HTTP/1.1
Host: localhost:8000
```
```json
{
  "claim_id": "CLM00001",
  "fraud_probability": 0.8472,
  "final_risk_score": 0.6143,
  "risk_band": "HIGH",
  "top_risk_increasing_factors": [
    {
      "feature": "days_since_policy_start",
      "display_name": "Days Since Policy Inception",
      "feature_value": 6.0,
      "shap_value": 1.428,
      "contribution": "INCREASES_RISK"
    }
  ],
  "graph_evidence": {
    "claimant_connected_claims": 3,
    "provider_claim_volume": 14,
    "fraud_neighbor_ratio": 0.3333
  },
  "narrative_explanation": "Claim exhibits HIGH fraud risk. Incident occurred only 6 days post-inception..."
}
```

---

## 4. Error Handling and Status Codes

- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created (e.g. `POST /cases`).
- `400 Bad Request`: Invalid state transition or business rule violation.
- `404 Not Found`: Claim ID or Case ID does not exist in SQLite database.
- `422 Unprocessable Entity`: Schema validation failure (e.g. negative pagination limit, invalid enum).
- `500 Internal Server Error`: Unhandled server exception with structured JSON logging.
