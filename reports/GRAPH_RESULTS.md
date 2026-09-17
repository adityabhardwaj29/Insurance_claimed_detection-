# Knowledge Graph Analysis & Network Results

## 1. Topological Graph Metrics

The heterogeneous knowledge graph constructed in Phase 6 models the complete relational ecosystem:

| Graph Metric | Value | Interpretation |
| :--- | :---: | :--- |
| **Total Nodes** | 1,020 | All entities across 7 ontological tiers |
| **Total Edges** | 2,615 | Directed and undirected relationships |
| **Density** | 0.005032 | Sparse network structure typical of social/transactional domains |
| **Connected Components**| 1 | Fully connected component connecting all active entities |
| **Isolated Nodes** | 0 | Zero disconnected entities |
| **Average Degree** | 5.13 | Average entity interconnectivity |

---

## 2. Node Degree Distributions by Entity Type

| Node Type | Node Count | Mean Degree | Median Degree | Min Degree | Max Degree |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Provider** | 25 | 22.60 | 22.0 | 15 | 34 |
| **Location** | 65 | 9.00 | 1.0 | 1 | 123 |
| **Claim** | 320 | 6.00 | 6.0 | 6 | 6 |
| **Claimant** | 120 | 5.92 | 6.0 | 1 | 11 |
| **Vehicle** | 130 | 3.46 | 3.0 | 1 | 9 |
| **Policy** | 140 | 3.29 | 3.0 | 1 | 8 |
| **Invoice** | 220 | 2.45 | 2.0 | 1 | 7 |

---

## 3. High-Throughput & Suspicious Provider Analysis

Analysis of provider degree centrality revealed significant funneling of claims through key repair providers:
- **`provider:PRV013`**: Degree = 34 (Highest throughput repair facility)
- **`provider:PRV002`**: Degree = 27
- **`provider:PRV016`**: Degree = 27
- **`provider:PRV022`**: Degree = 27

Providers handling disproportionately high claim volumes exhibit higher historical fraud-association rates, providing a strong structural indicator for the hybrid risk engine.

---

## 4. Fraud Neighbor Ratio Correlation

By projecting 1-hop and 2-hop neighbor relationships:
- Claims connected to claimants or providers with multiple prior fraud flags exhibit a higher likelihood of fraud.
- In the hybrid scoring engine, claims with `fraud_neighbor_ratio >= 0.25` trigger the `FRAUD_NEIGHBOR_PRESENT` reason code, directly improving SIU case prioritization.
