# Research Limitations & Ethical Disclosures

## 1. Academic & Research Integrity Statement

In compliance with the **Global Project Rules**, this platform is designed as an academic prototype and experimental benchmark. The following limitations are explicitly documented to preserve technical transparency:

1. **Synthetic Nature of Data**:
   - The dataset consists of 320 simulated automobile insurance claims generated specifically for research benchmarking.
   - It is **not** real policyholder data, and it is **not** sourced from IBM or external corporate repositories.
   - Ground-truth labels (`fraud_label`) represent synthetic target assignments created to benchmark detection algorithms.

2. **No Claim of Production Deployment**:
   - This platform has not been deployed in an active insurance carrier or underwriting system.
   - Operational KPIs (such as potential savings or recovery rates) are experimental projections based on the synthetic dataset.

3. **No Claim of 100% Detection**:
   - In accordance with statistical learning theory, no claims of 100% precision, 100% recall, or infallible fraud detection are made.
   - Model performance is evaluated using standard probabilistic metrics (PR-AUC, ROC-AUC, F1 score).

4. **No Claim of Untested GNN Superiority**:
   - The platform extracts network topological features using **NetworkX** rather than deep Graph Neural Networks (e.g., GCN, GAT, RGCN).
   - Topological feature enrichment is experimentally demonstrated to enhance tree-based models, but claims of GNN architectural superiority over tabular baselines are not made without dedicated GNN training runs.

---

## 2. Technical & Architectural Limitations

### 2.1. In-Memory Graph Processing
- **Current Approach**: NetworkX builds and analyzes the 765-node heterogeneous graph entirely in volatile system memory.
- **Limitation**: While fast for hundreds or thousands of claims, this approach does not scale to enterprise graphs with tens of millions of entities. Production systems require distributed graph databases such as Neo4j or Amazon Neptune.

### 2.2. Static Hybrid Scoring Weights
- **Current Approach**: Fixed heuristic weights ($w_1 = 0.40, w_2 = 0.20, w_3 = 0.15, w_4 = 0.25$) are used in the hybrid risk engine.
- **Limitation**: The weights are not dynamically optimized per product line or geographical region. A meta-classifier or Bayesian optimizer would be required in production.

### 2.3. Low-Entropy Text Descriptions
- **Current Approach**: Claim descriptions in the synthetic dataset follow template structures ("Claim description N").
- **Limitation**: While adequate for TF-IDF cosine similarity duplicate detection, the low lexical entropy prevents advanced Large Language Model (LLM) narrative analysis or sentiment-based fraud signals.

### 2.4. Cross-Origin Resource Sharing (CORS)
- **Current Approach**: `CORS_ORIGINS` defaults to `*` to allow seamless local development between FastAPI (port 8000) and Streamlit (port 8501).
- **Limitation**: Production deployment must restrict allowed origins to trusted domain names via the `CORS_ORIGINS` environment variable.

---

## 3. Ethical and Responsible AI (RAI) Considerations

- **Protected Demographic Attributes**: Attributes such as `gender` and `marital_status` are present in raw demographic tables. In compliance with fair lending and underwriting ethics, these attributes are strictly excluded from the supervised feature engineering matrix to prevent algorithmic bias and disparate impact.
- **Human-in-the-Loop Safeguards**: The platform is strictly an **investigative decision-support system**. No automated claim rejection or policy cancellation occurs. High-risk claims are placed into an SIU queue for human investigator adjudication.
- **Immutable Historical Labels**: Adjudications by investigators update case tables in SQLite without mutating the ground-truth benchmark label (`claims.fraud_label`).
