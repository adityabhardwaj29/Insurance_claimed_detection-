# Machine Learning Fraud Detection Report
## Supervised Baseline & Gradient Boosting Models

**Date:** 2026-09-16
**Target:** `fraud_label` (Binary: 0 = Legit, 1 = Fraud, ~16.25% prevalence)
**Selected Model:** `XGBoost` (selected by PR-AUC on held-out temporal test set)

---

## 1. Feature Engineering & Preprocessing

### Numeric Features (StandardScaler)
- `claim_amount`
- `claim_age_days`
- `days_since_policy_start`
- `amount_to_premium_ratio`
- `invoice_to_claim_ratio`
- `claimant_claim_frequency`
- `provider_claim_volume`
- `vehicle_age`
- `claimant_age`
- `provider_rating`
- `duplicate_similarity_score`
- `duplicate_flag`


### Categorical Features (OneHotEncoder)
- `claim_type`
- `policy_type`
- `vehicle_type`
- `vehicle_make`
- `provider_type`
- `claimant_city`


### Temporal Splitting & Leakage Prevention
- Claims are strictly ordered chronologically by `claim_date`.
- **Training Split:** First 70% of claims (chronological past).
- **Test Split:** Remaining 30% of claims (chronological future).
- Transformers are fitted strictly on the training set and applied to the test set.

---

## 2. Model Comparison Table

| Model                |   PR-AUC |   ROC-AUC |   F1-Score |   Precision |   Recall |   Precision@10% |   Recall@10% |   Precision@20% |   Recall@20% |   Brier Score |
|:---------------------|---------:|----------:|-----------:|------------:|---------:|----------------:|-------------:|----------------:|-------------:|--------------:|
| XGBoost              |   0.2348 |    0.5819 |     0.1818 |      0.2    |   0.1667 |             0.2 |       0.1111 |          0.1579 |       0.1667 |        0.1906 |
| RandomForest         |   0.2171 |    0.5328 |     0      |      0      |   0      |             0.3 |       0.1667 |          0.1579 |       0.1667 |        0.1735 |
| HistGradientBoosting |   0.2091 |    0.5442 |     0.2162 |      0.2105 |   0.2222 |             0.2 |       0.1111 |          0.2105 |       0.2222 |        0.2191 |
| LogisticRegression   |   0.1777 |    0.4687 |     0.2333 |      0.1667 |   0.3889 |             0.1 |       0.0556 |          0.1579 |       0.1667 |        0.3134 |

---

## 3. Selected Model Performance: `XGBoost`

- **PR-AUC (Average Precision):** 0.2348
- **ROC-AUC:** 0.5819
- **F1-Score:** 0.1818
- **Precision:** 0.2000
- **Recall:** 0.1667
- **Brier Score (Calibration):** 0.1906

### Precision@K and Recall@K (Investigation Efficiency)
- **Precision@10%:** 0.2000 (proportion of top 10% highest-risk claims that are fraud)
- **Recall@10%:** 0.1111 (fraction of all test frauds captured in top 10%)
- **Precision@20%:** 0.1579
- **Recall@20%:** 0.1667

### Confusion Matrix (Test Set, Threshold = 0.50)
| | Predicted Negative (0) | Predicted Positive (1) |
|---|---|---|
| **Actual Legit (0)** | TN = 66 | FP = 12 |
| **Actual Fraud (1)** | FN = 15 | TP = 3 |

---

## 4. Limitations and Next Steps

1. **Synthetic Data Characteristics:** The dataset is project-generated synthetic data. Metrics reflect pattern discovery in this specific synthetic formulation.
2. **Imbalance Constraints:** With ~16.25% positive prevalence, high decision thresholds reduce recall; risk-based ranking via `fraud_probability` is operationally superior to fixed 0.5 binary cutoffs.
3. **Graph Feature Enhancement (Phase 5):** Integrating network centrality and community risk will provide graph-structural signals to further improve PR-AUC.
