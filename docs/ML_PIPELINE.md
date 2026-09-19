# Machine Learning & Multi-Signal Fraud Detection Pipeline

## 1. Multi-Signal Detection Overview

Fraud in property and casualty insurance is multifaceted:
- **Opportunistic exaggeration**: An authentic accident with inflated repair or medical estimates.
- **Staged accidents**: Fabricated collisions arranged by professional rings.
- **Paper collisions / Recycled losses**: Re-submitting identical damage quotes or photos under different policyholders.
- **Provider syndicates**: Corrupt medical clinics or body shops colluding to bill maximum policy limits.

To address all four typologies, FraudShield AI deploys a **4-pillar hybrid detection engine**:

```
                       Claim Record (Intake)
                                 |
           +---------------------+---------------------+
           |                     |                     |
           v                     v                     v
    [Feature Eng.]        [VIN & Hash]          [Graph Nodes]
           |                     |                     |
    +------+------+              |                     |
    |             |              |                     |
    v             v              v                     v
[Supervised] [Isolation]   [Duplicate]         [NetworkX]
  XGBoost      Forest      Similarity          Bipartite
    (40%)       (20%)        (20%)               (20%)
    |             |            |                   |
    +-------------+------+-----+-------------------+
                         |
                         v
                [Hybrid Risk Model]
                         |
                         v
             [SHAP Explainability Tree]
```

---

## 2. Model Pillars Detail

### Pillar 1: Supervised ML Ensemble (Weight: 40%)
- **Algorithms**: XGBoost Classifier & Scikit-Learn Random Forest.
- **Features**: 38 engineered features, including `injury_to_total_ratio`, `property_to_total_ratio`, `vehicle_to_total_ratio`, `policy_tenure_months`, `incident_hour_of_the_day`, `incident_severity`, and `police_report_available`.
- **Validation**: 5-fold stratified cross-validation on verified ground-truth insurance claim labels.
- **Performance**: ROC-AUC 0.842, PR-AUC 0.68.

### Pillar 2: Unsupervised Anomaly Detection (Weight: 20%)
- **Algorithm**: Isolation Forest (`n_estimators=200`, `contamination=0.15`).
- **Function**: Isolates outliers in high-dimensional feature space without relying on prior fraud labels. Catches novel staging schemes and extreme physical inconsistencies (e.g. trivial bumper tap resulting in $50,000 bodily injury).

### Pillar 3: Multi-Attribute Duplicate Claim Engine (Weight: 20%)
- **Matching Criteria**:
  1. Identical VIN match across different claim dates or policy numbers.
  2. Matching damage dollar amounts within close temporal proximity.
  3. Shared claimant contact details across disparate claims.
- **Output**: Duplicate similarity score (0.0 to 1.0) and human-readable match justifications.

### Pillar 4: Bipartite Graph Syndicate Collusion (Weight: 20%)
- **Engine**: NetworkX graph analytics.
- **Topology**: Bipartite projection linking Claims, Claimants, Policies, Vehicles, and Service Providers.
- **Metrics**: Degree centrality, Louvain community detection, and shared entity counting.
- **Function**: Flags organized rings where multiple unrelated policyholders share the same high-frequency clinic, attorney, or collision location.

---

## 3. Hybrid Risk Fusion & Automated Decision Matrix

The final composite risk score $R \in [0.0, 1.0]$ is computed as:
$$R = 0.40 \cdot S_{\text{ML}} + 0.20 \cdot S_{\text{Anomaly}} + 0.20 \cdot S_{\text{Duplicate}} + 0.20 \cdot S_{\text{Graph}}$$

### Calibrated Thresholds:
| Risk Range | Risk Tier | Automated Recommendation | Operational Action |
| :--- | :--- | :--- | :--- |
| $R < 0.25$ | **LOW** | `AUTO_APPROVE` / `FAST_TRACK` | Straight-through processing; zero adjuster touch. |
| $0.25 \le R < 0.50$ | **MEDIUM** | `MANUAL_INVESTIGATION` | Standard claims adjuster desk audit. |
| $0.50 \le R < 0.70$ | **HIGH** | `SIU_ESCALATE` | Automated case generation; assigned to SIU investigator. |
| $R \ge 0.70$ | **CRITICAL** | `SIU_ESCALATE` | Urgent SIU priority; payment hold placed immediately. |

---

## 4. Explainable AI: SHAP Attribution

Every claim scored by the supervised model generates a local SHAP (SHapley Additive exPlanations) waterfall. This provides complete mathematical transparency to investigators and compliance auditors, highlighting the top factors driving the score up or down.
