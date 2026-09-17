# Phase 12: Explainable Fraud Detection (XAI) & Graph Evidence Report

## Executive Summary

Phase 12 implements the **Explainable Fraud Detection (XAI)** subsystem for the Graph-Enhanced Insurance Claim Fraud Detection platform. It addresses the critical academic and regulatory requirement that machine learning models and graph algorithms deployed in high-stakes insurance claims triage must not operate as uninterpretable black boxes.

In accordance with the **Global Project Rules**:
- **Zero Hallucinated Explanations:** Explanations are derived exclusively from actual SHAP (SHapley Additive exPlanations) values computed on the trained supervised XGBoost model and verifiable topological evidence extracted from the heterogeneous insurance knowledge graph.
- **Directional Factor Separation:** For every claim, features are mathematically partitioned into **risk-increasing** (positive SHAP impact pushing probability towards fraud) and **risk-decreasing / mitigating** (negative SHAP impact supporting legitimacy).
- **Knowledge Graph Grounding:** The graph explanation explicitly isolates:
  1. *Suspicious Connections* (cross-territory repairs, anomalous network bridges)
  2. *High-Degree Entities* (high-volume repair facilities, serial repeat claimants, recycled vehicles)
  3. *Repeated Relationships* (claimant-provider collusion pairings across distinct incidents)
  4. *Neighboring Flagged Claims* (exact claim IDs in the ego subnetwork with confirmed fraud or high risk scores)

---

## 1. Mathematical & Algorithmic Foundation

### A. Supervised ML: TreeSHAP on XGBoost
For a claim with feature vector $x \in \mathbb{R}^M$, the local prediction $f(x)$ is decomposed via Shapley values:
$$f(x) = \phi_0 + \sum_{j=1}^M \phi_j(x)$$
where:
- $\phi_0 = \mathbb{E}[f(X)]$ is the base expected value across the training population ($0.3345$)
- $\phi_j(x)$ is the marginal Shapley contribution of feature $j$
- Direction assignment:
  $$\text{direction}(j) = \begin{cases} \text{risk\_increasing}, & \phi_j(x) > 0 \\ \text{risk\_decreasing}, & \phi_j(x) < 0 \end{cases}$$

To maintain human interpretability, one-hot encoded dummy variables are cleanly mapped to descriptive domain names (e.g., `Claimant City / Territory: Ahmedabad`, `Insurance Policy Type: Third Party`).

### B. Graph Topological Evidence Extraction
Graph evidence is extracted deterministically from `data/features/graph_features.csv` and relational schema joins:
1. **Suspicious Connections:** Flagged when `suspicious_neighbor_count > 0`, betweenness centrality $> 0.005$, or when claimant residence territory differs from the servicing provider territory.
2. **High-Degree Hubs:** Flags providers with $\ge 15$ network edges or $\ge 8$ claims, claimants with $\ge 6$ edges or $\ge 3$ claims, and vehicles involved in $\ge 2$ separate claim incidents.
3. **Repeated Relationships:** Identifies exact pairings where `repeated_claimant_provider > 0` or vehicles claimed across multiple separate policies.
4. **Neighboring Flagged Claims:** Retrieves immediate neighbors sharing claimant, provider, or vehicle that have ground-truth fraud (`fraud_label == 1`) or composite risk $\ge 0.50$, reporting their claim IDs, amounts, and statuses.

---

## 2. Core Architecture & Module Overview

```
src/explainability/
├── __init__.py                     # Package exports (ShapExplainer, GraphExplainer, ClaimExplainer, explain_claim)
├── shap_explainer.py               # TreeExplainer wrapper, feature mapping, directional factor sorting
├── graph_explainer.py              # Topological evidence extractor across 4 structural dimensions
├── claim_explainer.py              # Unified multimodal orchestrator and natural language briefing generator
└── batch_explain.py                # Batch precomputation script generating claim_explanations.json
```

### Unified Output Schema
```json
{
  "claim_id": "CLM00001",
  "fraud_probability": 0.8472,
  "base_value": 0.3345,
  "top_factors": [
    {
      "feature": "Days Since Policy Inception (6)",
      "impact": 0.5013,
      "direction": "risk_increasing"
    },
    {
      "feature": "Claimant City / Territory: Ahmedabad",
      "impact": 0.2412,
      "direction": "risk_increasing"
    },
    {
      "feature": "Insurance Policy Type: Third Party",
      "impact": -0.1204,
      "direction": "risk_decreasing"
    }
  ],
  "top_positive_factors": [...],
  "top_negative_factors": [...],
  "graph_explanation": {
    "suspicious_connections": [
      {
        "type": "CROSS_TERRITORY_PROVIDER_SERVICE",
        "description": "Claimant registered in 'Ahmedabad' serviced by provider in distant territory 'Delhi'",
        "evidence_value": "Ahmedabad -> Delhi"
      }
    ],
    "high_degree_entities": [
      {
        "entity_type": "Provider",
        "entity_id": "PRV007",
        "name": "Provider 007",
        "degree": 21,
        "claim_count": 14,
        "description": "High-volume service provider 'Provider 007' connected to 21 edges and 14 claims"
      }
    ],
    "repeated_relationships": [
      {
        "relationship_type": "REPEATED_VEHICLE_CLAIMS",
        "entity_pair": "Vehicle: VEH0062",
        "count": 4,
        "description": "Vehicle was claimed across 4 separate incidents"
      }
    ],
    "neighboring_flagged_claims": [
      {
        "claim_id": "CLM00010",
        "shared_relationship": "SHARED_PROVIDER",
        "claim_amount": 243287.0,
        "claim_type": "Accident",
        "confirmed_fraud": true,
        "final_risk_score": 0.6913,
        "risk_band": "HIGH",
        "description": "Neighbor claim 'CLM00010' ($243,287.00) via SHARED_PROVIDER is CONFIRMED FRAUD (Score: 0.6913)"
      }
    ],
    "fraud_neighbor_count": 1,
    "fraud_neighbor_ratio": 0.3333
  },
  "summary_text": "Claim exhibits CRITICAL fraud probability of 84.7%, driven by strong supervised and behavioral signals..."
}
```

---

## 3. Streamlit Dashboard Integration

The investigation dossier page (`dashboard/pages/investigation.py`) features:
1. **Investigator Briefing Banner:** Non-technical narrative summarizing primary ML drivers and graph patterns.
2. **Interactive SHAP Factor Plot:** Color-coded horizontal bar chart distinguishing positive risk-increasing factors (Crimson) and negative mitigating factors (Teal).
3. **Factor Breakdown Tables:** Top 5 positive and top 5 negative features with exact marginal impact scores.
4. **Graph Evidence Decomposition Cards:** Tabbed quadrants detailing suspicious connections, entity degree hubs, repeated pairings, and neighboring flagged claims.

---

## 4. Verification & Test Results

- **Explainability Test Suite (`tests/test_explainability.py`):** **6/6 PASSED**
  - Model loading and TreeExplainer initialization
  - Factor directionality (`risk_increasing` vs `risk_decreasing`)
  - Graph evidence extraction from SQLite and engineered features
  - Unified JSON schema compliance
  - Full dataset coverage (all 320 claims precomputed in `claim_explanations.json`)
- **API Test Suite (`tests/test_api.py`):** **22/22 PASSED**
  - Verified `GET /claims/{claim_id}/explanation` returns complete SHAP and graph evidence.
- **Full Project Test Suite:** **335 PASSED in 26.86s** (0 failed, 0 errors across all 13 test modules).
