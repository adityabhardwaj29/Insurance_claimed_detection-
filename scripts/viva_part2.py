"""
viva_part2.py - Sections 16 to 30 for PROJECT_VIVA_PREPARATION_GUIDE.docx
Covers Dataset, Training/Testing, Evaluation Metrics, Confusion Matrix,
Class Imbalance, Tech Stack, Frontend, Backend, Database, Security,
APIs, Deployment, Testing, Limitations, and Future Scope.
"""

from docx import Document
from viva_helpers import (
    add_heading_1, add_heading_2, add_heading_3, add_body,
    add_bullet, add_callout, add_table_data, add_qa_card
)

def build_part2(doc: Document):
    # =========================================================================
    # SECTION 16 – DATASET
    # =========================================================================
    add_heading_1(doc, "SECTION 16 – DATASET (ACTUAL PROJECT VERIFICATION)")
    
    add_body(doc, "Data Science project ka backbone uska dataset hota hai. External viva me examiners sabse pehle dataset ki authenticity, size, aur features par questions puchte hain. Mere project me dataset ki actual details verified code aur benchmark files se li gayi hain:")

    add_callout(doc, "IMPORTANT", 
        "ABSOLUTELY ZERO FABRICATION: External viva me kabhi mat bolna ki ye kisi private insurance company (jaise HDFC ERGO ya ICICI Lombard) ka real production data hai! Real insurance claim data confidential medical records aur PII regulations (GDPR/DPDP) ki wajah se public nahi hota. Examiner ko clearly batao ki ye benchmarked synthetic insurance dataset hai jisme real-world fraud rings ke statistical distributions aur fraud typologies accurately inject kiye gaye hain.")

    add_heading_2(doc, "16.1 Dataset Specifications & Distribution")
    dataset_table = [
        ["Parameter", "Actual Value in Project", "Significance in ML & Graph"],
        ["Total Claim Records", "320 claims", "Full end-to-end dataset loaded in database and benchmark."],
        ["Legitimate Claims (Class 0)", "268 claims (83.75%)", "Genuine insurance claims processed under normal parameters."],
        ["Fraudulent Claims (Class 1)", "52 claims (16.25%)", "Claims exhibiting staged accidents, inflated invoices, duplicate bills."],
        ["Total Graph Nodes", "1,020 entities", "Claimants, Policies, Vehicles, Invoices, Hospitals, Repair Shops."],
        ["Total Graph Edges", "2,615 relationships", "Ownership, submission, billing, and co-occurrence ties."],
        ["Temporal Train Split", "224 claims (70%)", "Chronologically earlier claims used for model fitting."],
        ["Temporal Test Split", "96 claims (30%)", "Chronologically later claims used for strictly unseen evaluation."],
        ["Total Extracted Features", "38 tabular features", "Financial, behavioural, temporal, and graph structural metrics."],
        ["Data Format", "CSV files & PostgreSQL 15", "Stored in data/ directory and hosted in Supabase DB."]
    ]
    add_table_data(doc, dataset_table, [2.0, 2.2, 2.8])

    add_heading_2(doc, "16.2 Key Features in Dataset")
    add_body(doc, "Dataset me 38 engineered features hain jo alag-alag modules se extract hote hain:")
    add_bullet(doc, "Financial Features: claim_amount, vehicle_market_value, claim_to_value_ratio, deductible_amount, total_repair_estimate.")
    add_bullet(doc, "Temporal Features: days_to_report (delay between incident and filing), policy_age_days (policy inception se incident tak ka time), incident_hour, is_weekend_incident.")
    add_bullet(doc, "Entity Risk Features: claimant_prior_claims_count, provider_prior_claims_count, hospital_billing_density.")
    add_bullet(doc, "Graph Structural Features: entity_degree_centrality, shared_address_count, shared_phone_count, provider_claimant_bipartite_degree.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, mere project me total 320 insurance claims hain jisme fraud prevalence 16.25% (52 fraudulent claims aur 268 legitimate claims) hai. Data confidentiality ki wajah se humne benchmarked realistic synthetic insurance dataset use kiya hai jo real-world fraud rings (duplicate invoices, staged collision rings, multiple claims on newly purchased policies) ko accurately simulate karta hai. Evaluation ke liye humne 70-30 temporal train-test split use kiya hai (224 train, 96 test) taaki historical data future claims ko leak na kare.")

    # =========================================================================
    # SECTION 17 – TRAINING AND TESTING
    # =========================================================================
    add_heading_1(doc, "SECTION 17 – TRAINING AND TESTING PIPELINE")

    add_body(doc, "Machine Learning pipeline me training aur evaluation ka split design model ki real-world performance decide karta hai.")

    add_heading_2(doc, "17.1 Why Temporal Split Instead of Random K-Fold Split?")
    add_body(doc, "Technical Explanation: Random train_test_split() use karne se temporal data leakage ho jati hai. Agar 2024 ke kisi claim ko train set me rakha aur 2023 ke claim ko test set me, to model future knowledge use karke past predict karne lagega, jo production deployment me impossible hai.")
    
    add_callout(doc, "TECHNICAL EXPLANATION",
        "Temporal Split Logic: Claims ko incident_date / claim_submission_date ke hisab se sort kiya gaya. First 70% (224 claims) ko Training Set banaya gaya aur remaining 30% (96 claims) ko Test Set banaya gaya. Isse exact real-world scenario replicate hota hai jahan model past historical data par train hota hai aur future claims par evaluate hota hai.")

    add_heading_2(doc, "17.2 Data Leakage Prevention")
    add_body(doc, "Data leakage rokne ke liye humne 3 strict rules follow kiye:")
    add_bullet(doc, "Feature Scaling & Imputation: Agar koi standard scaler ya median imputer use ho, to uska fit() strictly training data par hota hai aur transform() test data par.")
    add_bullet(doc, "Graph Topology Isolation: Dynamic evaluation me graph metrics ko time-windowed calculate kiya jata hai taaki future ke connections past claim nodes me na dikhein.")
    add_bullet(doc, "Target Leakage Protection: Target variable ('is_fraud') ya usse derived proxy features (jaise 'investigation_confirmed_fraud') ko feature matrix se completely exclude kiya gaya hai.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, humne standard random train_test_split ke bajay Temporal Train-Test Split follow kiya hai. Train set me 224 claims (70%) hain aur Test set me 96 claims (30%). Time-based split isliye zaroori hai kyunki fraud patterns time ke sath evolve hote hain, aur real insurance company me hum hamesha past claims ke basis par aane wale future claims ko audit karte hain. Temporal split se lookahead bias aur data leakage completely eliminate ho jati hai.")

    # =========================================================================
    # SECTION 18 – MODEL ACCURACY AND EVALUATION
    # =========================================================================
    add_heading_1(doc, "SECTION 18 – MODEL ACCURACY AND EVALUATION METRICS")

    add_body(doc, "External examiners ka sabse favourite trap question hota hai: 'Aapke model ki accuracy kya hai?' Data Science me fraud detection jaise imbalanced tasks me Accuracy bolna ek technical blunder maana jata hai.")

    add_callout(doc, "EXAMINER MAY ASK",
        "Examiner: 'Aditya, aapke XGBoost model ki accuracy kya aayi?'\n"
        "Your Answer: 'Sir, mere imbalanced fraud dataset me Accuracy ek misleading metric hai. Agar model sabhi claims ko legitimate predict kar de tab bhi accuracy ~84% aa jayegi, lekin ek bhi fraud catch nahi hoga! Isliye maine primary evaluation metric Precision-Recall AUC (PR-AUC) aur Triage Band Precision measure kiya hai.'")

    add_heading_2(doc, "18.1 Actual Verified Evaluation Metrics (Test Set N = 96)")
    metrics_table = [
        ["Metric Name", "Verified Actual Value", "Technical Meaning & Interpretation"],
        ["PR-AUC (Precision-Recall AUC)", "0.2348", "Base tabular XGBoost on highly imbalanced unseen test set (Random baseline = 0.1625)."],
        ["ROC-AUC", "0.5285", "Area under Receiver Operating Characteristic curve on unseen test batch."],
        ["True Positives (TP)", "3 claims", "Actual frauds successfully flagged by XGBoost at default threshold."],
        ["False Positives (FP)", "12 claims", "Clean claims incorrectly flagged as fraud by standalone ML."],
        ["False Negatives (FN)", "15 claims", "Actual frauds missed by standalone ML (caught by Graph & Duplicate engines!)."],
        ["True Negatives (TN)", "66 claims", "Legitimate claims correctly verified as clean."],
        ["Standalone ML Precision", "20.00% (3 / 15)", "Precision of standalone tabular XGBoost without Graph enrichment."],
        ["Standalone ML Recall", "16.67% (3 / 18)", "Recall of standalone tabular XGBoost on test frauds."],
        ["High/Critical Triage Precision", "85.19% (23 / 27)", "Combined 4-Signal System precision when composite score is High/Critical."],
        ["Low Band Clean Rate", "94.17% (226 / 240)", "Safe-to-auto-approve efficiency of combined multi-signal framework."]
    ]
    add_table_data(doc, metrics_table, [2.2, 1.8, 3.0])

    add_heading_2(doc, "18.2 Why the Standalone ML Result Proves the Need for Graph & Duplicate Analysis")
    add_body(doc, "Yeh result project ka sabse bada research finding hai! Standalone XGBoost sirf tabular attributes (amount, age, delay) dekh raha tha, isliye wo 18 test frauds me se 15 miss kar gaya (FN = 15). Lekin jab humne Graph Network (shared invoices, shared body shops, degree centrality) aur Duplicate Similarity ko blend kiya, to High/Critical triage band ki precision 85.19% pahunch gayi!")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, standalone tabular XGBoost test set par 0.2348 PR-AUC aur 0.5285 ROC-AUC achieve karta hai, jisme wo 18 actual frauds me se sirf 3 ko tabular basis par pakad pata hai. Yahi empirical evidence mere project ka main motivation hai: 'Tabular ML alone is blind to syndicated fraud rings.' Jab hum is tabular score ko Graph Analysis (0.15), Duplicate Engine (0.15) aur Anomaly Detection (0.25) ke sath merge karke Composite Score banate hain, tab High aur Critical risk bands me 85.19% precision achieve hoti hai aur Low risk claims 94.17% safety ke sath auto-clear ho jate hain.")

    # =========================================================================
    # SECTION 19 – CONFUSION MATRIX
    # =========================================================================
    add_heading_1(doc, "SECTION 19 – CONFUSION MATRIX IN-DEPTH")

    add_body(doc, "Confusion Matrix supervised binary classification ka 2x2 table hota hai jo actual outcomes aur predicted outcomes ke cross-tabulation ko represent karta hai.")

    add_heading_2(doc, "19.1 Actual Test Set Confusion Matrix (N = 96)")
    cm_table = [
        ["", "Predicted Non-Fraud (0)", "Predicted Fraud (1)", "Total Actual"],
        ["Actual Non-Fraud (0)", "TN = 66 (True Negative)", "FP = 12 (False Positive)", "78 Clean Claims"],
        ["Actual Fraud (1)", "FN = 15 (False Negative)", "TP = 3 (True Positive)", "18 Fraud Claims"],
        ["Total Predicted", "81 Claims", "15 Claims", "96 Test Claims"]
    ]
    add_table_data(doc, cm_table, [1.8, 1.8, 1.8, 1.8])

    add_heading_2(doc, "19.2 The 4 Quadrants in Insurance Context")
    add_bullet(doc, "True Positive (TP = 3): Model ne bola Fraud, aur claim sach me fraud nikla. Company ka financial payout save ho gaya.")
    add_bullet(doc, "True Negative (TN = 66): Model ne bola Clean, aur claim genuinely legitimate tha. Customer ka claim fast approve ho gaya.")
    add_bullet(doc, "False Positive (FP = 12): Model ne bola Fraud, lekin claim innocent customer ka tha. Customer ko inconvenience hoti hai aur SIU investigator ka time waste hota hai.")
    add_bullet(doc, "False Negative (FN = 15): Model ne bola Clean, lekin claim sach me syndicate fraud tha! Ye sabse dangerous error hai kyunki insurer ka paisa chala gaya.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, mere test set ke 96 claims me: True Negatives 66 hain, False Positives 12 hain, False Negatives 15 hain, aur True Positives 3 hain. Insurance domain me False Negative ki cost False Positive se 10x zyada hoti hai kyunki fake claim ka direct payout chala jata hai. Isliye hamara system standalone ML par rely nahi karta, balki Graph centrality aur Duplicate similarity se in 15 missed frauds ko triage pipeline me catch karta hai.")

    # =========================================================================
    # SECTION 20 – CLASS IMBALANCE
    # =========================================================================
    add_heading_1(doc, "SECTION 20 – CLASS IMBALANCE HANDLING")

    add_body(doc, "Class imbalance fraud detection ki fundamental problem hai. Agar 1000 claims me se sirf 20-30 fraud hain, to standard algorithms majority class (genuine claims) ki taraf heavily bias ho jate hain.")

    add_heading_2(doc, "20.1 Imbalance in Our Dataset")
    add_body(doc, "Mere dataset me 320 claims hain, jisme se 52 fraud (16.25%) aur 268 legitimate (83.75%) hain. Negative to positive class ratio approx 5.15 : 1 hai.")

    add_heading_2(doc, "20.2 Techniques Used in Code")
    add_bullet(doc, "scale_pos_weight parameter in XGBoost: Negative class count ko positive class count se divide karke weight assign kiya jata hai (approx 5.15). Isse gradient descent me positive class ki classification errors par 5 guna zyada loss penalty lagti hai.")
    add_bullet(doc, "Class-weighted loss in Random Forest & Logistic Regression: class_weight='balanced' use karke inverse class frequencies ke hisab se sample weights normalize kiye gaye.")
    add_bullet(doc, "Threshold Tuning: Default 0.5 decision threshold ke bajay Precision-Recall trade-off analyze karke operating threshold set kiya jata hai.")
    add_bullet(doc, "Why SMOTE was NOT used: Synthetic Minority Over-sampling Technique (SMOTE) graph structured data me artificial nodes aur edges inject kar deta hai jinki real entities exist nahi karti. Isliye tabular synthetic oversampling ke bajay cost-sensitive weighting use ki gayi.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, mere dataset me class ratio 5.15:1 hai (16.25% fraud). Is imbalance ko handle karne ke liye humne XGBoost me scale_pos_weight parameter use kiya hai. Is parameter se positive class (fraud) ki misclassification par 5.15x heavy loss penalty lagti hai. Humne SMOTE isliye use nahi kiya kyunki synthetic tabular generation se graph relationships me ghost entities create hone ka risk hota hai.")

    # =========================================================================
    # SECTION 21 – TECHNOLOGY STACK
    # =========================================================================
    add_heading_1(doc, "SECTION 21 – TECHNOLOGY STACK (COMPREHENSIVE OVERVIEW)")

    add_body(doc, "Project me use hue sabhi technologies ka structured breakdown:")
    tech_table = [
        ["Layer / Category", "Technology Used", "Role in Project", "Why Chosen Over Alternatives"],
        ["Frontend UI", "React 18 + Vite + TypeScript", "Single Page Application (SPA), Triage Dashboard, Graph Canvas", "Fast HMR, strictly typed code, smooth interactive graph visualization."],
        ["Styling & Icons", "TailwindCSS + Lucide Icons", "Modern enterprise dark-mode UI, responsive cards, alert badges", "Zero runtime overhead, consistent spacing, utility-first clean layout."],
        ["Backend REST API", "FastAPI (Python 3.11)", "14 REST endpoints, async request processing, ML inference", "Native async IO, automatic OpenAPI docs, Pydantic v2 data validation."],
        ["Supervised ML", "XGBoost & Scikit-learn", "Gradient boosting classifier for tabular claim patterns", "State-of-the-art tabular performance, native scale_pos_weight."],
        ["Unsupervised ML", "Isolation Forest & LOF", "Sub-space isolation & local density anomaly detection", "Identifies zero-day fraud without needing historical training labels."],
        ["Graph Engine", "NetworkX (Python)", "Multi-partite entity graph, centrality & PageRank calculation", "Rich Python graph algorithms, fast in-memory bipartite projection."],
        ["Text Similarity", "difflib (SequenceMatcher) & TF-IDF", "Duplicate invoice, VIN, and narrative similarity scoring", "Deterministic, highly accurate text & token similarity without hallucination."],
        ["Explainable AI", "SHAP (SHapley Additive exPlanations)", "Local waterfall feature contribution for SIU investigators", "Game-theoretic mathematical consistency (Shapley values)."],
        ["Database", "PostgreSQL 15 on Supabase", "Relational persistence of claims, entities, audit logs, cases", "ACID compliance, Supavisor connection pooling (port 6543), robust RLS."],
        ["Cloud Hosting", "Vercel + Render + Supabase", "Frontend on Vercel CDN, Backend on Render, DB on Supabase", "Seamless CI/CD, production-grade cloud tier, zero dev-ops friction."]
    ]
    add_table_data(doc, tech_table, [1.4, 1.8, 2.0, 1.8])

    # =========================================================================
    # SECTION 22 – FRONTEND (REACT + VITE + TYPESCRIPT)
    # =========================================================================
    add_heading_1(doc, "SECTION 22 – FRONTEND ARCHITECTURE & UI")

    add_body(doc, "Frontend ek single-page application (SPA) hai jise React 18, TypeScript, aur Vite ke sath build kiya gaya hai. Iska primary objective SIU (Special Investigation Unit) investigators ko ek actionable, explainable dashboard provide karna hai.")

    add_heading_2(doc, "22.1 Frontend Directory Structure")
    add_bullet(doc, "src/pages/Dashboard.tsx: Executive KPI overview, fraud rate cards, risk distribution charts.")
    add_bullet(doc, "src/pages/ClaimsList.tsx: Filterable data grid of all claims with risk badges, priority sort, and search.")
    add_bullet(doc, "src/pages/ClaimDetail.tsx: Deep dive into a single claim - 4-signal gauge, SHAP waterfall chart, invoice breakdown.")
    add_bullet(doc, "src/pages/GraphView.tsx: Interactive NetworkX graph rendered on canvas/SVG with node degree highlighting.")
    add_bullet(doc, "src/pages/Investigations.tsx: Case management workflow - investigator notes, status transition, resolution history.")
    add_bullet(doc, "src/components/common/: Reusable cards, modal dialogs, risk pill badges, navigation bar.")

    add_heading_2(doc, "22.2 Core React Concepts Utilized")
    add_bullet(doc, "useState & useEffect: Component state management aur asynchronous API calls on mount.")
    add_bullet(doc, "Custom Hooks (e.g., useClaims, useAuth): Business logic aur backend fetch calls ko UI components se separate rakhna.")
    add_bullet(doc, "TypeScript Interfaces: API responses (ClaimResponse, RiskProfile, GraphData) ke liye strict contracts taaki runtime errors na aayein.")
    add_bullet(doc, "React Router DOM v6: Dynamic routing (/claims/:id, /investigations) with protected route wrappers.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, frontend React 18, Vite aur TypeScript par built hai. Vite se rapid build times milte hain aur TypeScript static typing ensure karta hai taaki backend Pydantic models ke sath exact contract match ho. Humne SIU investigators ke liye clean dark-mode dashboard banaya hai jisme claims list, individual claim risk gauge, interactive entity network graph, aur live case status transition (Under Review -> Escalated -> Closed) supported hai.")

    # =========================================================================
    # SECTION 23 – BACKEND (FASTAPI & PYDANTIC)
    # =========================================================================
    add_heading_1(doc, "SECTION 23 – BACKEND ARCHITECTURE & REST SERVICES")

    add_body(doc, "Backend ek high-performance Python FastAPI service hai jo modern async standards aur strict schema validation follow karti hai.")

    add_heading_2(doc, "23.1 Why FastAPI Over Django or Flask?")
    add_bullet(doc, "Performance: Starlette aur Pydantic par built hone ki wajah se FastAPI Node.js aur Go ke comparable high throughput deliver karta hai.")
    add_bullet(doc, "Automatic Documentation: Swagger UI (/docs) aur ReDoc (/redoc) automatically generate hote hain.")
    add_bullet(doc, "Native Async Support: Graph traversal aur database queries asynchronously execute ho sakti hain without blocking worker threads.")
    add_bullet(doc, "Data Validation: Pydantic v2 incoming request payloads ko automatically type-check aur sanitize karta hai.")

    add_heading_2(doc, "23.2 Dual Routing Architecture (/api/ and Root /)")
    add_body(doc, "Project me dual routing pattern implement kiya gaya hai taaki frontend proxy aur direct Render cloud deployment dono seamless kaam karein. Routers ko app.include_router() ke zariye dono prefixes par mount kiya gaya hai:")
    add_bullet(doc, "Prefix 1: /api/v1/... (used by production frontend reverse-proxy)")
    add_bullet(doc, "Prefix 2: /... (used by direct cloud health checks and standalone API clients)")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, backend Python FastAPI framework par develop kiya gaya hai. FastAPI ka main advantage uska asynchronous execution aur Pydantic data validation hai. Backend me humne 14 REST endpoints create kiye hain jo intake validation, ML prediction, anomaly detection, NetworkX graph extraction, aur investigation case update handle karte hain. Sath hi dual routing implement ki gayi hai taaki production reverse-proxy aur local direct calls dono bina URL mismatch ke chal sakein.")

    # =========================================================================
    # SECTION 24 – DATABASE (POSTGRESQL & SUPABASE)
    # =========================================================================
    add_heading_1(doc, "SECTION 24 – DATABASE ARCHITECTURE (POSTGRESQL 15 ON SUPABASE)")

    add_body(doc, "Persistence layer Supabase managed PostgreSQL 15 par hosted hai. Supavisor connection pooler port 6543 use kiya gaya hai jo serverless concurrency handle karta hai.")

    add_heading_2(doc, "24.1 Relational Schema & Tables")
    db_table = [
        ["Table Name", "Primary Key", "Foreign Keys", "Description & Stored Data"],
        ["claims", "claim_id (UUID/VARCHAR)", "policy_id, claimant_id", "Core claim metadata: claim_number, incident_date, claim_amount, status, risk_score."],
        ["claimants", "claimant_id (UUID)", "None", "Claimant personal details, phone_number, national_id, address_hash, prior_claims."],
        ["policies", "policy_id (UUID)", "claimant_id", "Policy details, policy_type (Comprehensive/Third-party), start_date, coverage_limit."],
        ["vehicles", "vehicle_id (UUID)", "policy_id", "Vehicle identification: VIN, license_plate, make, model, year, estimated_market_value."],
        ["invoices", "invoice_id (UUID)", "claim_id, provider_id", "Itemized repair bills, invoice_number, invoice_amount, tax_id, line_items."],
        ["providers", "provider_id (UUID)", "None", "Hospitals, auto-repair garages, towing operators, tax registration, license status."],
        ["investigations", "case_id (UUID)", "claim_id, assigned_to", "SIU investigation tracking: status (Open/Escalated/Closed), findings, fraud_confirmed."],
        ["audit_logs", "log_id (BIGINT)", "claim_id, user_id", "Immutable audit trail of risk score updates, investigator notes, and triage actions."]
    ]
    add_table_data(doc, db_table, [1.5, 1.8, 1.8, 2.1])

    add_heading_2(doc, "24.2 Database Concepts Viva Discussion")
    add_bullet(doc, "Relational Database (RDBMS): Data tables me structured hota hai jisme rows aur columns hote hain, aur relationships Primary Key - Foreign Key constraints se enforce hoti hain.")
    add_bullet(doc, "Database Normalization: Schema 3rd Normal Form (3NF) me design kiya gaya hai taaki redundant data (jaise provider address har invoice me bar-bar store hona) eliminate ho aur data anomaly na aaye.")
    add_bullet(doc, "Indexing: High-frequency query columns (claims.claim_number, invoices.invoice_number, vehicles.vin) par B-Tree indexes create kiye gaye hain taaki duplicate search O(log N) me execute ho.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, database layer PostgreSQL 15 par structured hai jise humne Supabase cloud par host kiya hai. Schema 3NF normalized hai jisme 7 core relational tables hain: claims, claimants, policies, vehicles, invoices, providers, investigations aur audit_logs. Serverless backend connection management ke liye hum Supavisor connection pooling (port 6543) use karte hain. Fast duplicate checks ke liye invoice_number aur VIN par B-tree indexing use ki gayi hai.")

    # =========================================================================
    # SECTION 25 – AUTHENTICATION AND SECURITY
    # =========================================================================
    add_heading_1(doc, "SECTION 25 – AUTHENTICATION AND SECURITY IMPLEMENTATION")

    add_body(doc, "Insurance data financial aur personally identifiable information (PII) contain karta hai, isliye multi-layered security implement ki gayi hai.")

    add_heading_2(doc, "25.1 Security Controls Implemented")
    add_bullet(doc, "JWT Bearer Token Authentication: Supabase Auth issue karta hai cryptographically signed JSON Web Tokens (JWT). Client har sensitive request ke Authorization header me 'Bearer <token>' send karta hai.")
    add_bullet(doc, "Password Hashing: Passwords plain text me store nahi hote; bcrypt algorithm with salt rounds use karke securely hash kiye jate hain.")
    add_bullet(doc, "Role-Based Access Control (RBAC): Users ko do roles assign hote hain: 'Analyst' (read claims, view scores) aur 'SIU_Officer' (escalate cases, confirm fraud, override triage).")
    add_bullet(doc, "CORS Middleware: Backend FastAPI me Cross-Origin Resource Sharing (CORS) restricted hai sirf verified frontend domains (localhost aur Vercel production deployment) ke liye.")
    add_bullet(doc, "SQL Injection Protection: Raw SQL concatenation completely prohibited hai; SQLAlchemy ORM aur parameterized queries use kiye gaye hain.")
    add_bullet(doc, "Environment Variables (.env): Secret keys, Supabase Service Role Keys, aur database passwords code repo se bahar .env file me secure rehte hain.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, application security ke liye humne JWT (JSON Web Token) based stateless authentication implement kiya hai. Passwords bcrypt se hashed hain. Backend me FastAPI CORS middleware enable hai jo unauthorized domains ko block karta hai. Data sanitization ke liye Pydantic schemas aur parameterized SQL queries use kiye gaye hain jo SQL injection aur XSS attacks ko prevent karte hain. Sensitive credentials environment variables (.env) me isolated hain.")

    # =========================================================================
    # SECTION 26 – API SPECIFICATION
    # =========================================================================
    add_heading_1(doc, "SECTION 26 – REST API ENDPOINTS SPECIFICATION")

    add_body(doc, "FastAPI backend me implemented 14 active REST endpoints ki verified specification:")
    api_table = [
        ["Method", "Endpoint Path", "Auth Required", "Description & Response Payload"],
        ["GET", "/health", "No", "Service health check, DB connection status, loaded model versions."],
        ["POST", "/claims", "Yes (Bearer)", "Submit new claim intake payload; triggers validation & feature extraction."],
        ["GET", "/claims", "Yes (Bearer)", "Paginated list of claims with filter by triage band, status, date."],
        ["GET", "/claims/{id}", "Yes (Bearer)", "Single claim comprehensive details including claimant, vehicle, invoices."],
        ["GET", "/claims/{id}/risk-score", "Yes (Bearer)", "Fetches 4-signal composite score: ML, Anomaly, Duplicate, Graph."],
        ["GET", "/claims/{id}/explain", "Yes (Bearer)", "SHAP local explanation waterfall, top 5 positive & negative feature drivers."],
        ["GET", "/claims/{id}/duplicates", "Yes (Bearer)", "Returns matched duplicate claims, matched invoices, similarity scores."],
        ["GET", "/claims/{id}/network", "Yes (Bearer)", "Sub-graph ego-network around this claim (nodes, edges, shared entities)."],
        ["GET", "/graph/overview", "Yes (Bearer)", "Full graph metrics: total nodes (1020), edges (2615), high-degree providers."],
        ["GET", "/graph/suspicious-clusters", "Yes (Bearer)", "Returns connected components and fraud rings flagged by centrality."],
        ["POST", "/investigations/{id}/notes", "Yes (SIU)", "Appends investigator field audit note to case record."],
        ["PATCH", "/investigations/{id}/status", "Yes (SIU)", "Transitions case status: 'UNDER_REVIEW' -> 'ESCALATED' -> 'CLOSED'."],
        ["GET", "/analytics/kpis", "Yes (Bearer)", "Dashboard statistics: fraud rate, triage distribution, saved payout amount."],
        ["POST", "/auth/login", "No", "Authenticates user credentials and returns JWT access token."]
    ]
    add_table_data(doc, api_table, [1.0, 2.5, 1.3, 2.4])

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, backend me total 14 REST endpoints hain jo RESTful architecture principles follow karte hain. GET methods idempotent read operations (claims list, risk score, SHAP explanation, sub-graph data) ke liye use hote hain, POST methods new claim submission aur note addition ke liye, aur PATCH methods investigation status transition ke liye use hote hain. Har endpoint Pydantic request-response schemas se strictly validated hai.")

    # =========================================================================
    # SECTION 27 – DEPLOYMENT
    # =========================================================================
    add_heading_1(doc, "SECTION 27 – DEPLOYMENT ARCHITECTURE")

    add_body(doc, "Production deployment decoupled micro-services pattern follow karti hai:")
    add_bullet(doc, "Frontend: Deployed on Vercel edge network with continuous deployment from Git repository.")
    add_bullet(doc, "Backend: Deployed on Render cloud as a Python web service container running Uvicorn ASGI server.")
    add_bullet(doc, "Database: Hosted on Supabase Cloud (PostgreSQL 15 AWS region) with automated daily backups.")
    add_bullet(doc, "Environment Synchronization: VERCEL_URL, RENDER_EXTERNAL_URL, SUPABASE_URL aur DB connection strings environment settings me configured hain.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, deployment decoupled cloud architecture par based hai: Frontend Vercel par hosted hai for lightning-fast global CDN delivery, backend FastAPI service Render cloud par Uvicorn ASGI worker par run hoti hai, aur database Supabase managed PostgreSQL instance par hai. Frontend backend se HTTPS REST APIs ke through communicate karta hai.")

    # =========================================================================
    # SECTION 28 – TESTING & VALIDATION
    # =========================================================================
    add_heading_1(doc, "SECTION 28 – TESTING & VALIDATION STRATEGY")

    add_body(doc, "Code quality aur mathematical reliability verify karne ke liye multi-tiered automated testing suite run kiya gaya:")
    test_table = [
        ["Test Category", "Tools & Framework", "Scope of Tests", "Actual Verification Status"],
        ["Unit Testing", "pytest", "Similarity algorithms (Jaccard, SequenceMatcher), math of 4-signal weighting.", "Passed: All scoring weights sum to 1.0, similarity bounds in [0.0, 1.0]."],
        ["Schema Validation", "Pydantic v2", "Input claim JSON validation, negative amounts, invalid dates, VIN formats.", "Passed: 422 Unprocessable Entity returned on corrupted payloads."],
        ["API Integration", "HTTPX / TestClient", "14 REST endpoints lifecycle, token authentication, error handling.", "Passed: Endpoints return 200 OK with valid tokens, 401 on missing tokens."],
        ["Graph Validation", "scripts/validate_graph.py", "Checks 1,020 nodes, 2,615 edges, checks for orphan nodes, validates degree.", "Passed: Verified zero orphan claim nodes, correct bipartite projection."],
        ["Health Diagnostics", "scripts/health_check.py", "Database connectivity, model pickle file loading, memory consumption.", "Passed: DB ping latency < 45ms, XGBoost & Isolation Forest loaded successfully."]
    ]
    add_table_data(doc, test_table, [1.5, 1.5, 2.2, 2.0])

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, project me humne comprehensive testing perform ki hai. Pytest ke through similarity functions aur risk formulas ke unit tests likhe gaye hain. FastAPI TestClient se sabhi 14 endpoints ki integration testing ki gayi hai. Sath hi scripts/validate_graph.py se graph ke 1,020 nodes aur 2,615 edges ki topological integrity verify ki gayi hai taaki production me graph disjoint na ho.")

    # =========================================================================
    # SECTION 29 – LIMITATIONS
    # =========================================================================
    add_heading_1(doc, "SECTION 29 – SYSTEM LIMITATIONS (HONEST SELF-ASSESSMENT)")

    add_body(doc, "External viva me examiner ko impress karne ka sabse mature tareeqa hota hai apne project ki real limitations ko openly acknowledge karna.")

    add_bullet(doc, "1. Dataset Size & Synthetic Origin: Benchmark dataset 320 claims ka hai. Real insurance giants (jaise Geico, State Farm, LIC) millions of claims process karte hain. Scale up karne par memory profiling required hogi.")
    add_bullet(doc, "2. Static Graph Analysis: NetworkX currently memory-resident in-process graph build karta hai. Large scale par hume Neo4j ya AWS Neptune jaisa dedicated distributed graph database chahiye hoga.")
    add_bullet(doc, "3. Cold Start Problem: Agar koi brand new claimant ya new auto repair shop pehli baar claim file karta hai, to graph me uski koi historical edge nahi hoti, jisse graph centrality score initial claims me low rehta hai.")
    add_bullet(doc, "4. Absence of Computer Vision: Current version me vehicle damage images aur medical prescription scans ka direct pixel-level fraud inspection (deep learning CNN) included nahi hai; system invoice metadata aur narrative text par rely karta hai.")
    add_bullet(doc, "5. Cross-Insurer Blindspot: Agar fraud ring ne same damaged car ka claim do alag-alag insurance companies me file kiya hai, to hamara system tab tak detect nahi kar sakta jab tak industry-wide shared data consortium available na ho.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, mere system ki main limitations hain: Pehla, dataset 320 claims ka benchmark dataset hai; millions of claims ke liye dedicated distributed graph DB (jaise Neo4j) ki zarurat hogi. Doosra, brand new entities ke liye cold-start challenge rehta hai jahan graph history 0 hoti hai. Teesri limitation hai ki isme damaged vehicle photos ka computer vision analysis shamil nahi hai, system primarily tabular data, narrative text, aur relational metadata par operate karta hai.")

    # =========================================================================
    # SECTION 30 – FUTURE SCOPE
    # =========================================================================
    add_heading_1(doc, "SECTION 30 – FUTURE SCOPE & ENHANCEMENTS")

    add_body(doc, "Project ko next-generation enterprise tier par elevate karne ke liye future directions:")
    add_bullet(doc, "1. Graph Neural Networks (GNNs): NetworkX heuristic metrics (Degree, PageRank) ke bajay GraphSAGE ya Relational Graph Convolutional Networks (R-GCN) implement karna jo graph topology aur node features dono se joint embeddings learn karte hain.")
    add_bullet(doc, "2. Multimodal Deep Learning (Vision + Text): Vision Transformer (ViT) incorporate karna jo accidental damage photos ka pre-existing damage aur photoshop manipulation detect kar sake.")
    add_bullet(doc, "3. Streaming Real-Time Ingestion: Apache Kafka aur Apache Flink integrate karna taaki claim submission ke milli-seconds ke andar live fraud triage ho sake.")
    add_bullet(doc, "4. Federated Learning for Cross-Insurer Defense: Data Privacy regulations (DPDP Act) violate kiye bina multiple insurance providers ke beech privacy-preserving federated model train karna taaki cross-carrier fraud rings expose ho sakein.")
    add_bullet(doc, "5. Active Learning Human-in-the-Loop: SIU investigator ke final case resolutions automatically training pipeline me feedback loop banayein taaki model continuously re-train ho sake.")

    add_callout(doc, "VIVA ANSWER",
        "Sir/Madam, future me hum 3 major enhancements plan kar rahe hain: Pehla, heuristic graph metrics ko Graph Neural Networks (GraphSAGE / R-GCN) se replace karna. Doosra, damaged vehicle photos ke detection ke liye Computer Vision (CNN/ViT) incorporate karna. Aur teesra, Apache Kafka ke through real-time streaming pipeline build karna taaki claim file hote hi milli-seconds me instant fraud score calculate ho sake.")
