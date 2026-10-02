"""
scripts/viva_part1.py
---------------------
Contains sections 1 to 15 of the Viva Preparation Guide.
"""

from viva_helpers import (
    add_title, add_heading_1, add_heading_2, add_heading_3,
    add_body, add_bullet, add_callout, add_table_data
)

def build_part1(doc):
    # Title & Metadata
    add_title(
        doc,
        "PROJECT VIVA PREPARATION HANDBOOK",
        "Graph-Enhanced Insurance Claim Anomaly and Duplicate Network Detection\nBachelor of Data Science (Semester V) — Academic Year 2026–2027"
    )

    add_callout(
        doc,
        "REMEMBER",
        "Student Name: Aditya Bhardwaj  |  Roll No.: TDDS003A  |  Division: A\n"
        "Programme: Third Year, Bachelor of Data Science (Semester V)\n"
        "Project Guide: Ms. Sweta Suman  |  Department of Data Science\n"
        "Project Title: GRAPH-ENHANCED INSURANCE CLAIM ANOMALY AND DUPLICATE NETWORK DETECTION (FraudShield AI)\n"
        "Deployment Frontend: https://insurance-claimed-detection.vercel.app\n"
        "Backend API: https://fraudshield-api-3j07.onrender.com",
        title="📋 CANDIDATE & PROJECT IDENTIFICATION"
    )

    # =========================================================================
    # SECTION 1: PROJECT AT A GLANCE
    # =========================================================================
    add_heading_1(doc, "SECTION 1 — PROJECT AT A GLANCE (QUICK REVISION)")
    add_body(doc, "Yeh section aapko project ka 360-degree overview deta hai. Viva room mein ghusne se pehle sabse pehle isi table aur speeches ko revise karna hai.")

    glance_headers = ["Dimension", "Actual Implementation Detail in Project"]
    glance_rows = [
        ["Project Title", "Graph-Enhanced Insurance Claim Anomaly and Duplicate Network Detection (FraudShield AI)"],
        ["Domain", "InsurTech, Data Science, Machine Learning, Graph Analytics, Cyber-Forensics"],
        ["Core Problem", "Organized fraud syndicates, invoice recycling, staged collisions aur high investigator false-alarm fatigue."],
        ["Proposed Solution", "Multi-signal fusion engine jo Supervised ML, Unsupervised Anomaly, Text Matching aur Knowledge Graph ko combine karta hai."],
        ["Input Data", "Policy details, Claim amount, Accident date/time, Description text, Provider ID, Vehicle VIN, Invoices."],
        ["Benchmark Dataset", "320 claims (16.25% ground-truth fraud prevalence = 52 frauds, 268 clean claims)."],
        ["Engineered Features", "38 domain-specific features (financial ratios, velocity metrics, temporal intervals, historical aggregates)."],
        ["Supervised Model", "XGBoost Classifier (Primary benchmark) supported by Random Forest, Logistic Regression, HistGradientBoosting."],
        ["Anomaly Detection", "Ensemble of Isolation Forest (100 trees), Local Outlier Factor (k=20), One-Class SVM."],
        ["Duplicate Engine", "Character SequenceMatcher, Token Jaccard similarity, TF-IDF Cosine vector similarity."],
        ["Knowledge Graph", "NetworkX Heterogeneous Bipartite Graph: 1,020 entity nodes, 2,615 relationship edges."],
        ["Composite Risk Formula", "Composite Risk = 0.45*ML + 0.25*Anomaly + 0.15*Duplicate + 0.15*Graph"],
        ["Operational Bands", "CRITICAL (>=0.75), HIGH (0.50-0.75), MEDIUM (0.35-0.50), LOW (<0.35)."],
        ["Verified Precision", "High & Critical bands: 85.19% fraud precision (23 frauds in 27 flagged claims). Low band: 94.17% clean rate."],
        ["Explainability (XAI)", "SHAP (TreeExplainer) local feature contributions + Subgraph neighborhood visualizer."],
        ["Frontend Tech", "React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, SPA architecture on Vercel."],
        ["Backend Tech", "Python 3.11+, FastAPI (Asynchronous REST API, 14 endpoints, OpenAPI 3.1) on Render."],
        ["Database", "Supabase PostgreSQL 15, Supavisor IPv4 Connection Pooler (Port 6543), Row-Level Security, 7 tables."],
        ["Security & Auth", "End-to-End JWT Authentication (HS256), bcrypt password hashing, 5-Role RBAC, Audit Logging."],
        ["Primary Users", "Claims Adjusters (Fast-track clearing) aur Senior SIU Forensic Investigators (Fraud cases)."]
    ]
    add_table_data(doc, glance_headers, glance_rows, col_widths=[2.0, 4.1])

    # Spoken Speeches
    add_heading_2(doc, "1.1 Speeches to Memorize for Opening Question")

    add_heading_3(doc, "🗣️ My Project in 30 Seconds (The Elevator Pitch)")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Good morning Sir/Madam. Mera project ek Graph-Enhanced Insurance Claim Fraud and Duplicate Detection System hai, "
        "jiska naam FraudShield AI hai. Traditional insurance systems isolated tabular rules use karte hain jisse organized collusion aur "
        "recycled invoices pakadna mushkil hota hai. Mere project mein hum 4 layers ko combine karte hain: Supervised XGBoost ML, "
        "Unsupervised Isolation Forest, Multi-metric Duplicate Text Matching, aur NetworkX Knowledge Graph. Ye system claims ko 4 risk bands "
        "mein classify karke SIU investigators ko SHAP explainability ke saath decision-support provide karta hai.”"
    )

    add_heading_3(doc, "🗣️ My Project in 1 Minute")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, insurance industry mein claim fraud ki wajah se companies ko har saal billions ka loss hota hai aur honest policyholders ka "
        "premium badhta hai. Traditional systems static SQL rules use karte hain jo structured syndicates aur shared repair providers ko miss kar dete hain.\n\n"
        "Is problem ko solve karne ke liye maine ek full-stack AI Decision-Support platform banaya hai. Jab koi claim submit hota hai, "
        "hum 38 engineered features calculate karte hain. System concurrently 4 analytical signals run karta hai:\n"
        "1. Supervised XGBoost jo historical fraud patterns detect karta hai.\n"
        "2. Isolation Forest jo novel ya unusual claim behavior ko flag karta hai.\n"
        "3. TF-IDF aur Jaccard similarity jo duplicate descriptions aur recycled invoices pakadti hai.\n"
        "4. NetworkX Knowledge Graph jo 1,020 entities ke network mein collusion aur high-centrality rogue providers ko uncover karta hai.\n\n"
        "Ye chaaro signals ek calibrated composite formula se combine hote hain. High-risk claims mein 85.19% fraud precision milti hai jabki "
        "75% genuine claims low-risk tier mein fast-track settle ho jaate hain.”"
    )

    add_heading_3(doc, "🗣️ My Project in 3 Minutes")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir/Madam, let me explain the complete architecture and methodology of my project in three parts: Problem, Technical Implementation, and Impact.\n\n"
        "1. Problem Context: Traditional fraud detection tabular classification pe depend karti hai, jisme har claim ko independent i.i.d. row maana jaata hai. "
        "Lekin real-world fraud organized syndicates karte hain—jahan ek hi garage multiple claimants ke naam par fake invoices recycle karta hai, "
        "ya staged accidents create karta hai. Normal ML models in relational patterns ko nahi dekh paate.\n\n"
        "2. Technical Architecture: Maine ek decoupled cloud-native platform develop kiya hai:\n"
        "• Frontend: React 18 with TypeScript deployed on Vercel Edge CDN.\n"
        "• Backend: High-performance asynchronous FastAPI microservice deployed on Render.\n"
        "• Database: Supabase PostgreSQL 15 connected via transaction pooler on Port 6543 with 7 normalized tables.\n\n"
        "3. Core Data Science Pipeline:\n"
        "• Hum raw claims data ko clean karke 38 domain features engineer karte hain jaise claim-to-income ratio, policy age, velocity metrics.\n"
        "• Supervised layer mein XGBoost class imbalance handle karte hue fraud probability deta hai.\n"
        "• Anomaly layer mein Isolation Forest novel outliers pakadta hai bina labeled data ke.\n"
        "• Duplicate engine character-level SequenceMatcher aur token-level TF-IDF cosine similarity se recycled bills flag karta hai.\n"
        "• Sabse unique component hamara Bipartite Knowledge Graph hai jisme 1,020 nodes (claims, claimants, policies, vehicles, providers, invoices) "
        "aur 2,615 edges hain. Isme hum Betweenness Centrality aur PageRank se collusion hubs detect karte hain.\n\n"
        "4. Composite Decision-Support: Charo scores ko weight karke hum composite risk banate hain. System automatically claim reject nahi karta, "
        "balki human investigator ko SHAP visual waterfall chart aur interactive graph evidence deta hai jisse SIU team ka investigation time 70% kam ho jaata hai.”"
    )

    add_heading_3(doc, "🗣️ My Project in 5 Minutes (Comprehensive Viva Walkthrough)")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir/Madam, I would like to walk you through the end-to-end journey of my project: Motivation, Architecture, Algorithms, Results, and Practical Deployment.\n\n"
        "[1. MOTIVATION & PROBLEM]: According to IRDAI, roughly 10% to 15% of insurance claims have fraudulent elements. Traditional insurers use manual audit "
        "ya simple SQL rules jaise 'if claim > 1 Lakh flag it'. Modern fraud rings stagger amounts just below thresholds and rotate collusive garages. "
        "Mere project ka objective is problem ko multi-signal machine learning aur graph network topology se solve karna hai.\n\n"
        "[2. DATA PIPELINE & 38 FEATURES]: Benchmark data mein 320 claims hain with 16.25% fraud prevalence. Maine zero data leakage ensure karne ke liye "
        "temporal train-test split use kiya (70% train = 224 claims, 30% test = 96 claims). 38 features banaye gaye, including claim_to_income_ratio, "
        "incident_hour, days_to_policy_expiry, aur repair_to_total_ratio.\n\n"
        "[3. FOUR ANALYTICAL PILLARS]:\n"
        "• Pillar 1: XGBoost Classifier. Humne Logistic Regression, Random Forest aur HistGradientBoosting compare kiye. XGBoost ne highest PR-AUC (0.2348) deliver kiya.\n"
        "• Pillar 2: Unsupervised Anomaly Detection. Isolation Forest (100 estimators) 10% outliers flag karta hai jisme fraud prevalence 18.75% aati hai (1.15x lift).\n"
        "• Pillar 3: Deterministic Duplicate Matching. Jaccard + TF-IDF cosine similarity ne 34 possible duplicate claims identify kiye with a 1.45x fraud concentration.\n"
        "• Pillar 4: NetworkX Graph Analytics. 1,020 nodes aur 2,615 edges mein humne paya ki 153 claims ne 167 invoices share kiye the. Rogue Provider PRV008 ki degree 42 thi, "
        "jo tabular model kabhi detect nahi kar sakta tha.\n\n"
        "[4. COMPOSITE FUSION & STRATIFICATION]:\n"
        "Score = 0.45*ML + 0.25*Anomaly + 0.15*Duplicate + 0.15*Graph. Incoming claims 4 bands mein aate hain. Critical aur High band mein 85.19% precision aayi, "
        "jabki Low risk band mein 94.17% clean rate mili jo 75% claims ko instant fast-track approval deta hai.\n\n"
        "[5. PRODUCTION DEPLOYMENT]: Humne pura full-stack live deploy kiya hai. React 18 frontend Vercel par chal raha hai, FastAPI backend Render par, "
        "aur database Supabase cloud par hai. Pura system audited SIU case management aur SHAP local explainability ke saath operational hai.”"
    )

    # =========================================================================
    # SECTION 2: PROJECT INTRODUCTION
    # =========================================================================
    add_heading_1(doc, "SECTION 2 — PROJECT INTRODUCTION & OBJECTIVES")

    add_heading_2(doc, "2.1 What is the Project?")
    add_callout(
        doc,
        "TECHNICAL EXPLANATION",
        "Graph-Enhanced Insurance Claim Anomaly and Duplicate Network Detection is an enterprise-grade cyber-forensic decision-support system "
        "that integrates multivariate supervised classification, unsupervised anomaly ensembles, pairwise text/numerical similarity engines, "
        "and bipartite knowledge graph topological analytics to assist human SIU (Special Investigation Unit) investigators in detecting complex fraud."
    )
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, mera project ek enterprise-level fraud detection decision-support system hai. Ye insurance companies ke claims officers aur SIU "
        "investigators ko ye batata hai ki incoming claim kitna suspicious hai, usme recycled invoices hain ya nahi, aur kya wo kisi hidden criminal network ya "
        "collusive repair garage se juda hua hai.”"
    )

    add_heading_2(doc, "2.2 What Problem Does It Solve?")
    add_body(doc, "Insurers face three major bottlenecks:", bold_prefix="Key Bottlenecks: ")
    add_bullet(doc, "Scalability failure: Lakhs of claims submit hote hain par SIU team limited hoti hai; manual review impossible hai.")
    add_bullet(doc, "Tabular isolation: Traditional ML models claim ko standalone row maante hain, unhe interconnected entities ka pata nahi chalta.")
    add_bullet(doc, "High false positive fatigue: Naive rules 90% false alarms generate karte hain jisse genuine claims delay hote hain.")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, ye project manual audit ke bottleneck ko solve karta hai. Naive rules bahut saare false positives dete hain jisse genuine customers pareshan hote hain. "
        "Mera system 75% genuine claims ko automatically fast-track clearance ke liye identify karta hai aur high-risk organized fraud rings ko priority queue mein filter karta hai.”"
    )

    add_heading_2(doc, "2.3 Why Did I Select This Project?")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, maine ye project isliye choose kiya kyunki insurance fraud ek complex real-world Data Science problem hai. Yahan tabular classification akeli fail ho jaati hai "
        "kyunki fraudsters coordinated syndicates banate hain. Mujhe ek aisa project karna tha jahan Supervised Learning, Unsupervised Anomaly Detection, NLP Text Matching, "
        "aur Graph Theory—ye chaaro domains ek single enterprise cloud platform mein integrate ho sakein.”"
    )

    add_heading_2(doc, "2.4 Why is Insurance Fraud Detection Important?")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, insurance fraud ki wajah se underwriting losses hote hain, jise balance karne ke liye companies common public ka premium badha deti hain. "
        "Agar hum fraud ko settle hone se pehle detect kar lein, toh claim settlement ratio improve hota hai, honest customers ko kam premium dena padta hai, "
        "aur turnaround time days se minutes mein aa jaata hai.”"
    )

    add_heading_2(doc, "2.5 What is the Role of Data Science in This Project?")
    add_body(doc, "Data Science brings three mathematical competencies:", bold_prefix="Core Competencies: ")
    add_bullet(doc, "Non-linear pattern learning: Tree ensembles non-linear interactions capture karte hain jo simple IF/ELSE rules nahi kar sakte.")
    add_bullet(doc, "Multimodal signal fusion: Numeric ratios, raw textual bills, aur structural graph edges ko calibrated risk score mein convert karna.")
    add_bullet(doc, "Algorithmic explainability: Black-box model ko SHAP game theory values se explainable banana.")

    add_heading_2(doc, "2.6 Who Will Use the System?")
    add_bullet(doc, "Claims Adjuster: Daily claims verify karne ke liye aur low-risk claims ko fast-track approve karne ke liye.")
    add_bullet(doc, "SIU Senior Investigator: High/Critical priority cases ki in-depth forensic inquiry karne ke liye.")
    add_bullet(doc, "SIU Head / Executive: Portfolio-level fraud prevalence aur financial risk metrics monitor karne ke liye.")

    add_heading_2(doc, "2.7 What is the Final Output?")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, final output ek comprehensive forensic claim dossier hai jisme:\n"
        "1. Composite Risk Score (0.0 to 1.0) aur Risk Band (CRITICAL, HIGH, MEDIUM, LOW).\n"
        "2. Four sub-scores: ML Probability, Anomaly Score, Duplicate Score, Graph Topology Score.\n"
        "3. SHAP local feature importance chart jo batata hai ki risk score kin features ki wajah se badha.\n"
        "4. Subgraph network visualization jo shared invoices aur collusive providers show karta hai.\n"
        "5. Complete SIU Case Management workflow for human investigator sign-off.”"
    )

    add_heading_2(doc, "2.8 What Makes This Project Different from a Simple Fraud Classifier?")
    add_callout(
        doc,
        "IMPORTANT",
        "Examiner definitely puchega: 'Kaggle par toh fraud classification ke hazaro models hain, tumne naya kya kiya?'"
    )
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, Kaggle par simple tabular classifier hota hai jo ek row dekh kar 0 ya 1 bol deta hai. Mera project ek multi-signal decision-support platform hai:\n"
        "1. Graph Analytics: Agar fraudster ne feature values normal rakhi hain lekin uska repair provider pehle 5 fraud claims mein involved tha, toh mera graph us collusion ko pakad lega.\n"
        "2. Duplicate Text Engine: Agar damage description ya invoice number pehle kisi aur insurer ke claim se recycle kiya gaya hai, toh NLP text similarity use flag kar degi.\n"
        "3. Unsupervised Detection: Agar zero-day fraud pattern hai jo training data mein tha hi nahi, toh Isolation Forest outlier score badha dega.\n"
        "4. Production Deployment: Ye sirf Jupyter notebook nahi hai, balki live React frontend, FastAPI backend aur PostgreSQL database ke saath deployed system hai.”"
    )

    # =========================================================================
    # SECTION 3: PROBLEM STATEMENT
    # =========================================================================
    add_heading_1(doc, "SECTION 3 — PROBLEM STATEMENT (IN-DEPTH BREAKDOWN)")
    add_body(doc, "Traditional claims handling systems suffer from systemic architectural vulnerabilities:")
    add_bullet(doc, "Isolated Tabular Silos: Traditional relational databases claim ko ek standalone entity ke roop mein store karte hain. Relations jaise shared phone numbers, identical vehicle damage descriptions, aur common garages unmapped rehte hain.")
    add_bullet(doc, "Recycled Invoices & Collusion: Staged collision rings ek hi repair bill ko multiple policies ya alag-alag companies mein submit karte hain.")
    add_bullet(doc, "Black-Box Model Distrust: Standard deep learning ya ensemble models prediction toh de dete hain par ye nahi batate ki claim suspicious kyu hai. Regulatory bodies (IRDAI) bina solid evidence ke claim withhold karne ki permission nahi deti.")
    add_bullet(doc, "Human Fatigue & SLA Penalties: Insurance regulations demand karti hain ki genuine claims 30 din mein settle ho. Investigator har claim ko manually verify karega toh legitimate customers suffer karenge.")

    add_callout(
        doc,
        "EXAMINER MAY ASK",
        "“What exactly is the core problem statement in your project? Tell me in two sentences.”"
    )
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, core problem ye hai ki traditional insurance fraud systems isolated tabular rules use karte hain jo multi-party organized collusion aur recycled invoices ko detect nahi kar paate, "
        "aur high false-alarm rates ki wajah se genuine claims settlement mein delay hota hai. Mera project graph topology aur multi-signal ML se collusion expose karta hai aur automated operational triage provide karta hai.”"
    )

    # =========================================================================
    # SECTION 4: EXISTING SYSTEM VS PROPOSED SYSTEM
    # =========================================================================
    add_heading_1(doc, "SECTION 4 — EXISTING SYSTEM VS PROPOSED SYSTEM")

    comp_headers = ["Evaluation Parameter", "Traditional Existing System", "Proposed System (FraudShield AI)"]
    comp_rows = [
        ["Detection Approach", "Static IF-THEN SQL rules & manual adjusters", "Multi-signal fusion: Supervised + Anomaly + NLP + Graph"],
        ["Entity Relationships", "Isolated rows in SQL tables (No relational link)", "Heterogeneous Bipartite NetworkX Graph (1,020 nodes)"],
        ["Duplicate Detection", "Exact string match on claim ID (easily bypassed)", "SequenceMatcher + Jaccard + TF-IDF Cosine Similarity"],
        ["Novel / Zero-Day Fraud", "Fails completely (rules don't exist yet)", "Flagged by Unsupervised Isolation Forest & LOF"],
        ["Collusion Discovery", "Manual cross-referencing across paper dossiers", "Automated PageRank, Degree & Betweenness Centrality"],
        ["Operational Triage", "Uniform manual processing (Heavy backlogs)", "Automated 4-tier risk banding (75% fast-tracked in Low band)"],
        ["Explainability", "Opaque score or arbitrary rule trigger", "Local SHAP waterfall feature attribution + Subgraph visuals"],
        ["Human Integration", "Adjuster makes final guess under pressure", "Full-featured SIU Case Dossier with audit trail"]
    ]
    add_table_data(doc, comp_headers, comp_rows, col_widths=[1.5, 2.3, 2.3])

    # =========================================================================
    # SECTION 5 & 6: PROPOSED SYSTEM WORKFLOW (12 STEPS)
    # =========================================================================
    add_heading_1(doc, "SECTIONS 5 & 6 — COMPLETE 12-STEP END-TO-END PROJECT WORKFLOW")
    add_body(doc, "Jab user ya insurance officer portal par claim submit karta hai, system step-by-step 12 stages execute karta hai:")

    steps = [
        ("Step 1: Intake & Ingestion", "Claimant ya officer web portal par claim details input karta hai (policy ID, claim amount, vehicle VIN, accident description, incident date/time, provider ID, invoice numbers)."),
        ("Step 2: Schema Validation", "FastAPI Pydantic schemas data validation perform karte hain: positive numeric amounts, valid ISO timestamps, non-empty textual descriptions, aur valid foreign keys."),
        ("Step 3: Data Preprocessing", "Missing numerical values ko median imputation se handle kiya jaata hai; categorical strings ko lower-case aur clean tokenize kiya jaata hai; dates se duration intervals derive hote hain."),
        ("Step 4: Feature Engineering", "Raw data se 38 domain features calculate hote hain: claim_to_income_ratio, days_since_policy_inception, incident_hour, repair_to_total_ratio, etc."),
        ("Step 5: Duplicate Text & Invoice Matching", "Pairwise SequenceMatcher, Token Jaccard overlap, aur TF-IDF vector cosine similarity calculate karke description similarity score generate hota hai."),
        ("Step 6: Supervised ML Inference", "XGBoost classifier 38 features par run hota hai aur fraud probability P(Fraud) calculate karta hai using learned tree split thresholds."),
        ("Step 7: Unsupervised Anomaly Scoring", "Isolation Forest claim ko isolate karne ke liye required tree path length measure karta hai. Short path length = high anomaly score."),
        ("Step 8: Knowledge Graph Topological Inference", "Claim, policyholder, vehicle aur provider ko NetworkX graph mein map kiya jaata hai. Node degree, betweenness centrality aur fraud-neighbor density calculate hoti hai."),
        ("Step 9: Composite Risk Fusion", "Charo analytical signals calibrated weights se multiply hote hain: Risk = 0.45*ML + 0.25*Anomaly + 0.15*Duplicate + 0.15*Graph."),
        ("Step 10: Operational Triage Banding", "Score ke basis par claim 4 bands mein categorize hota hai: CRITICAL (>=0.75), HIGH (0.50-0.75), MEDIUM (0.35-0.50), LOW (<0.35)."),
        ("Step 11: SHAP Local Explainability Generation", "TreeExplainer run karke top risk-increasing aur risk-decreasing features ka waterfall attribution plot generate hota hai."),
        ("Step 12: SIU Case Dossier & Human Sign-off", "High/Critical claims automatically SIU worklist mein add hote hain jahan forensic investigator evidence review karke legal decision leta hai.")
    ]

    for s_title, s_desc in steps:
        add_heading_3(doc, s_title)
        add_body(doc, s_desc)

    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, mere project ka pipeline modular hai: Intake -> Validation -> 38 Feature Extraction -> Parallel execution of ML, Anomaly, Duplicate, and Graph -> "
        "Weighted Risk Score -> 4 Triage Bands -> SHAP Explanation -> SIU Case Dossier. Is pure process mein automated rejection nahi hota, balki investigator ko "
        "decision-support evidence milta hai.”",
        title="🗣️ WORKFLOW EXPLANATION IN VIVA:"
    )

    # =========================================================================
    # SECTION 7: MACHINE LEARNING MODELS
    # =========================================================================
    add_heading_1(doc, "SECTION 7 — MACHINE LEARNING MODELS IN THE PROJECT")
    add_body(doc, "Humne total 7 machine learning aur anomaly algorithms implement aur benchmark kiye hain:")

    models_info = [
        {
            "name": "1. XGBoost (Extreme Gradient Boosting) — Primary Classifier",
            "type": "Supervised Classification Algorithm",
            "input": "38 numerical and encoded tabular features",
            "output": "Fraud probability score P(Fraud) in range [0.0, 1.0]",
            "why": "Handles tabular non-linear interactions exceptionally well, includes L1/L2 regularization to prevent overfitting, and handles class imbalance via scale_pos_weight.",
            "results": "Delivered highest PR-AUC (0.2348) and ROC-AUC (0.5285) on test set (N=96 claims). At 0.50 threshold: TN=66, FP=12, FN=15, TP=3.",
            "viva": "“XGBoost hamara primary supervised model hai. Ye multiple decision trees sequentially build karta hai jahan har naya tree previous trees ki residual errors ko fit karta hai. Humne isko 38 domain features par train kiya hai.”"
        },
        {
            "name": "2. Random Forest Classifier — Benchmark Model",
            "type": "Supervised Bagging Ensemble",
            "input": "38 engineered tabular features",
            "output": "Class probability via ensemble majority vote",
            "why": "Used as an ensemble baseline to compare bagging vs boosting.",
            "results": "PR-AUC = 0.2185, ROC-AUC = 0.5120 on benchmark test set.",
            "viva": "“Random Forest bagging use karta hai jahan multiple decision trees parallel mein train hote hain aur final prediction majority voting se aati hai. Comparison mein XGBoost ne isse behtar PR-AUC score deliver kiya.”"
        },
        {
            "name": "3. Logistic Regression — Linear Baseline",
            "type": "Supervised Generalized Linear Model",
            "input": "StandardScaler normalized 38 features",
            "output": "Log-odds probability via sigmoid link function",
            "why": "Serves as the fundamental linear benchmark required in academic methodology.",
            "results": "PR-AUC = 0.1706, ROC-AUC = 0.4850 on test set.",
            "viva": "“Logistic Regression ek linear baseline hai. Ye non-linear feature interactions capture nahi kar pata isliye iska PR-AUC lowest (0.1706) raha, jo prove karta hai ki insurance fraud mein non-linear models mandatory hain.”"
        },
        {
            "name": "4. HistGradientBoosting Classifier — Fast Gradient Boosting",
            "type": "Supervised Binned Gradient Boosting",
            "input": "38 continuous tabular features",
            "output": "Probability score via integer binned histograms",
            "why": "Evaluates histogram-based splitting for ultra-fast inference.",
            "results": "PR-AUC = 0.2076, ROC-AUC = 0.5015 on test set.",
            "viva": "“HistGradientBoosting continuous features ko 256 discrete bins mein convert karke fast splitting karta hai. Iska PR-AUC 0.2076 tha.”"
        },
        {
            "name": "5. Isolation Forest — Primary Unsupervised Anomaly Model",
            "type": "Unsupervised Tree-Based Outlier Detection",
            "input": "Subset of 7 high-variance numerical ratios",
            "output": "Continuous anomaly score normalized to [0.0, 1.0]",
            "why": "Does not require historical fraud labels; isolates rare anomalies in feature space using fewer random splits.",
            "results": "Flagged 32 claims as outliers (10.0% of population) with an 18.75% fraud concentration rate (1.15x lift over baseline).",
            "viva": "“Isolation Forest unsupervised model hai. Iska basic principle ye hai ki abnormal data points normal points ke mukable feature space mein jaldi isolate ho jaate hain. Short tree path length matlab high anomaly.”"
        },
        {
            "name": "6. Local Outlier Factor (LOF) — Density-Based Anomaly",
            "type": "Unsupervised Density-Based Outlier Model",
            "input": "Standardized numerical feature vectors",
            "output": "Local density ratio compared against k=20 nearest neighbors",
            "why": "Detects claims that reside in low-density regions relative to their immediate peer cluster.",
            "results": "Demonstrated an 84.67% decision agreement rate with Isolation Forest.",
            "viva": "“LOF har point ki local density ko uske 20 nearest neighbors ki density se compare karta hai. Agar kisi claim ki density neighbors se substantially kam hai, toh wo outlier hai.”"
        },
        {
            "name": "7. One-Class Support Vector Machine (OCSVM) — Novelty Detector",
            "type": "Unsupervised Kernel Boundary Novelty Detector",
            "input": "RBF kernel projected feature space",
            "output": "Distance from learned hyperplane enclosing legitimate claims",
            "why": "Constructs a tight decision envelope around nominal claims to flag zero-day claims outside the normal manifold.",
            "results": "Calibrated with nu=0.10 and RBF gamma='scale'.",
            "viva": "“One-Class SVM normal claims ke charo taraf ek non-linear hyperplane boundary create karta hai. Jo claim is boundary ke bahar fall kare wo novelty ya zero-day pattern mana jaata hai.”"
        }
    ]

    for m in models_info:
        add_heading_2(doc, m["name"])
        add_bullet(doc, m["type"], bold_prefix="Algorithm Paradigm: ")
        add_bullet(doc, m["input"], bold_prefix="Input Features: ")
        add_bullet(doc, m["output"], bold_prefix="Model Output: ")
        add_bullet(doc, m["why"], bold_prefix="Why Selected: ")
        add_bullet(doc, m["results"], bold_prefix="Verified Result in Project: ")
        add_callout(doc, "VIVA ANSWER", m["viva"])

    # =========================================================================
    # SECTION 8: SUPERVISED VS UNSUPERVISED LEARNING
    # =========================================================================
    add_heading_1(doc, "SECTION 8 — SUPERVISED VS UNSUPERVISED LEARNING IN FRAUD")
    add_body(doc, "Examiner ka favorite conceptual question: 'Aapne supervised aur unsupervised dono kyu use kiya?'")

    ml_comp_headers = ["Dimension", "Supervised Learning (XGBoost)", "Unsupervised Learning (Isolation Forest)"]
    ml_comp_rows = [
        ["Target Labels", "Requires historical labels (fraud_reported = 1 or 0)", "Zero labels required (learns pure data distribution)"],
        ["What It Learns", "Known historical fraud tricks & patterns", "Statistical deviations & zero-day novel behaviors"],
        ["Strengths", "High precision on established modus operandi", "Catches novel schemes fraudsters haven't tried before"],
        ["Vulnerability", "Blind to brand new fraud schemes", "Higher false alarms on rare but legitimate rich claims"],
        ["Role in Project", "Primary fraud score component (Weight = 0.45)", "Secondary safety net for novel tricks (Weight = 0.25)"]
    ]
    add_table_data(doc, ml_comp_headers, ml_comp_rows, col_widths=[1.5, 2.3, 2.3])

    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, supervised learning historical fraud patterns ko achhe se pehchanta hai, lekin agar fraudster ne koi nayi trick use ki jo training data mein "
        "kabhi thi hi nahi, toh supervised model use 0 score de dega. Yahan unsupervised anomaly detection kaam aata hai: wo dekhta hai ki claim statistically "
        "unusual hai. Dono ko combine karne se known aur unknown dono fraud catch ho jaate hain.”"
    )

    # =========================================================================
    # SECTION 9: XGBOOST DEEP EXPLANATION
    # =========================================================================
    add_heading_1(doc, "SECTION 9 — XGBOOST DEEP MATHEMATICAL EXPLANATION")
    add_body(doc, "XGBoost (Chen & Guestrin, 2016) is a scalable implementation of tree gradient boosting:")
    add_bullet(doc, "Sequential Ensemble: Trees sequentially add hote hain; Tree_t builds on the negative gradient of the loss function of Tree_{t-1}.")
    add_bullet(doc, "Objective Function: Objective = Sum(Loss(y_i, y_hat_i)) + Sum(Omega(Tree_k)), jahan Omega penalize karta hai tree complexity ko (L1 alpha aur L2 lambda weights).")
    add_bullet(doc, "Second-Order Taylor Approximation: Traditional gradient boosting sirf first derivative (gradient g_i) use karta hai. XGBoost first (gradient) aur second (hessian h_i) derivatives dono use karta hai for exact split finding.")
    add_bullet(doc, "scale_pos_weight: Class imbalance handle karne ke liye negative samples / positive samples ratio set kiya jaata hai.")

    add_heading_2(doc, "Why XGBoost over Random Forest and Logistic Regression?")
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, Logistic Regression sirf linear relationships draw kar sakta hai, jabki claim fraud mein complex combinations hote hain (jaise: age < 25 AND claim_amount > 2L AND night_incident). "
        "Random Forest bagging use karta hai jo trees independently banata hai. XGBoost boosting use karta hai jo previous trees ki mistakes par focus karta hai. "
        "Iske alawa XGBoost mein L1 aur L2 regularization built-in hoti hai jo tabular data mein overfitting prevent karti hai.”"
    )

    # =========================================================================
    # SECTION 10: ANOMALY DETECTION DEEP DIVE
    # =========================================================================
    add_heading_1(doc, "SECTION 10 — ANOMALY DETECTION DEEP DIVE")
    add_body(doc, "How does Isolation Forest mathematically work?")
    add_bullet(doc, "Random Partitioning: Isolation tree randomly ek feature select karta hai aur uske min aur max ke beech mein random split cut karta hai.")
    add_bullet(doc, "Path Length Hypothesis: Normal points dense clusters mein hote hain, unhe isolate karne ke liye deeply split karna padta hai (long path length h(x)). Abnormal points isolated space mein hote hain, wo 1 ya 2 cuts mein alag ho jaate hain (short path length).")
    add_bullet(doc, "Anomaly Score Formula: s(x, n) = 2^(- E(h(x)) / c(n)), jahan c(n) average path length of unsuccessful search in BST hai. Agar score close to 1 hai, toh point definitely anomalous hai.")

    # =========================================================================
    # SECTION 11: DUPLICATE DETECTION DEEP DIVE
    # =========================================================================
    add_heading_1(doc, "SECTION 11 — DETERMINISTIC DUPLICATE DETECTION")
    add_body(doc, "Fraudsters often recycle claims across multiple vehicles or insurers. Humne 4 complementary text and numeric matching methods implement kiye hain:")

    add_heading_2(doc, "1. Python difflib SequenceMatcher (Ratcliff-Obershelp)")
    add_body(doc, "Formula: Similarity = 2 * M / (T_A + T_B), jahan M matches hain character sequence mein. Ye typographical variations aur OCR character mistakes capture karta hai.")

    add_heading_2(doc, "2. Jaccard Token Set Similarity")
    add_body(doc, "Formula: J(A, B) = |Tokens(A) ∩ Tokens(B)| / |Tokens(A) ∪ Tokens(B)|. Text ko words mein split karke common vocabulary overlap dekha jaata hai. Order of words matter nahi karta.")

    add_heading_2(doc, "3. TF-IDF + Cosine Similarity")
    add_body(doc, "TF(t, d) = term frequency in document d. IDF(t) = log(N / (1 + df(t))). Rare medical terms ya vehicle parts ko high weight milta hai, generic words ko low. Cosine angle in vector space gives similarity in [0.0, 1.0].")

    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, duplicate detection fraud detection se alag isliye hai kyunki duplicate engine purely syntactic aur lexical similarity dekhta hai—kya ye invoice number "
        "ya accident description pehle kisi claim mein exact ya fuzzy match ho chuka hai? Agar description match > 0.50 hai, toh hamara lift 1.45x increase hota hai.”",
        title="🗣️ DIFFERENCE BETWEEN DUPLICATE & FRAUD IN VIVA:"
    )

    # =========================================================================
    # SECTION 12: GRAPH-BASED FRAUD ANALYSIS
    # =========================================================================
    add_heading_1(doc, "SECTION 12 — GRAPH-BASED FRAUD ANALYSIS (NETWORKX)")
    add_body(doc, "Graph analytics is the central novelty of this project. A graph G = (V, E) represents entities as nodes and relationships as edges:")
    add_bullet(doc, "1,020 Entity Nodes: 320 Claims, 220 Invoices, 140 Policies, 130 Vehicles, 120 Claimants, 65 Locations, 25 Providers.")
    add_bullet(doc, "2,615 Relationship Edges: FILED_BY, ASSOCIATED_WITH_VEHICLE, INVOLVES_PROVIDER, BILLED_UNDER_INVOICE, OCCURRED_AT.")
    add_bullet(doc, "Degree Centrality: Ek node se kitne direct edges connected hain. High degree in a repair garage node indicates high transaction concentration.")
    add_bullet(doc, "Betweenness Centrality: Kitne shortest paths us node ke through pass hote hain. Measures bridge nodes facilitating cross-claimant collusion.")
    add_bullet(doc, "PageRank: Evaluates structural importance based on connections from other influential nodes.")
    add_bullet(doc, "Fraud-Neighbor Ratio: Ek claim ke 2-hop radius mein kitne known fraudulent claims connected hain.")

    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, tabular ML model ko pata nahi chal sakta ki 5 alag-alag claimants ne ek hi fake invoice number reuse kiya hai, ya ek hi garage 'PRV008' "
        "har hafte suspicious claims generate kar raha hai. NetworkX graph mein jaise hi hum edges draw karte hain, collusion clusters visually aur mathematically "
        "high centrality ke roop mein expose ho jaate hain.”"
    )

    # =========================================================================
    # SECTION 13: GRAPH VS NORMAL RELATIONAL DATABASE
    # =========================================================================
    add_heading_1(doc, "SECTION 13 — GRAPH VS RELATIONAL DATABASE (POSTGRESQL)")
    add_callout(
        doc,
        "EXAMINER MAY ASK",
        "“Jab PostgreSQL database already relation store karta hai, toh alag se NetworkX Graph kyu banaya?”"
    )
    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, PostgreSQL structured tabular CRUD operations ke liye best hai—fast indexing, ACID transactions, aur secure storage. "
        "Lekin multi-hop traversal (jaise 3-hop connection between Claimant A -> Vehicle -> Invoice -> Provider -> Claimant B) SQL mein 5 expensive JOINs mangta hai "
        "jo scale par crash ho jaata hai. NetworkX in-memory adjacency list use karta hai jahan graph algorithms jaise Connected Components, PageRank aur Shortest Paths "
        "milliseconds mein compute ho jaate hain. Isliye database persistence ke liye hai aur Graph relational intelligence ke liye.”"
    )

    # =========================================================================
    # SECTION 14: COMPOSITE RISK SCORING
    # =========================================================================
    add_heading_1(doc, "SECTION 14 — COMPOSITE RISK FORMULA & OPERATIONAL BANDS")
    add_body(doc, "The four analytical signals are fused into a single calibrated composite score:", bold_prefix="Mathematical Formula: ")
    add_callout(
        doc,
        "TECHNICAL EXPLANATION",
        "Composite_Risk = (0.45 * S_ML) + (0.25 * S_Anomaly) + (0.15 * S_Duplicate) + (0.15 * S_Graph)\n\n"
        "Weights Explanation:\n"
        "• 0.45 for ML: Supervised model has the highest direct correlation with verified historical labels.\n"
        "• 0.25 for Anomaly: Ensures statistical zero-day outliers contribute meaningful risk elevation.\n"
        "• 0.15 for Duplicate: Heavily flags recycled descriptions and invoice reuse.\n"
        "• 0.15 for Graph: Elevates claims connected to high-degree collusive hubs or rogue garages."
    )

    triage_headers = ["Risk Band", "Score Range", "Pop. Count", "Pop. %", "Actual Fraud Count", "Operational Triage Action"]
    triage_rows = [
        ["CRITICAL", "Score >= 0.75", "1", "0.3%", "1", "Immediate escalation. Mandatory freeze on payment. Priority SIU warrant."],
        ["HIGH", "0.50 <= Score < 0.75", "26", "8.1%", "22", "Priority SIU worklist. Full physical verification and garage audit."],
        ["MEDIUM", "0.35 <= Score < 0.50", "53", "16.6%", "15", "Desk adjuster audit. Supplemental documentation required."],
        ["LOW", "Score < 0.35", "240", "75.0%", "14", "Automated straight-through fast-track settlement (94.17% clean rate)."]
    ]
    add_table_data(doc, triage_headers, triage_rows, col_widths=[1.0, 1.2, 0.7, 0.7, 1.0, 1.8])

    # =========================================================================
    # SECTION 15: EXPLAINABLE AI (SHAP)
    # =========================================================================
    add_heading_1(doc, "SECTION 15 — EXPLAINABLE AI (XAI) VIA SHAP")
    add_body(doc, "Why is XAI mandatory in insurance?")
    add_bullet(doc, "Regulatory compliance: IRDAI guidelines forbid rejecting or withholding claims without justifiable causal rationale.")
    add_bullet(doc, "Investigator trust: Agar model sirf 'Fraud: 0.88' dega toh investigator ko pata nahi chalega kahan inquiry karni hai.")
    add_bullet(doc, "SHAP (Lundberg & Lee, 2017): Shapley Additive exPlanations uses cooperative game theory. Base value E[f(x)] se individual prediction f(x) tak har feature ka positive ya negative push calculate hota hai.")

    add_callout(
        doc,
        "VIVA ANSWER",
        "“Sir, SHAP investigator ko ye batata hai ki prediction kyu aayi. For example, agar kisi claim ka score 0.82 hai, "
        "toh SHAP waterfall chart show karega: base risk 0.16 tha, claim_to_income_ratio ne +0.35 risk badhaya, incident_hour (3 AM) ne +0.20 badhaya, "
        "aur high customer tenure ne -0.08 risk ghataya. Isse investigator ko clear focus area mil jaata hai.”"
    )
