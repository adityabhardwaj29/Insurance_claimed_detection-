# FraudShield AI — Enterprise System Architecture

## 1. Executive Summary & System Philosophy

**FraudShield AI** is an enterprise-grade Insurance Claims Processing, Fraud Detection, and Special Investigation Unit (SIU) platform. It provides an operational workflow uniting customer relationship management, automated underwriting policy validation, multi-step claim intake, multi-signal algorithmic fraud scoring, explainable AI (SHAP), and human-in-the-loop investigation management.

The platform is designed around strict **academic and empirical integrity**:
- Zero synthetic mock numbers or arbitrary hardcoded statistics.
- All risk scores and fraud probabilities are mathematically calculated by verified machine learning models and deterministic graph algorithms.
- Full provenance tracing: from raw claimant intake data through feature engineering, inference, and human disposition.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------+
|                                 CLIENT TIER                                 |
|                                                                             |
|   +------------------------------------+  +-----------------------------+   |
|   |    React Enterprise SaaS (Vite)    |  | Streamlit Research Console  |   |
|   |    - Dashboard & KPI Ribbon        |  | - Raw Experimentation       |   |
|   |    - Multi-Step Claim Wizard       |  | - Model Tuning & Graphs     |   |
|   |    - 360° Forensic Claim Dossier   |  | - Port 8501                 |   |
|   |    - SIU Case Investigation Triage |  +-----------------------------+   |
|   |    - Customer 360 Directory        |                                    |
|   |    - Port 3000 (Proxy to :8000)    |                                    |
|   +------------------------------------+                                    |
+-----------------------------------------------------------------------------+
                                       |
                               (HTTP REST / JWT)
                                       v
+-----------------------------------------------------------------------------+
|                           API GATEWAY TIER (FastAPI)                        |
|                                                                             |
|   [Auth & RBAC Middleware] -> [Claims & Intake Router] -> [SIU Case Router] |
|   [Policy Verification Router] -> [Customer 360 Router] -> [Audit Stream]   |
+-----------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+------------------------------------+   +------------------------------------+
|       FRAUD INFERENCE ENGINE       |   |          PERSISTENCE TIER          |
|                                    |   |                                    |
|  1. Supervised ML (XGBoost/RF)     |   |  Primary: Supabase PostgreSQL      |
|  2. Isolation Forest Outlier       |   |  - Row-Level Security (RLS)        |
|  3. Multi-Attribute Duplicate Hash |   |  - Relational Schema (001-004)     |
|  4. NetworkX Syndicate Collusion   |   |  Fallback: Local SQLite            |
|  5. Hybrid Scoring Engine          |   |  - Document Storage: /documents    |
|  6. SHAP Attribution Waterfall     |   |                                    |
+------------------------------------+   +------------------------------------+
```

---

## 3. Technology Stack

| Layer | Technologies | Key Responsibilities |
| :--- | :--- | :--- |
| **Frontend Application** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons | Responsive enterprise UI, interactive SVG network graph, multi-step intake wizard, 360° claim dossier. |
| **Research Console** | Streamlit, Plotly, Altair | In-depth research analysis, dataset inspection, exploratory graph visualization. |
| **Backend API Gateway** | FastAPI, Uvicorn, Python 3.13, Pydantic v2 | High-throughput async REST endpoints, JWT authentication, RBAC, input validation. |
| **Machine Learning Engine** | Scikit-Learn, XGBoost, NetworkX, SHAP | Supervised classification, unsupervised anomaly detection, bipartite graph collusion, SHAP feature importance. |
| **Database & Security** | Supabase PostgreSQL, SQLite, bcrypt, Jose JWT | ACID transactions, Row-Level Security (RLS) policies, immutable audit logging. |
| **Deployment** | Docker, Docker Compose, Nginx (Alpine) | Multi-stage production container builds, reverse proxy routing, environment orchestration. |

---

## 4. Multi-Signal Detection Architecture

The platform scores every submitted insurance claim against four complementary detection pillars:

```
                          Claim Features (38 engineered attributes)
                                             |
         +-------------------+---------------+-------------------+
         |                   |               |                   |
         v                   v               v                   v
+-----------------+ +-----------------+ +---------+ +------------------------+
| 1. Supervised   | | 2. Unsupervised | | 3. Dupe | | 4. Graph Syndicate     |
|    XGBoost      | |    Isolation    | |    Hash | |    Collusion           |
|    Ensemble     | |    Forest       | |  Engine | |    Topology            |
| (Weight: 40%)   | | (Weight: 20%)   | | (W: 20%)| |  (Weight: 20%)         |
+-----------------+ +-----------------+ +---------+ +------------------------+
         |                   |               |                   |
         +-------------------+---------------+-------------------+
                                     |
                                     v
                       +---------------------------+
                       |   Hybrid Risk Formula:    |
                       | R = 0.40(ML) + 0.20(Anom) |
                       |   + 0.20(Dup) + 0.20(Net) |
                       +---------------------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
     [Risk Score >= 0.50]                          [Risk Score < 0.25]
              |                                             |
              v                                             v
  Automated SIU Escalation                      Straight-Through Fast-Track
  Investigator Docket Created                   Auto-Approval Queue
```

---

## 5. Security & Access Control Model

1. **Authentication:**
   - JSON Web Tokens (JWT) signed with HMAC-SHA256.
   - Passwords hashed using standard `bcrypt` with salt rounds = 12.
2. **Role-Based Access Control (RBAC):**
   - `CLAIMS_OFFICER`: Claim intake, document upload, initial triage.
   - `INVESTIGATOR`: Evidence evaluation, forensic notes, claimant interview logging.
   - `SUPERVISOR`: Final claim approval, rejection, threshold adjustment sign-off.
   - `ANALYST`: Model retraining inspection, syndicate cluster analysis, drift monitoring.
   - `ADMIN`: User management, system configuration, immutable audit stream inspection.
3. **Row-Level Security (RLS):**
   - Applied via PostgreSQL policies ensuring tenants and roles access only permitted tables and rows.
