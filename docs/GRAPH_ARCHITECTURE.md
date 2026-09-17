# Knowledge Graph Architecture

## 1. Graph Overview

Standard tabular machine learning models treat each claim as an independent observation ($i.i.d.$ assumption), failing to identify organized fraud rings, shared fraudulent providers, or identity rotation. The **Knowledge Graph Architecture** models the interconnected insurance domain as a heterogeneous network, extracting structural relationships to enrich predictive scoring.

---

## 2. Graph Ontology and Schema

```
                           +---------------+
                           |   Location    |
                           +---------------+
                               ^       ^
                 WITHIN_TERRITORY     LOCATED_AT
                               |       |
                               |   +---+-----------+
                               |   |   Provider    |
                               |   +---------------+
                               |       ^       ^
                               |  ISSUED_BY   ASSIGNED_TO
                               |       |       |
+---------------+          +---------------+   |
|   Claimant    |--OWNS--->|    Policy     |   |
+---------------+          +---------------+   |
       |                           ^           |
    FILED                      COVERED_BY      |
       |                           |           |
       v                           |           v
+--------------------------------------------------+
|                      Claim                       |
+--------------------------------------------------+
       |                           |
    INVOLVES                      HAS
       |                           |
       v                           v
+---------------+          +---------------+
|    Vehicle    |          |    Invoice    |
+---------------+          +---------------+
```

---

## 3. Node and Edge Ontology Specifications

### 3.1. Node Types (765 Nodes Total)
| Node Type | Prefix | Description | Properties | Count |
| :--- | :--- | :--- | :--- | :---: |
| **Claim** | `claim:` | Core insurance transaction | `claim_id`, `amount`, `claim_type`, `date`, `fraud_label` | 320 |
| **Claimant** | `claimant:` | Person filing the claim | `claimant_id`, `age`, `city`, `gender` | 120 |
| **Policy** | `policy:` | Contract covering the claim | `policy_id`, `policy_type`, `premium` | 140 |
| **Vehicle** | `vehicle:` | Asset involved in incident | `vehicle_id`, `make`, `model_year` | 130 |
| **Provider** | `provider:` | Repair shop or facility | `provider_id`, `name`, `rating`, `type` | 25 |
| **Invoice** | `invoice:` | Billing documentation | `invoice_id`, `amount` | 220 (approx) |
| **Location** | `location:` | Territory or city node | `location_id`, `city`, `coordinates` | 60 |

### 3.2. Relationship Types (1,770 Edges Total)
| Relationship | Source Node | Target Node | Semantics |
| :--- | :--- | :--- | :--- |
| **FILED** | `Claimant` | `Claim` | Claimant initiated the claim |
| **COVERED_BY** | `Claim` | `Policy` | Policy underwriting the claim |
| **INVOLVES** | `Claim` | `Vehicle` | Vehicle involved in the claim event |
| **ASSIGNED_TO** | `Claim` | `Provider` | Provider repairing or assessing the damage |
| **HAS** | `Claim` | `Invoice` | Billing invoice submitted for the claim |
| **OWNS** | `Claimant` | `Policy` | Ownership of the insurance policy |
| **ISSUED_BY** | `Invoice` | `Provider` | Facility that billed the invoice |
| **LOCATED_AT** | `Provider` | `Location` | Physical location of repair provider |
| **WITHIN_TERRITORY**| `Location` | `Location` | Regional or district containment |
| **OCCURRED_AT** | `Claim` | `Location` | Geographic site of the reported incident |

---

## 4. Graph Feature Extraction

Using **NetworkX**, four primary categories of graph features are extracted for each claim:

1. **Claimant Degree Centrality**:
   - Total number of claims and policies connected to the claimant. High centrality indicates serial filing behavior.
2. **Provider Claim Volume & Centrality**:
   - Total volume of claims funneled through a single repair facility. Highlights high-throughput or collusive providers.
3. **Fraud-Neighbor Ratio**:
   - Percentage of 1-hop and 2-hop neighbor claims that have confirmed ground-truth fraud labels.
   - Formal definition:
     $$\text{Fraud Neighbor Ratio}(c) = \frac{|\{n \in \mathcal{N}(c) \mid \text{fraud\_label}(n) = 1\}|}{|\mathcal{N}(c)|}$$
4. **Local Clustering Coefficient**:
   - Quantifies the degree to which neighboring entities form tightly connected cliques (collusion triangles).

---

## 5. Ego-Subnetwork Extraction for Explainability

When an investigator opens a claim in the dashboard or via the API (`/claims/{claim_id}/graph`), an ego-subnetwork of radius $k=2$ is generated:
- Returns nodes: Claim, Claimant, Provider, Policy, Vehicle, and all connected sibling claims.
- Returns edges: Direct relationships interconnecting the ego network.
- Visualized dynamically in Streamlit using interactive force-directed graph layouts.
