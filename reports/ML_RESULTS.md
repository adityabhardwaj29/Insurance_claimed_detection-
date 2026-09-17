# Supervised Machine Learning Benchmark Results

## 1. Experimental Methodology

To benchmark supervised fraud detection capabilities while preventing future-data leakage:
- **Dataset**: 320 claims partitioned chronologically by `claim_date`.
- **Training Set**: Chronological first 70% ($N = 224$ claims, 34 fraud, 15.18% prevalence).
- **Test Set**: Chronological remaining 30% ($N = 96$ claims, 18 fraud, 18.75% prevalence).
- **Evaluation Priority**: Area Under the Precision-Recall Curve (PR-AUC / Average Precision) due to positive class rarity.

---

## 2. Comparative Benchmark Table

| Model Architecture | PR-AUC | ROC-AUC | F1-Score | Precision | Recall | Precision@10% | Recall@10% | Precision@20% | Recall@20% | Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Selected)** | **0.2348** | **0.5819** | **0.1818** | **0.2000** | **0.1667** | **0.2000** | **0.1111** | **0.1579** | **0.1667** | **0.1906** |
| Random Forest | 0.2171 | 0.5328 | 0.0000 | 0.0000 | 0.0000 | 0.3000 | 0.1667 | 0.1579 | 0.1667 | 0.1735 |
| HistGradientBoosting | 0.2091 | 0.5442 | 0.2162 | 0.2105 | 0.2222 | 0.2000 | 0.1111 | 0.2105 | 0.2222 | 0.2191 |
| Logistic Regression (Baseline)| 0.1777 | 0.4687 | 0.2333 | 0.1667 | 0.3889 | 0.1000 | 0.0556 | 0.1579 | 0.1667 | 0.3134 |

---

## 3. Analysis of Selected Model: XGBoost

### 3.1. Performance Metrics
- **PR-AUC**: `0.2348` (Outperforms the random baseline prevalence of 0.1875 by +25.2%).
- **ROC-AUC**: `0.5819`.
- **Calibration (Brier Score)**: `0.1906`.
- **Top 10% Triage Efficiency (Precision@10%)**: `0.2000` (Directing investigators to the top decile of highest risk predictions captures fraud at higher density than baseline random audit).

### 3.2. Test Set Confusion Matrix (Default Threshold 0.50)
- **True Negatives (TN)**: 66
- **False Positives (FP)**: 12
- **False Negatives (FN)**: 15
- **True Positives (TP)**: 3

### 3.3. Key Findings
1. Fixed binary classification thresholds (e.g. 0.50) suffer on imbalanced data. Continuous risk scoring via `fraud_probability` provides significantly greater utility for operational triage than binary decisions.
2. Tabular features alone provide modest separation; enrichment with graph centrality and anomaly scoring (Phase 8 hybrid engine) provides the complementary signals needed for robust ranking.
