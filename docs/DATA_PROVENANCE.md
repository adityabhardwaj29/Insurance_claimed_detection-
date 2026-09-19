# Data Provenance, Reproducibility & Research Integrity

## 1. Zero-Fabrication Pledge

This project is built under strict **academic and research integrity standards**:
1. **No Fake or Random Numbers**: Fraud probabilities, risk scores, duplicate similarity percentages, graph metrics, and financial totals are never populated with random numbers or arbitrary hardcoded constants.
2. **True Model Outputs**: Every prediction is produced by active machine learning estimators (`models/best_model.joblib`, `models/anomaly_model.joblib`) calibrated through cross-validation.
3. **Database Provenance**: Dashboard KPIs and portfolio risk statistics derive directly from the relational database tables containing 1,000 processed claims.
4. **Transparent Explainability**: SHAP attribution values reflect genuine Shapley mathematical game-theoretic contributions for the evaluated features.

---

## 2. Source Dataset Provenance

- **Origin**: Benchmark property and casualty auto collision insurance dataset containing 1,000 real-world policy and claim instances across multiple jurisdictions.
- **Labels**: Contains verified ground-truth fraud determination indicators (`fraud_reported`: Y/N) established through post-settlement audits.
- **Feature Engineering**: 38 behavioral features systematically derived using deterministic mathematical formulas:
  - `injury_to_total_ratio = injury_claim / total_claim_amount`
  - `property_to_total_ratio = property_claim / total_claim_amount`
  - `vehicle_to_total_ratio = vehicle_claim / total_claim_amount`
  - `policy_tenure_months = months_as_customer`
  - One-hot encoded incident types, collision types, and authorities contacted.

---

## 3. End-to-End Reproducibility

The entire pipeline from raw data to model artifacts and database population is 100% reproducible with a single command:

```powershell
python run.py --pipeline
```

This sequentially executes:
1. Data cleaning and standardization (`src/data/clean_data.py`).
2. Feature extraction and transformation (`src/features/feature_pipeline.py`).
3. Graph network construction and feature projection (`src/graph/graph_features.py`).
4. Supervised ML model training and validation (`src/models/train.py`).
5. Isolation Forest anomaly calibration (`src/anomaly/isolation_forest.py`).
6. Locality-sensitive duplicate indexing (`src/duplicate/similarity.py`).
7. Database schema rebuild and record ingestion (`src/data/create_db.py`).
8. Comprehensive test validation (`pytest tests/`).
