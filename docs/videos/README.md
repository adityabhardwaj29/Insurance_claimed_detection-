# System Demonstration & Full Verification Screen Recordings

This folder contains complete, end-to-end screen recordings of both application consoles:

---

## 1. Live Web Application Full Walkthrough (`live_webapp_full_walkthrough.webp`)
**Platform:** [https://insurance-claimed-detection.vercel.app/](https://insurance-claimed-detection.vercel.app/)  
**Duration & Scope:** Comprehensive walkthrough covering 100% of all user pages and workflows:

1. **Enterprise Authentication (`/login`):**
   - Direct officer login using JWT authentication.
2. **Operational Dashboard (`/`):**
   - Real-time KPI summaries: Total Claims, Total Claims Amount ($), Active Investigations, Fraud Detected Count, Claims Volume bar charts, and Risk Distribution breakdown.
3. **Claims Directory (`/claims`):**
   - Dynamic claims sorting, multi-status filters, and risk band indicators.
4. **360° Forensic Claim Dossier (`/claims/{id}`):**
   - Multi-Signal risk score decomposition (XGBoost 40%, Isolation Forest 20%, Duplicate Match 20%, Bipartite Graph 20%).
   - SHAP Explainability waterfall chart highlighting top risk-increasing and risk-mitigating features.
   - Pairwise duplicate claim comparisons and subnetwork syndicate clusters.
5. **Customer 360 & Policyholder Intelligence (`/customers`):**
   - Interactive policyholder card directory.
   - Comprehensive 5-tab Customer 360 modal dossier:
     - `Overview`: Personal, contact, and underwriting profile.
     - `Policies`: Active policy coverage limits, annual premiums, and validity periods.
     - `Claims History`: Chronological claim history with statuses and direct dossier links.
     - `Vehicles`: Insured assets, model years, and VIN identifiers.
     - `Risk & Syndicate Assessment`: Network collusion risk and cumulative loss exposure.
6. **New Claim Intake Workflow (`/claims/new`):**
   - Full 7-Step intake sequence:
     - Step 1: Customer lookup & verified profile selection.
     - Step 2: Policy coverage verification.
     - Step 3: Loss incident details, financial loss breakdown, and vehicle attributes.
     - Step 4: Supporting evidence & document intake.
     - Step 5: Summary review card.
     - Step 6: Multi-Signal fraud pipeline execution with animated live stepper.
     - Step 7: Confirmation Screen displaying generated Claim ID, Status, Risk Band, Recommendation, and one-click navigation links.
7. **SIU Investigation Cases (`/cases`):**
   - Open case management, priority triage, and investigative timelines.
8. **Graph Syndicate Intelligence (`/intelligence`):**
   - Interactive bipartite graph topology, shared entity collusion rings, and network metrics.
9. **Regulatory Audit Trail (`/audit-logs`):**
   - Immutable system activity logs tracking decisions, actor emails, and IP tracking.

---

## 2. Streamlit Forensic Analytics Console (`streamlit_forensic_console_walkthrough.webp`)
**Platform:** Streamlit Forensic Intelligence Console (`http://localhost:8501`)  
**Scope:** Deep-dive exploratory data science and research portal:

1. **Executive Fraud Overview (`/overview`):**
   - High-level KPIs, fraud prevalence rate (16.00%), composite risk score box plots, and Priority SIU Triage Worklist.
2. **Claims Relational Explorer (`/claims`):**
   - Dynamic full-text search, multi-column sorting, and filter recalculation.
3. **SIU Case Pipeline (`/cases`):**
   - Pipeline state distributions (`NEW`, `UNDER_REVIEW`, `ESCALATED`, `CONFIRMED_FRAUD`) and workload balancing.
4. **Duplicate & Staged Claim Analysis (`/duplicates`):**
   - Pairwise cosine similarity distributions, TF-IDF string matching, and recycled VIN detection.
5. **360° Forensic Claim Dossier (`/investigation`):**
   - Component signal radar, local SHAP feature attribution waterfall, and narrative summaries.
6. **Empirical Model Performance (`/model_performance`):**
   - Precision-Recall curves, ROC-AUC (0.5819), confusion matrices, and candidate model benchmarks.
7. **Audit & Monitoring (`/audit_logs`, `/monitoring`):**
   - Event log streams and pipeline artifact readiness checks.
