# Data Flow Architecture

## 1. End-to-End Data Lifecycle

The platform follows a unidirectional, reproducible data flow across nine distinct transformation layers:

```
[1. RAW DATA]
      |
      v
[2. RELATIONAL NORMALIZATION] ---------> [SQLITE DATABASE: fraud_detection.db]
      |
      +------------------------+------------------------+
      |                        |                        |
      v                        v                        v
[3. FEATURE ENG.]    [4. DUPLICATE DETECT.]   [5. GRAPH CONSTRUCTION]
      |                        |                        |
      |                        |                        v
      |                        |                [6. GRAPH TOPOLOGY]
      |                        |                        |
      +------------+-----------+                        |
                   |                                    |
                   v                                    v
          [7. MODEL INFERENCE]                 [GRAPH FEATURES CSV]
          - Supervised XGBoost (P(Fraud))               |
          - Isolation Forest (Anomaly Score)            |
                   |                                    |
                   +-----------------+------------------+
                                     |
                                     v
                          [8. HYBRID RISK ENGINE]
                          - Weighted Combination
                          - Risk Banding
                          - Rule Catalog Triggers
                                     |
                                     +------------------+
                                     |                  |
                                     v                  v
                          [9. CASE MANAGEMENT]   [10. EXPLAINABILITY]
                          - SIU Case Records     - SHAP TreeExplainer
                          - Audit Events Trail   - Graph Evidence Subnet
                                     |                  |
                                     +------------------+
                                     |
                                     v
                       [11. SERVING & PRESENTATION]
                       - FastAPI REST API (Port 8000)
                       - Streamlit Analytics Portal (Port 8501)
```

---

## 2. Stage-by-Stage Data Transformation

### Stage 1: Raw Ingestion to Relational Storage
- **Source Files**: `data/raw/` CSV files.
- **Transformations**:
  - Null value imputation and data type coercion.
  - Foreign key relationship validation.
  - Storage into SQLite database tables (`claims`, `claimants`, `policies`, `vehicles`, `providers`, `invoices`, `locations`).
- **Destination**: `database/fraud_detection.db` (320 claims, 120 claimants, 140 policies, 130 vehicles, 25 providers, 220 invoices, 60 locations).

### Stage 2: Feature Engineering & Preprocessing
- **Source**: Relational tables joined on foreign keys.
- **Engineered Metrics**:
  - `claim_age_days`: Age in days relative to dataset observation horizon.
  - `days_since_policy_start`: Days elapsed between policy start date and claim incident.
  - `amount_to_premium_ratio`: Claim amount divided by annual premium.
  - `invoice_to_claim_ratio`: Repair invoice amount divided by reported claim amount.
  - `claimant_claim_frequency`: Cumulative historical count of claims filed by the claimant prior to current date.
  - `provider_claim_volume`: Cumulative historical count of claims handled by the provider prior to current date.
- **Temporal Split**: Chronological partition (first 70% claims for training, remaining 30% for out-of-time testing).
- **Destination**: `data/features/claim_features.csv` (320 rows, 21 columns).

### Stage 3: Duplicate Detection
- **Source**: Claim descriptions and relational attributes.
- **Transformation**:
  - Tokenization, stopword removal, and TF-IDF vectorization ($n$-gram range 1 to 2).
  - Pairwise cosine similarity matrix computation across all 320 claims.
  - Self-similarity diagonal masked to 0.0.
  - Pair matching and duplicate clustering.
- **Destination**: `data/features/duplicate_features.csv`.

### Stage 4: Knowledge Graph Construction & Graph Feature Extraction
- **Source**: Relational tables.
- **Nodes**: 765 nodes across 7 ontological categories (`Claim`, `Claimant`, `Policy`, `Vehicle`, `Provider`, `Invoice`, `Location`).
- **Edges**: 1,770 edges across 10 relationship types (`FILED`, `ASSIGNED_TO`, `COVERED_BY`, `INVOLVES`, `HAS`, `LOCATED_AT`, `WITHIN_TERRITORY`, `OWNS`, `ISSUED_BY`, `OCCURRED_AT`).
- **Graph Metrics**: Degree centrality, clustering coefficient, shared provider claim frequency, and fraud neighbor ratio.
- **Destination**: `data/graph/nodes.csv`, `data/graph/edges.csv`, and `data/features/graph_features.csv`.

### Stage 5: Multi-Signal Model Inference
- **Supervised Classifier**: XGBoost pipeline (`models/fraud_model/model.joblib`) outputs probability $P(\text{Fraud}) \in [0, 1]$.
- **Unsupervised Anomaly Detector**: Isolation Forest (`models/anomaly_model/isolation_forest.joblib`) outputs calibrated anomaly score $\in [0, 1]$.

### Stage 6: Hybrid Risk Engine & Rule Triggering
- **Aggregation**:
  $$\text{Final Risk Score} = 0.40 \cdot S_{\text{ML}} + 0.20 \cdot S_{\text{Anomaly}} + 0.15 \cdot S_{\text{Dup}} + 0.25 \cdot S_{\text{Graph}}$$
- **Operational Banding**: Assigned to `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- **Reason Codes**: Triggered deterministically from codified risk rules.
- **Destination**: `data/features/final_risk_scores.csv`.

### Stage 7: Case Management & Explainability Synthesis
- **Case Generation**: High/Critical claims populate `investigation_cases` table in SQLite.
- **Explainability**: SHAP TreeExplainer generates top risk-increasing and risk-decreasing features, merged with ego-network graph evidence into structured dossiers.

### Stage 8: API Serving & Dashboard Rendering
- **FastAPI**: Ingests database and feature files into memory caches; serves REST endpoints.
- **Streamlit**: Queries SQLite views and live endpoints to render metrics, charts, and interactive graph visualizations.
