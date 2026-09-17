# System Reproducibility Guide

## 1. Reproducibility Principles

Every metric, model artifact, graph feature, and risk score in this repository is strictly reproducible via code execution. All stochastic processes (train/test splits, XGBoost training, Isolation Forest scoring) use a pinned seed (`random_state=42`).

---

## 2. Environment Prerequisites

- **Python Version**: Python 3.10, 3.11, 3.12, or 3.13.
- **Operating System**: Windows, macOS, or Linux.
- **Hardware**: Standard commodity CPU (minimum 4 GB RAM, 2 CPU cores). No GPU required.

---

## 3. Step-by-Step Reproduction Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/adityabhardwaj29/Insurance_claimed_detection-.git
cd Insurance_claimed_detection-
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Core Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Execute Full Data and Modeling Pipeline
To reproduce all database tables, feature files, models, graph metrics, and risk scores from scratch:
```bash
python run.py --pipeline
```
This single command executes in sequence:
1. `src/data/relational_builder.py` -> Creates SQLite database (`database/fraud_detection.db`)
2. `src/duplicate/duplicate_detector.py` -> Computes TF-IDF similarity (`data/features/duplicate_features.csv`)
3. `src/features/claim_features.py` -> Computes engineered features (`data/features/claim_features.csv`)
4. `src/models/train.py` -> Trains supervised models and persists best XGBoost (`models/fraud_model/model.joblib`)
5. `src/models/anomaly/train.py` -> Trains Isolation Forest (`models/anomaly_model/isolation_forest.joblib`)
6. `src/graph/build_graph.py` -> Constructs heterogeneous graph (`data/graph/nodes.csv`, `data/graph/edges.csv`)
7. `src/graph/features.py` -> Extracts graph topological features (`data/features/graph_features.csv`)
8. `src/scoring/risk_calculator.py` -> Calculates hybrid risk scores (`data/features/final_risk_scores.csv`)
9. `src/cases/case_manager.py` -> Seeds SIU case investigation queue in SQLite
10. `src/explainability/explainer.py` -> Computes SHAP attributions

### Step 5: Verify Claim Journey
Trace an individual claim end-to-end through all 9 layers:
```bash
python run.py --journey CLM00001
```

### Step 6: Execute Automated Test Suite
Run the 373 unit, integration, and security tests:
```bash
pytest -v
```

### Step 7: Launch Application
Run both FastAPI Backend and Streamlit Dashboard concurrently:
```bash
python run.py --all
```
- **FastAPI Documentation**: `http://localhost:8000/docs`
- **Streamlit Analytics Portal**: `http://localhost:8501`
