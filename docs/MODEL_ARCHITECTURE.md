# Machine Learning & Anomaly Detection Architecture

## 1. Modeling Strategy Overview

The platform uses a two-tier machine learning architecture combining **supervised predictive learning** for known fraud typologies and **unsupervised anomaly detection** for zero-day behavioral deviations.

---

## 2. Supervised Fraud Classification Pipeline

### 2.1. Feature Preprocessing
Features are processed through a strict scikit-learn `ColumnTransformer` inside an unified `Pipeline`:
- **Numeric Pipeline**:
  - `SimpleImputer(strategy="median")`
  - `StandardScaler()`
  - Input Columns: `claim_amount`, `claim_age_days`, `days_since_policy_start`, `amount_to_premium_ratio`, `invoice_to_claim_ratio`, `claimant_claim_frequency`, `provider_claim_volume`, `vehicle_age`, `claimant_age`, `provider_rating`, `duplicate_similarity_score`, `duplicate_flag`.
- **Categorical Pipeline**:
  - `SimpleImputer(strategy="most_frequent")`
  - `OneHotEncoder(handle_unknown="ignore", sparse_output=False)`
  - Input Columns: `claim_type`, `policy_type`, `vehicle_type`, `vehicle_make`, `provider_type`, `claimant_city`.

### 2.2. Temporal Splitting (Zero Data Leakage)
To mirror real-world insurance underwriting where future claims cannot inform current models:
- Claims are sorted chronologically by `claim_date`.
- Split ratio: First 70% claims for training, remaining 30% for out-of-time evaluation.
- Train cutoff: June 29, 2026. Test start: July 1, 2026.
- The preprocessor is fit strictly on `X_train` and transforms `X_test`.

### 2.3. Model Benchmark & Selection
Four candidate architectures were trained and evaluated on held-out test data:
1. **Logistic Regression** (L2 penalty, balanced class weights) — *Baseline*
2. **Random Forest** (150 trees, max depth 6, balanced weights)
3. **HistGradientBoosting** (Histogram-based gradient booster, learning rate 0.05)
4. **XGBoost Classifier** (`scale_pos_weight=5.0`, 100 estimators, max depth 4, learning rate 0.05, subsample 0.85)

**Selection Criterion**: Area Under the Precision-Recall Curve (PR-AUC) on the held-out test set, due to class imbalance (~16.25% fraud rate).
- Selected Model: **XGBoost Classifier**
- Persisted Artifact: `models/fraud_model/model.joblib`

---

## 3. Unsupervised Anomaly Detection

### 3.1. Isolation Forest Architecture
Supervised models can miss novel, emerging fraud mechanisms. The unsupervised pipeline detects distributional outliers:
- **Algorithm**: `IsolationForest`
- **Contamination Parameter**: `contamination=0.10`
- **Estimators**: 100 trees
- **Features Used**: Multidimensional financial and behavioral ratios (`claim_amount`, `amount_to_premium_ratio`, `invoice_to_claim_ratio`, `days_since_policy_start`, `vehicle_age`).

### 3.2. Score Calibration
Raw Isolation Forest decision functions output values where lower numbers indicate higher anomaly degree.
- The platform inverts and min-max scales the score into $[0, 1]$:
  $$S_{\text{Anomaly}} = \text{clip}\left(\frac{\text{score\_max} - \text{score}}{\text{score\_max} - \text{score\_min}}, 0, 1\right)$$
- Anomaly scores above the 90th percentile trigger the `ISOLATION_FOREST_OUTLIER` reason code.
- Persisted Artifact: `models/anomaly_model/isolation_forest.joblib`

---

## 4. Explainable AI (SHAP TreeExplainer)

For every evaluated claim, local feature attributions are computed using the exact **TreeSHAP** algorithm:
- Base Value $\phi_0$: Expected log-odds of fraud across training background.
- Local Attributions $\phi_i$: Additive contribution of each feature $i$ such that:
  $$f(x) = \phi_0 + \sum_{i=1}^M \phi_i$$
- Returns the top 3 risk-increasing features (e.g. `days_since_policy_start < 10`, `amount_to_premium_ratio > 1.8`) and top 2 risk-mitigating features (e.g. `claimant_age`, `provider_rating`).
- Pre-computed explanations are persisted to `models/explainability/shap_explanations.json` for low-latency retrieval.
