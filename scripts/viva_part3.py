"""
viva_part3.py - Sections 31 to 35 for PROJECT_VIVA_PREPARATION_GUIDE.docx
Covers:
- Section 31: 105 Viva Questions across 5 Levels (Basic, Project, ML, Advanced, Trick)
- Section 32: 50 Rapid Fire Questions with 1-3 line answers
- Section 33: 14 "Why Did You Use This?" Questions
- Section 34: 10 "What If?" Scenario Questions
- Section 35: 17 External Examiner Challenge Questions
"""

from docx import Document
from viva_helpers import (
    add_heading_1, add_heading_2, add_heading_3, add_body,
    add_bullet, add_callout, add_table_data, add_qa_card
)

def build_part3(doc: Document):
    # =========================================================================
    # SECTION 31 – MOST IMPORTANT VIVA QUESTIONS (105 QUESTIONS IN 5 LEVELS)
    # =========================================================================
    add_heading_1(doc, "SECTION 31 – MOST IMPORTANT VIVA QUESTIONS (DIVIDED BY DIFFICULTY)")

    add_body(doc, "Ye section aapke external viva ka sabse critical weapon hai. Yahan 105 questions 5 levels me categorized hain. Har question ke 4 structured parts hain: Question, Short Technical Answer, Detailed Answer, aur 'Viva mein bolne ka simple answer'.")

    # -------------------------------------------------------------------------
    # LEVEL 1 – BASIC QUESTIONS (20 Questions)
    # -------------------------------------------------------------------------
    add_heading_2(doc, "LEVEL 1: BASIC LEVEL QUESTIONS (FUNDAMENTALS & DEFINITIONS)")

    l1_questions = [
        ("Q1. What is the title of your project?",
         "Graph-Enhanced Insurance Claim Anomaly and Duplicate Network Detection (FraudShield AI).",
         "The project is an intelligent multi-signal decision support system combining supervised ML, unsupervised anomaly detection, deterministic text similarity, and graph network analysis.",
         "Sir, mere project ka title hai 'Graph-Enhanced Insurance Claim Anomaly and Duplicate Network Detection'. Ye insurance fraud aur syndicate rings ko detect karne ke liye multi-signal platform hai."),

        ("Q2. Why did you choose the insurance domain?",
         "Insurance fraud causes massive financial loss (~10% of total incurred losses) which increases premiums for honest policyholders.",
         "Traditional rule-based checking evaluates claims in isolation and fails to detect organized fraud rings where multiple actors share bills, addresses, and vehicles.",
         "Sir, insurance fraud har saal billions of dollars ka loss create karta hai. Traditional systems isolated claims dekhte hain jabki aajkal organized gangs milkar fraud karte hain. Isliye maine ye problem choose ki."),

        ("Q3. What is Machine Learning in simple terms?",
         "Machine Learning is a subset of AI where systems learn statistical patterns from historical data to make predictions without explicit hardcoded rules.",
         "Instead of writing thousands of if-else conditions, ML algorithms optimize mathematical loss functions over training data to predict outcomes on unseen records.",
         "Sir, Machine Learning ek aisi technology hai jahan computer historical data ke patterns ko observe karke khud seekhta hai, taaki naye aane wale data par accurate predictions kar sake."),

        ("Q4. What is the difference between AI and Data Science?",
         "Data Science is an umbrella field covering data extraction, cleaning, analytics, and modeling, whereas AI focuses on building intelligent agents.",
         "Data Science extracts actionable business insights from structured and unstructured data using statistics, while AI develops autonomous learning models (like ML and Deep Learning).",
         "Sir, Data Science complete data lifecycle (cleaning, feature engineering, analysis) par focus karta hai, jabki AI us data se intelligent decision-making systems create karta hai."),

        ("Q5. What is Supervised Learning?",
         "Supervised learning trains a mathematical model on labeled datasets where both input features (X) and ground truth targets (Y) are provided.",
         "The algorithm computes prediction errors via a loss function and adjusts parameters (weights or tree splits) to minimize prediction error.",
         "Sir, supervised learning me hum algorithm ko input features ke sath-sath correct answer (label) bhi dete hain. Jaise 'ye claim fraud hai ya nahi'."),

        ("Q6. What is Unsupervised Learning?",
         "Unsupervised learning identifies hidden patterns, clusters, or anomalies in data without predefined ground truth labels.",
         "It optimizes structural criteria such as Euclidean distance, density, or isolation tree depth without knowing whether any record is fraudulent.",
         "Sir, unsupervised learning me hamare paas koi target label nahi hota. Model data ke natural distribution ko dekhkar unusual ya anomalous records ko alag karta hai."),

        ("Q7. What is Anomaly Detection?",
         "Anomaly detection is the identification of rare observations, data points, or patterns that deviate significantly from majority normal behavior.",
         "In insurance, anomalies are unusual claim amounts, rare medical procedure codes, or abnormal time intervals that do not conform to expected statistical distributions.",
         "Sir, anomaly detection ka matlab hai normal data distribution se alag hatkar unusual patterns ko identify karna, bina ye jaane ki wo explicitly fraud hain ya nahi."),

        ("Q8. What is Duplicate Detection?",
         "Duplicate detection identifies identical, repeated, or highly similar records (such as identical invoice numbers, vehicle VINs, or narrative texts).",
         "It uses deterministic string and token matching algorithms (like SequenceMatcher and Jaccard similarity) to catch multiple submissions of the same underlying financial loss.",
         "Sir, duplicate detection ka matlab hai check karna ki kahin same bill, same car, ya same accidental damage ka claim dobara to submit nahi kiya gaya."),

        ("Q9. What is a Graph in computer science?",
         "A graph is a non-linear data structure comprising vertices (nodes) that represent entities and edges (links) that represent relationships.",
         "Mathematically denoted as G = (V, E), graphs capture complex topological connectivity that relational tabular structures cannot natively represent.",
         "Sir, graph ek data structure hai jisme points ko 'nodes' (entities jaise claimant, vehicle) kehte hain aur unke beech ke connection ko 'edge' (relationship) kehte hain."),

        ("Q10. What is a Node and what is an Edge?",
         "A Node represents an individual entity, and an Edge represents a directed or undirected connection/relationship between two nodes.",
         "In our project, nodes are Claims, Claimants, Vehicles, and Invoices. Edges are 'FILED_BY', 'INVOLVES_VEHICLE', or 'BILLED_BY'.",
         "Sir, Node ka matlab entity (jaise person ya car) aur Edge ka matlab un dono ke beech ka relation (jaise claimant owns vehicle)."),

        ("Q11. What is an API?",
         "API (Application Programming Interface) is a standardized set of communication protocols that enables two software systems to exchange data.",
         "In modern web architectures, APIs use HTTP methods (GET, POST, etc.) with JSON request-response bodies to connect client frontends with backend processing engines.",
         "Sir, API ek bridge ki tarah hota hai jo frontend UI aur backend server ke beech secure data communication allow karta hai."),

        ("Q12. What is a REST API?",
         "A REST API is an API architectural style adhering to constraints such as statelessness, client-server decoupling, and standard HTTP verbs.",
         "It treats resources as URIs and exchanges representations using standard media formats, predominantly JSON.",
         "Sir, REST API ek stateless communication pattern hai jo standard HTTP methods (GET, POST, PATCH) use karke resources ko manage karta hai."),

        ("Q13. What is a Database?",
         "A database is an organized, persistent electronic collection of structured, semi-structured, or unstructured data managed by a DBMS.",
         "It guarantees ACID properties (Atomicity, Consistency, Isolation, Durability) to ensure reliable transactional data integrity.",
         "Sir, database ek structured storage system hota hai jo claims, users aur policies ke records ko permanently aur securely store karta hai."),

        ("Q14. What is a Primary Key?",
         "A Primary Key is a unique column (or combination of columns) that unambiguously identifies each row in a database table.",
         "Primary key columns are inherently unique and cannot contain NULL values, serving as indexing anchors for relational joins.",
         "Sir, primary key table ka wo unique identifier hota hai jo har record ko alag pehchanta hai, jaise har claim ka unique 'claim_id'."),

        ("Q15. What is a Foreign Key?",
         "A Foreign Key is a table column that references the primary key of another table to establish a relational constraint.",
         "It maintains referential integrity by preventing orphaned records and ensuring that child entities correspond to valid parent records.",
         "Sir, foreign key ek table ko doosri table se link karti hai. Jaise claims table me 'claimant_id' claimants table se connected rehta hai."),

        ("Q16. What is Overfitting in Machine Learning?",
         "Overfitting occurs when a model memorizes noise and sample-specific idiosyncrasies of training data, failing to generalize to unseen test data.",
         "It results in high training accuracy/performance but degraded test accuracy due to excessive model complexity.",
         "Sir, overfitting ka matlab hai ki model ne training data ko ratta maar liya hai, jisse test data par uski performance kharab aati hai."),

        ("Q17. What is Underfitting?",
         "Underfitting occurs when an overly simplistic model fails to capture underlying patterns in training data, exhibiting high bias.",
         "The model performs poorly on both training and testing datasets because its hypothesis space is too constrained.",
         "Sir, underfitting ka matlab hai ki model itna simple hai ki wo training data ke basic patterns ko bhi nahi seekh pa raha."),

        ("Q18. What is Data Cleaning?",
         "Data cleaning is the process of detecting, rectifying, or removing corrupt, incomplete, incorrectly formatted, or duplicate records.",
         "It includes missing value imputation, type casting, outlier sanitization, and categorical normalization prior to training.",
         "Sir, data cleaning me hum missing values fill karte hain, formatting errors thik karte hain aur duplicate entries remove karte hain taaki model clean data par train ho."),

        ("Q19. What is Feature Engineering?",
         "Feature engineering transforms raw input data into mathematically informative variables that enhance predictive performance of ML algorithms.",
         "It leverages domain knowledge to construct derived ratios, temporal differences, frequency aggregates, and interaction terms.",
         "Sir, feature engineering ka matlab raw data se naye useful columns banana, jaise claim amount ko vehicle value se divide karke claim_to_value_ratio nikalna."),

        ("Q20. What is Explainable AI (XAI)?",
         "Explainable AI refers to methods and frameworks that provide human-interpretable explanations of why a machine learning model made a specific prediction.",
         "It demystifies 'black-box' algorithms, enabling regulators, domain experts, and end-users to understand feature attribution and trust predictions.",
         "Sir, Explainable AI aisi techniques hain jo batati hain ki ML model ne koi decision kyu liya. Insurance me investigator ko pata hona chahiye ki claim kyu flag hua.")
    ]

    for q, sa, da, va in l1_questions:
        add_qa_card(doc, q, sa, da, va)

    # -------------------------------------------------------------------------
    # LEVEL 2 – PROJECT SPECIFIC QUESTIONS (25 Questions)
    # -------------------------------------------------------------------------
    add_heading_2(doc, "LEVEL 2: PROJECT SPECIFIC QUESTIONS (SYSTEM & ARCHITECTURE)")

    l2_questions = [
        ("Q21. What enters the system when a new claim is submitted?",
         "A structured JSON payload containing claim incident details, claimant info, vehicle attributes, invoice items, and narrative description.",
         "The payload maps to Pydantic intake schemas with fields like claim_amount, incident_date, vehicle_vin, repair_shop_id, and itemized invoice totals.",
         "Sir, claim submission ke time ek structured JSON payload aata hai jisme accident date, claim amount, car VIN, repair invoice, aur narrative text hota hai."),

        ("Q22. What validation checks are performed on intake?",
         "Syntactic and business logic validations via Pydantic: positive amounts, valid date sequences, alphanumeric VIN checks.",
         "We verify that incident_date <= claim_submission_date, claim_amount > 0, policy is active on the incident date, and required keys are present.",
         "Sir, intake par Pydantic validation hota hai jo check karta hai ki claim amount positive ho, accident date future ki na ho, aur policy accident date par active ho."),

        ("Q23. What are the 4 core detection signals in your system?",
         "Supervised ML (0.45), Anomaly Detection (0.25), Duplicate Similarity (0.15), and Graph Centrality (0.15).",
         "These four normalized signals evaluate isolated tabular patterns, statistical outliers, repeated bills, and syndicated network rings respectively.",
         "Sir, hamare 4 core signals hain: Pehla Tabular ML (45%), doosra Anomaly Detection (25%), teesra Duplicate Detection (15%), aur chautha Graph Network Analysis (15%)."),

        ("Q24. What is the Composite Risk Score formula?",
         "Composite_Score = (0.45 * ML) + (0.25 * Anomaly) + (0.15 * Duplicate) + (0.15 * Graph).",
         "The output is a bounded continuous score between 0.0 and 1.0, which maps directly into 4 operational triage bands.",
         "Sir, composite formula hai: 0.45 * ML + 0.25 * Anomaly + 0.15 * Duplicate + 0.15 * Graph. Sabhi weights milkar 1.0 bante hain aur final score 0 se 1 ke beech aata hai."),

        ("Q25. What are the 4 triage bands and their score ranges?",
         "Low (0.00-0.39), Medium (0.40-0.64), High (0.65-0.84), and Critical (0.85-1.00).",
         "Each band directs the claim into a specific operational path: Auto-approve, Standard Desk Review, SIU Priority Audit, or Immediate Hard Freeze.",
         "Sir, char bands hain: Low (0-0.39) auto-approve ke liye, Medium (0.40-0.64) desk review ke liye, High (0.65-0.84) SIU priority audit ke liye, aur Critical (0.85-1.0) immediate claim freeze ke liye."),

        ("Q26. What was the exact dataset size in your project?",
         "320 insurance claims, 52 fraudulent (16.25%) and 268 legitimate (83.75%).",
         "The dataset includes associated relational tables totaling 1,020 graph nodes and 2,615 topological edges.",
         "Sir, mere dataset me verified 320 claims hain, jisme 52 fraud hain (16.25%) aur 268 legitimate claims hain (83.75%)."),

        ("Q27. Why did you use a temporal train/test split of 224 and 96 claims?",
         "To prevent lookahead data leakage by training on chronologically past claims and testing on future claims.",
         "Chronologically sorting claims ensures 70% (224) are used for training and the remaining 30% (96) represent strictly unseen future operational claims.",
         "Sir, humne 70-30 temporal split use kiya hai. 224 claims past ke train set me hain aur 96 future claims test set me, taaki future data ka past me leakage na ho."),

        ("Q28. What graph metrics did you calculate using NetworkX?",
         "Degree Centrality, PageRank, Betweenness Centrality, and Connected Components.",
         "These metrics quantify how interconnected an entity is, whether it acts as a bridge between disjoint clusters, and identify dense syndicates.",
         "Sir, humne NetworkX se Degree Centrality, PageRank, Betweenness Centrality aur Connected Components calculate kiye hain."),

        ("Q29. What is an ego-network in your claim detail view?",
         "A sub-graph focused on a specific central node (the claim) and all directly connected neighboring entities up to 2 hops away.",
         "It extracts all entities (claimants, vehicles, repair shops, invoices) linked to that claim so an investigator can immediately spot suspicious shared ties.",
         "Sir, ego-network ka matlab hai kisi ek claim ke aas-paas ka 2-hop sub-graph. Isse investigator ko turant dikh jata hai ki ye claim kin-kin suspects se juda hua hai."),

        ("Q30. What text similarity algorithms did you implement for duplicate detection?",
         "Python difflib SequenceMatcher (Ratcliff-Obershelp) and Token Jaccard / TF-IDF Cosine similarity.",
         "Exact string hashing checks invoice numbers and VINs, while SequenceMatcher and Jaccard evaluate narrative descriptions and itemized bill lines.",
         "Sir, humne exact string matching ke sath SequenceMatcher aur Token Jaccard / TF-IDF similarity use kiya hai invoice numbers aur damage narratives ke liye."),

        ("Q31. How does SequenceMatcher work in your duplicate module?",
         "It uses the Ratcliff-Obershelp algorithm to find the longest common contiguous matching subsequence recursively.",
         "Similarity ratio is calculated as 2 * M / (T), where M is matching characters and T is total characters across both strings.",
         "Sir, SequenceMatcher do text strings ke beech longest common matching characters find karta hai aur 0 se 1 ke beech similarity score deta hai."),

        ("Q32. How is Jaccard similarity defined mathematically?",
         "J(A, B) = |A ∩ B| / |A ∪ B|, the size of intersection divided by the size of union of two token sets.",
         "It evaluates word-level overlap in claim descriptions, invariant to token order or minor punctuation differences.",
         "Sir, Jaccard formula hai Intersection divided by Union. Dono texts me common words ko total unique words se divide karte hain."),

        ("Q33. What is TF-IDF and where is it used in your project?",
         "Term Frequency - Inverse Document Frequency; used to vectorize claim accident narratives.",
         "It discounts common filler words (like 'car', 'accident') and highlights rare, discriminative terms (like 'whiplash', 'phantom collision').",
         "Sir, TF-IDF common words ki importance kam karta hai aur rare descriptive words ko high weight deta hai, jisse similar fake narratives pakad me aate hain."),

        ("Q34. What is the difference between duplicate detection and fraud detection?",
         "Duplicate detection flags repeated financial submissions; fraud detection identifies deceptive or anomalous patterns across claims.",
         "A duplicate claim might simply be an accidental double submission by a hospital clerk, whereas fraud implies deliberate organized deception.",
         "Sir, duplicate detection sirf copy-paste ya repeated bills check karta hai, jabki fraud detection intentional deceit aur staged accidents ko identify karta hai."),

        ("Q35. What is SHAP and how is it used in your project?",
         "SHAP (SHapley Additive exPlanations) is a game-theoretic approach that assigns each feature an attribution value for a specific claim prediction.",
         "We generate local waterfall plots showing how features like days_to_report (+0.18) or claim_amount (+0.24) pushed the risk score higher.",
         "Sir, SHAP ek Explainable AI library hai jo batati hai ki kis specific feature (jaise delay ya high claim amount) ne risk score ko kitna badhaya ya ghataya."),

        ("Q36. What database is used and how is it hosted?",
         "PostgreSQL 15 hosted on Supabase Cloud, accessed via Supavisor connection pooler on port 6543.",
         "It stores 7 relational tables with ACID transactions, foreign key constraints, and B-Tree indexes.",
         "Sir, Supabase cloud par hosted PostgreSQL 15 database use kiya hai, jo port 6543 par Supavisor connection pooler ke through safely connect hota hai."),

        ("Q37. What is the role of FastAPI in your backend?",
         "FastAPI serves as the asynchronous RESTful microservice layer handling request routing, data validation, and ML inference orchestration.",
         "It exposes 14 endpoints with automated Swagger documentation and handles concurrent async DB queries efficiently.",
         "Sir, FastAPI hamara high-performance Python backend framework hai jo data validate karta hai, ML models run karta hai, aur 14 REST APIs expose karta hai."),

        ("Q38. Why do you have dual route prefixes in FastAPI?",
         "To seamlessly support both production reverse-proxy routing (/api/v1/...) and direct local/cloud health checks (/...).",
         "Both prefixes route to identical logic, preventing routing 404 errors during deployment transitions on Vercel and Render.",
         "Sir, humne dual routing (/api/ aur /) isliye lagayi hai taaki Vercel frontend proxy aur direct Render server dono bina URL error ke smoothly chalein."),

        ("Q39. What frontend technologies did you use?",
         "React 18 with TypeScript, Vite build tool, TailwindCSS styling, and Lucide icons.",
         "The SPA delivers an executive dashboard, interactive data tables, risk score gauges, and sub-graph entity visualizations.",
         "Sir, frontend React 18, TypeScript aur Vite par banaya gaya hai, with TailwindCSS styling for a clean dark-mode SIU dashboard."),

        ("Q40. How does case management work in your application?",
         "Investigators can open flagged claims, review 4-signal scores, add field notes, and transition status from UNDER_REVIEW to ESCALATED or CLOSED.",
         "Every state change is recorded immutably in the audit_logs table with timestamp and investigator ID.",
         "Sir, investigator dashboard se flagged claim dekh sakta hai, field audit notes add kar sakta hai, aur status ko 'Under Review' se 'Escalated' ya 'Closed' me update kar sakta hai."),

        ("Q41. Can your system auto-approve claims?",
         "Yes, claims scoring in the Low Risk band (0.00 - 0.39) achieve a 94.17% clean rate and are routed for straight-through auto-approval.",
         "This dramatically reduces operational backlog so investigators can focus 100% of their manual time on High and Critical claims.",
         "Sir, bilkul! Low risk band (score < 0.40) ke claims 94.17% clean hote hain, isliye system unhe auto-approve recommend karta hai taaki staff ka time save ho."),

        ("Q42. How does the system prevent an honest customer from being wrongly denied?",
         "The system is strictly a decision support tool; it never issues an automated claim rejection.",
         "Claims flagged as High or Critical are routed to human SIU investigators for manual verification; rejection requires human confirmation.",
         "Sir, hamara system decision support system hai, autonomous judge nahi! High risk claims sirf human investigator ke paas audit ke liye jate hain, system khud reject nahi karta."),

        ("Q43. What is an audit log in your database?",
         "A chronological, append-only record of all actions, status updates, and score overrides performed on a claim.",
         "It ensures full regulatory compliance and non-repudiation for insurance audits and legal court proceedings.",
         "Sir, audit log ek secure table hai jisme har action (kisne score dekha, kisne note likha, kab status change hua) timestamp ke sath record hota hai."),

        ("Q44. Where is your application deployed?",
         "Frontend is deployed on Vercel CDN; Backend FastAPI is hosted on Render cloud; Database is on Supabase.",
         "All three communicate securely over HTTPS with CORS protection and environment variable credential storage.",
         "Sir, frontend Vercel par deployed hai, backend Render cloud par run ho raha hai, aur database Supabase par hosted hai."),

        ("Q45. What happens if the database connection drops?",
         "FastAPI returns HTTP 503 Service Unavailable with a structured JSON error; retry logic attempts reconnection.",
         "The health check endpoint (/health) continuously monitors database ping latency and alerts operations if pool connections fail.",
         "Sir, agar DB disconnect hota hai to backend 503 error return karta hai aur connection pooler automatically reconnect karne ki koshish karta hai.")
    ]

    for q, sa, da, va in l2_questions:
        add_qa_card(doc, q, sa, da, va)

    # -------------------------------------------------------------------------
    # LEVEL 3 – MACHINE LEARNING QUESTIONS (25 Questions)
    # -------------------------------------------------------------------------
    add_heading_2(doc, "LEVEL 3: MACHINE LEARNING & ANOMALY DETECTION QUESTIONS")

    l3_questions = [
        ("Q46. What is XGBoost and what does it stand for?",
         "Extreme Gradient Boosting; an optimized distributed gradient boosting library implementing sequential decision trees.",
         "It minimizes an objective function containing a convex loss function and a regularization term penalizing model complexity.",
         "Sir, XGBoost ka full form Extreme Gradient Boosting hai. Ye decision trees ko sequentially build karta hai jahan har naya tree purane tree ki errors ko correct karta hai."),

        ("Q47. How does Gradient Boosting differ from Random Forest?",
         "Random Forest builds trees in parallel (bagging) to reduce variance; Gradient Boosting builds trees sequentially (boosting) to reduce bias.",
         "Random Forest averages independent tree votes, whereas Gradient Boosting fits each new tree to the pseudo-residuals of the previous ensemble.",
         "Sir, Random Forest me saare trees parallel aur independently bante hain, jabki Gradient Boosting me trees ek ke baad ek bante hain aur previous tree ki mistake ko target karte hain."),

        ("Q48. What is the role of learning rate (eta) in XGBoost?",
         "Learning rate scales the contribution of each newly added tree, preventing the model from overshooting during gradient descent.",
         "Typical values range from 0.01 to 0.1; lower learning rates require more estimators but yield better generalization.",
         "Sir, learning rate ye decide karta hai ki har naye tree ki prediction ko kitni importance deni hai. Chhota learning rate overfitting rokta hai."),

        ("Q49. What is max_depth in tree models?",
         "The maximum allowable depth of any individual decision tree, controlling model capacity and feature interaction level.",
         "In XGBoost, max_depth is typically kept small (3 to 6) to maintain weak learners and prevent memorization of noise.",
         "Sir, max_depth tree ki maximum height limit hoti hai. Agar depth zyada ho to tree complex hokar overfit ho jata hai."),

        ("Q50. How does XGBoost handle missing values natively?",
         "XGBoost learns an optimal default split direction for missing values at each node based on reduction of training loss.",
         "If a sample has a missing feature value, it is automatically routed to the branch that yields the best objective improvement.",
         "Sir, XGBoost missing values ko automatically handle karta hai. Training ke dauran wo khud learn kar leta hai ki missing value ko left branch me bhejna better hai ya right me."),

        ("Q51. What is scale_pos_weight in XGBoost?",
         "A parameter that balances the gradient contributions of positive and negative classes in imbalanced classification tasks.",
         "It is mathematically set to (count(negative samples) / count(positive samples)), which was ~5.15 in our dataset.",
         "Sir, scale_pos_weight imbalanced data me minority fraud class ko heavy weight deta hai taaki algorithm fraud misclassifications par zyada penalty lagaye."),

        ("Q52. What is Isolation Forest and how does it detect anomalies?",
         "An unsupervised ensemble of random isolation trees that isolates anomalies by recursive random feature and value splits.",
         "Because anomalies are rare and statistically distinct, they are isolated close to the root of trees, requiring fewer splits (shorter path lengths).",
         "Sir, Isolation Forest random cuts lagakar data points ko alag karta hai. Anomalies jaldi isolate ho jati hain (short path length), jabki normal points ko isolate karne me zyada splits lagte hain."),

        ("Q53. What is path length in Isolation Forest?",
         "The number of edges an observation traverses from the tree root to an isolating terminal leaf node.",
         "Average path length across all trees is converted into an anomaly score between 0.0 and 1.0 using an exponential normalization formula.",
         "Sir, path length ka matlab hai tree ke top se leaf tak kitne splits lage. Short path length ka matlab observation highly anomalous hai."),

        ("Q54. Why did you use Isolation Forest alongside XGBoost?",
         "XGBoost only detects fraud patterns it has seen in labeled training data; Isolation Forest catches novel, zero-day anomalies.",
         "If fraudsters invent an entirely new fraud scheme, supervised XGBoost may miss it, but Isolation Forest flags it due to its statistical rarity.",
         "Sir, XGBoost sirf wahi fraud pakad sakta hai jo pehle training data me dekha ho. Agar fraud gang koi bilkul nayi trick use kare, to Isolation Forest use unusual pattern ki wajah se pakad leta hai."),

        ("Q55. What is Local Outlier Factor (LOF)?",
         "An unsupervised density-based algorithm that measures the local density deviation of a data point relative to its k-nearest neighbors.",
         "Points with substantially lower local density than their surrounding neighbors are flagged as outliers (LOF score > 1.0).",
         "Sir, LOF har point ki density ko uske neighbors ki density se compare karta hai. Agar koi point apne padosiyo ke mukable akele khada hai, to wo outlier hota hai."),

        ("Q56. What is One-Class SVM?",
         "An unsupervised algorithm that fits a tight hypersphere or separating hyperplane around the majority normal training points in feature space.",
         "Points falling outside this boundary in high-dimensional kernel space are classified as novelty outliers.",
         "Sir, One-Class SVM normal data ke charo taraf ek boundary draw karta hai. Jo data point is boundary ke bahar fall kare wo novelty ya anomaly kehlaata hai."),

        ("Q57. What is Logistic Regression and why is it not sufficient alone?",
         "A linear parametric model that estimates log-odds of a binary outcome using a logistic sigmoid function.",
         "It assumes linear decision boundaries and cannot capture complex non-linear feature interactions or graph topology without manual feature cross-products.",
         "Sir, Logistic Regression ek simple linear model hai. Insurance fraud complex aur non-linear hota hai jise simple straight line se separate nahi kiya ja sakta."),

        ("Q58. What is HistGradientBoostingClassifier?",
         "A Scikit-learn gradient boosting implementation that bins continuous features into 256 integer buckets to accelerate training.",
         "Inspired by LightGBM, it significantly reduces tree split finding complexity from O(N log N) to O(N_bins), handling large tabular datasets efficiently.",
         "Sir, HistGradientBoosting continuous features ko 256 bins me convert karta hai jisse training speed bahut fast ho jati hai aur memory consumption kam hoti hai."),

        ("Q59. What is Precision in fraud detection?",
         "The proportion of claims flagged as fraudulent that were genuinely fraudulent: TP / (TP + FP).",
         "High precision means investigators waste minimal time chasing false leads (innocent policyholders).",
         "Sir, Precision ka matlab: jitne claims model ne fraud bole, unme se sach me kitne fraud nikle. Formula hai TP / (TP + FP)."),

        ("Q60. What is Recall (Sensitivity)?",
         "The proportion of all actual fraudulent claims in the population that the model successfully detected: TP / (TP + FN).",
         "High recall ensures the insurance company minimizes undetected leakage and missed fraudulent payouts.",
         "Sir, Recall ka matlab: total actual frauds me se model ne kitne percent frauds pakad liye. Formula hai TP / (TP + FN)."),

        ("Q61. What is the F1-Score?",
         "The harmonic mean of Precision and Recall: 2 * (Precision * Recall) / (Precision + Recall).",
         "It balances precision and recall into a single metric, heavily penalizing models that sacrifice one for the other.",
         "Sir, F1-Score Precision aur Recall ka harmonic mean hota hai, jo dono metrics ka balanced score deta hai."),

        ("Q62. What is ROC-AUC?",
         "Area Under the Receiver Operating Characteristic curve, plotting True Positive Rate against False Positive Rate across all thresholds.",
         "It measures the probability that a randomly chosen positive instance is ranked higher than a randomly chosen negative instance.",
         "Sir, ROC-AUC batata hai ki model fraud aur non-fraud claims ko kitni achhi tarah rank kar pa raha hai regardless of threshold."),

        ("Q63. What is PR-AUC (Precision-Recall AUC)?",
         "The area under the Precision-Recall curve, plotting precision against recall across operating thresholds.",
         "It is significantly more informative than ROC-AUC in heavily imbalanced domains because it does not include True Negatives in its calculation.",
         "Sir, PR-AUC imbalanced data ka gold standard metric hai kyunki ye large negative class se inflate nahi hota aur directly precision aur recall focus karta hai."),

        ("Q64. Why is high accuracy misleading in fraud detection?",
         "In an imbalanced dataset where 98% of claims are legitimate, a dummy model predicting 'Clean' for all claims achieves 98% accuracy while catching 0% of fraud.",
         "Accuracy masks total model failure on the minority class of interest, making PR-AUC and cost-weighted loss essential.",
         "Sir, agar 100 me se 95 claims clean hain aur model sabhi ko clean bol de, to accuracy 95% aayegi par ek bhi fraud catch nahi hoga. Isliye accuracy misleading hoti hai."),

        ("Q65. What was your verified XGBoost PR-AUC on test data?",
         "0.2348 on the unseen 96-claim test set (random baseline prevalence = 0.1625).",
         "This represents the standalone tabular baseline prior to multi-signal composite fusion.",
         "Sir, mere standalone XGBoost ka verified PR-AUC unseen test data par 0.2348 hai (jabki random baseline 0.1625 tha)."),

        ("Q66. What was your verified XGBoost ROC-AUC?",
         "0.5285 on the test partition.",
         "It confirms that tabular features alone offer limited separability for organized syndicate fraud, proving the necessity of graph network enrichment.",
         "Sir, verified test ROC-AUC 0.5285 hai. Ye proof karta hai ki sirf tabular numbers dekhkar organized fraud gangs ko reliably pakadna mushkil hai."),

        ("Q67. How many True Positives and False Negatives did standalone XGBoost produce?",
         "On 96 test claims: TP = 3, FP = 12, FN = 15, TN = 66.",
         "Out of 18 actual test frauds, standalone tabular ML caught 3 and missed 15 (which were subsequently flagged by graph and duplicate signals).",
         "Sir, 96 test claims me: TP = 3, FP = 12, FN = 15, aur TN = 66 the. Tabular model 18 me se 15 fraud miss kar gaya jise hamare graph aur duplicate module ne capture kiya."),

        ("Q68. What was the precision achieved in High/Critical triage bands by the 4-signal system?",
         "85.19% precision (23 verified frauds out of 27 flagged claims).",
         "This demonstrates that fusing graph, duplicate, anomaly, and ML signals increases precision from 20% to over 85%.",
         "Sir, jab humne 4-signal composite framework use kiya, to High aur Critical triage bands me precision 85.19% achieve hui (27 me se 23 actual fraud the)."),

        ("Q69. What was the clean rate in the Low triage band?",
         "94.17% clean rate (226 verified legitimate claims out of 240 in the low band).",
         "This confirms that claims classified into the low-risk tier can be safely auto-cleared with minimal financial exposure.",
         "Sir, Low risk triage band me clean rate 94.17% tha (240 claims me se 226 bilkul clean the), jo auto-approval ke liye safe hai."),

        ("Q70. What is regularization in XGBoost?",
         "Mathematical penalty terms added to the loss function to penalize large leaf weights and complex tree structures.",
         "reg_alpha (L1 regularization) encourages sparsity; reg_lambda (L2 regularization) shrinks weights smoothly, both reducing overfitting.",
         "Sir, regularization ek penalty term hoti hai jo model ko zaroorat se zyada complex hone aur weights ko abnormally bada karne se rokti hai.")
    ]

    for q, sa, da, va in l3_questions:
        add_qa_card(doc, q, sa, da, va)

    # -------------------------------------------------------------------------
    # LEVEL 4 – ADVANCED QUESTIONS (20 Questions)
    # -------------------------------------------------------------------------
    add_heading_2(doc, "LEVEL 4: ADVANCED LEVEL QUESTIONS (GRAPH, XAI & SCORING)")

    l4_questions = [
        ("Q71. What is Degree Centrality in your graph?",
         "The fraction of total possible nodes in the network directly connected to a specific node: d(v) = deg(v) / (N - 1).",
         "High degree centrality in an auto-repair shop or hospital node indicates it is connected to an unusually high volume of distinct claims.",
         "Sir, Degree Centrality batati hai ki koi entity kitne direct connections rakhti hai. Agar kisi repair garage ka degree bahut high hai to wo multiple claims me billed ho raha hai."),

        ("Q72. What was the highest degree provider in your project graph?",
         "Provider PRV008 with a degree of 42 distinct claim connections.",
         "This provider acts as a massive central billing hub for multiple collusive claimants across several synthetic collision rings.",
         "Sir, mere graph me Provider PRV008 ka degree 42 tha, jo 42 alag-alag claims se directly juda hua suspicious repair hub hai."),

        ("Q73. What is PageRank and how does it apply to insurance fraud?",
         "An iterative link-analysis algorithm that assigns importance scores based on the quality and quantity of incoming links.",
         "Entities connected to known fraudulent claimants or suspicious repair shops inherit high PageRank risk scores through network propagation.",
         "Sir, PageRank ye measure karta hai ki agar aap suspicious ya high-risk logo se jude hain, to unka risk score transfer hokar aapka risk score bhi badha dega."),

        ("Q74. What is Betweenness Centrality?",
         "The fraction of all shortest paths between all pairs of nodes in the network that pass through a specific node.",
         "Nodes with high betweenness act as critical brokers or bridges connecting otherwise separate fraud rings or claimant communities.",
         "Sir, Betweenness Centrality measure karti hai ki koi node alag-alag fraud groups ke beech kitna bada bridge ya middleman hai."),

        ("Q75. What is a Connected Component in graph theory?",
         "A maximal subgraph in which any two vertices are connected to each other by paths, and which is connected to no additional vertices.",
         "In our project, large connected components reveal organized syndicates sharing phone numbers, addresses, and vehicles.",
         "Sir, connected component ka matlab ek isolated network cluster. Agar 10 claimants aur 3 garages ek isolated group banate hain, to wo fraud syndicate ring indicate karta hai."),

        ("Q76. Why is bipartite graph projection useful for insurance claims?",
         "Claims and Providers form a bipartite graph (two disjoint sets of nodes where edges only run between claims and providers).",
         "Projecting this graph onto the claim set creates direct edges between two claims if and only if they share a common provider, exposing co-billing patterns.",
         "Sir, bipartite projection se hum do alag-alag claims ke beech direct link bana sakte hain agar wo dono same hospital ya same car garage use kar rahe hain."),

        ("Q77. What is Shapley Value in Explainable AI?",
         "A concept from cooperative game theory that assigns a unique fair payout (feature importance) to each player based on marginal contribution.",
         "SHAP computes the marginal contribution of feature i across all possible feature subsets S: sum(|S|!(|F|-|S|-1)!/|F|!) * [f(S ∪ {i}) - f(S)].",
         "Sir, Shapley value cooperative game theory ka concept hai jo batata hai ki prediction outcome me har feature ka kitna fair aur mathematically justified contribution hai."),

        ("Q78. What is the difference between Local and Global Feature Importance in SHAP?",
         "Local importance explains why a single specific claim received its risk score; Global importance aggregates contributions across all claims.",
         "An investigator reviewing Claim #104 needs local waterfall attribution, whereas a model validator needs global mean |SHAP| values.",
         "Sir, Local importance ek specific claim ka explanation deti hai, jabki Global importance pure dataset me overall sabse important features batati hai."),

        ("Q79. What does a positive SHAP value mean in your claim explanation?",
         "A positive SHAP value (+phi) indicates that the feature's value pushed the model's prediction higher toward the fraud class.",
         "For example, days_to_report = 45 days having a SHAP value of +0.22 increases the predicted log-odds of fraud.",
         "Sir, positive SHAP value ka matlab hai ki us feature ne risk score ko increase kiya (fraud ki taraf dhakela)."),

        ("Q80. What does a negative SHAP value mean?",
         "A negative SHAP value (-phi) indicates that the feature's value pulled the prediction lower toward the legitimate class.",
         "For example, policy_age_days = 2,100 days having a SHAP value of -0.31 indicates a long-standing loyal policyholder.",
         "Sir, negative SHAP value ka matlab hai ki us feature ne claim ko safe aur clean banaya (risk score kam kiya)."),

        ("Q81. Why is Min-Max normalization essential before composite scoring?",
         "Raw outputs from different models have mismatched scales (e.g., ML produces probabilities [0, 1], LOF produces density ratios [1, 5], graph degree is integer count).",
         "Normalizing all four components to [0.0, 1.0] ensures that specified weights (0.45, 0.25, 0.15, 0.15) reflect true relative influence without scale distortion.",
         "Sir, ML probability 0 se 1 hoti hai jabki graph degree 40 tak ja sakti hai. Dono ko bina scale kiye add karne par degree dominant ho jayegi, isliye Min-Max normalization mandatory hai."),

        ("Q82. How do you prevent data leakage in graph feature engineering?",
         "Graph metrics must be calculated strictly on graph edges timestamped prior to or on the current claim's incident date.",
         "Calculating graph degree using future connections creates lookahead bias where a node appears suspicious before its fraudulent acts occurred.",
         "Sir, graph metrics me time-window lagana padta hai taaki future ke connections past claim ke graph features me leak na ho sakein."),

        ("Q83. What is the Ratcliff-Obershelp algorithm?",
         "A pattern matching algorithm implemented in Python's difflib that finds matching sub-sequences between two character sequences.",
         "It recursively finds the longest common substring, anchors it, and repeats the search on non-matching left and right substrings.",
         "Sir, ye difflib ka algorithm hai jo do text sentences ke beech longest matching parts ko dhund kar accurate similarity ratio nikalta hai."),

        ("Q84. What is the time complexity of pairwise duplicate detection on N claims?",
         "Naive all-pairs comparison has O(N^2) time complexity, which becomes prohibitive as N grows into millions.",
         "We mitigate this in production by indexing on blocking keys (same vehicle make, same city, or shared tax ID) before computing heavy text similarity.",
         "Sir, pairwise matching O(N^2) hoti hai. Isko fast karne ke liye hum pehle indexing ya blocking rules (jaise same city ya same vehicle) lagate hain."),

        ("Q85. What is the difference between Graph Centrality and Graph Community Detection?",
         "Centrality measures the topological prominence of individual nodes; Community detection partitions the graph into dense clusters of tightly knit nodes.",
         "Centrality finds the rogue garage; Community detection finds the entire 15-member staged collision gang.",
         "Sir, centrality ek individual node ki importance batati hai, jabki community detection pure group ya syndicate gang ko identify karti hai."),

        ("Q86. What is a bipartite graph?",
         "A graph whose vertices can be divided into two disjoint and independent sets U and V such that every edge connects a vertex in U to one in V.",
         "In insurance, Set U = Claims and Set V = Providers/Invoices; no claim connects directly to another claim except through a shared entity.",
         "Sir, bipartite graph me do alag sets hote hain (jaise Claims aur Garages). Claims aapas me directly nahi judte, wo garage ke through connect hote hain."),

        ("Q87. What is the difference between Parametric and Non-Parametric models?",
         "Parametric models (like Logistic Regression) assume a fixed mathematical distribution with a fixed number of parameters; Non-parametric models (like Decision Trees) do not.",
         "Tree-based models adapt their complexity dynamically to data size and capture arbitrary boundary shapes without normality assumptions.",
         "Sir, parametric models data ke distribution ka assumption banate hain, jabki non-parametric decision trees bina kisi distribution assumption ke complex boundaries learn kar sakte hain."),

        ("Q88. How does Pydantic v2 achieve fast validation in FastAPI?",
         "Pydantic v2 core logic is rewritten in Rust (pydantic-core), generating optimized compiled validators and deserializers.",
         "It executes type validation up to 10x faster than pure Python validation libraries while maintaining strict type safety.",
         "Sir, Pydantic v2 ka core engine Rust me likha gaya hai, jo validation ko pure Python ke comparison me 5-10 guna fast bana deta hai."),

        ("Q89. What is JWT structure?",
         "A JSON Web Token consists of three base64url-encoded parts separated by dots: Header.Payload.Signature.",
         "Header specifies the algorithm (HS256); Payload contains user claims (sub, role, exp); Signature cryptographically verifies integrity.",
         "Sir, JWT ke 3 parts hote hain: Header (algorithm), Payload (user data & expiry), aur Signature (tamper-proof security check)."),

        ("Q90. Why is stateless authentication beneficial in cloud deployment?",
         "The backend server does not need to store active session objects in memory; any server instance can verify requests by verifying the JWT signature.",
         "This enables horizontal autoscaling across multiple container instances on cloud providers like Render or AWS without session stickiness.",
         "Sir, stateless authentication me server par session save nahi karna padta. Token khud verified hota hai, isliye server asani se scale ho jata hai.")
    ]

    for q, sa, da, va in l4_questions:
        add_qa_card(doc, q, sa, da, va)

    # -------------------------------------------------------------------------
    # LEVEL 5 – TRICK QUESTIONS (15 Questions)
    # -------------------------------------------------------------------------
    add_heading_2(doc, "LEVEL 5: TRICK QUESTIONS & DEFENSE STRATEGY")

    l5_questions = [
        ("Q91. Why didn't you use Deep Learning or Graph Neural Networks (GNN)?",
         "On tabular datasets of 320 claims, Deep Learning models severely overfit; gradient boosted trees consistently outperform neural nets on tabular data.",
         "Research benchmarks (Grinsztajn et al., 2022) prove XGBoost outperforms DL on tabular data, and GNNs require massive graph topologies to converge without vanishing gradients.",
         "Sir, mere dataset me 320 claims hain. Tabular data par itne size me Deep Learning severely overfit ho jata hai. State-of-the-art benchmarks prove karte hain ki tabular data par XGBoost deep learning se superior perform karta hai."),

        ("Q92. Why do you need Graph Analysis if XGBoost already detects fraud?",
         "XGBoost only evaluates isolated tabular features (amounts, dates); it is mathematically blind to relational collusion and shared entities.",
         "A claim may appear completely normal in isolation, but linking it to a body shop connected to 40 other claims reveals syndicate fraud that tabular ML cannot see.",
         "Sir, XGBoost sirf single claim ke numbers dekhta hai. Agar ek fraud gang normal dikhne wale 10 claims alag-alag naam se file kare, to ML fail ho jayega. Graph unke shared garage aur shared bills ko link karke pakadta hai."),

        ("Q93. What if your model gives a False Positive and flags an honest customer?",
         "The system is a decision support tool, not an automated denial engine; flagged claims are routed to human investigators for polite desk verification.",
         "No customer claim is rejected automatically by AI; a human SIU investigator must find corroborating physical evidence before taking action.",
         "Sir, hamara system claim ko reject nahi karta. Agar honest customer flag ho jaye, to wo human investigator ke desk review me jata hai jahan genuine documents dekhkar claim approve kar diya jata hai."),

        ("Q94. Can your system guarantee 100% fraud detection?",
         "No machine learning or statistical system can guarantee 100% accuracy due to irreducible noise (Bayes error rate) and evolving fraud tactics.",
         "Our goal is risk prioritization: surfacing the highest probability cases to increase SIU investigator efficiency from 20% to 85%.",
         "Sir, real world me 100% guarantee impossible hai kyunki fraudsters nayi techniques invent karte rehte hain. Hamara goal investigator ki efficiency 20% se badhakar 85% karna hai."),

        ("Q95. Is your dataset real or synthetic, and why?",
         "It is a benchmarked synthetic insurance dataset with realistically injected fraud syndicates, preserving statistical validity without violating PII privacy laws.",
         "Real insurer datasets are strictly proprietary, confidential, and legally protected by DPDP/GDPR regulations and HIPAA medical privacy.",
         "Sir, maine real insurance data confidential medical records aur privacy laws ki wajah se use nahi kiya. Ye benchmarked synthetic dataset hai jisme real fraud syndicates accurately simulate kiye gaye hain."),

        ("Q96. Why is your standalone XGBoost ROC-AUC only 0.5285 on the test set?",
         "Because tabular attributes alone contain almost no discriminative signal for organized syndicate fraud, proving the central thesis of our research.",
         "The syndicate claims had normal amounts and believable narratives; their fraudulent nature existed exclusively in the network connections and duplicate bills.",
         "Sir, ye hamare project ka sabse bada finding hai! Fraud ring itni smart thi ki unke claim amounts aur dates bilkul normal the. Isliye tabular ML confuse ho gaya, aur graph analysis ne unhe expose kiya."),

        ("Q97. Why did you choose the weights 0.45, 0.25, 0.15, 0.15 in your composite formula?",
         "They reflect empirical signal reliability: supervised ML provides primary tabular risk, anomaly covers unseen outliers, and duplicate/graph detect syndicate collusion.",
         "Weights were calibrated to maximize precision in the top two triage tiers while maintaining high clean rates in the auto-approval band.",
         "Sir, supervised ML historical patterns capture karta hai isliye 45% weight diya. Anomaly zero-day risk cover karti hai (25%), aur Duplicate tatha Graph syndicate ties pakadte hain (15% each). Sab milkar 100% bante hain."),

        ("Q98. What happens if a brand new claimant submits a claim with no graph history?",
         "The graph degree score is 0.0, but the other three signals (supervised ML tabular risk, anomaly score, and invoice duplicate checks) evaluate the claim normally.",
         "The system gracefully handles cold-start entities through its multi-signal fallback architecture.",
         "Sir, agar new claimant hai to graph score 0 hoga, lekin baki 3 modules (ML, Anomaly, Duplicate) us claim ko accurately check karenge. Multi-signal system hone ki wajah se single point of failure nahi hota."),

        ("Q99. What if an investigator disagrees with the AI risk score?",
         "The investigator has full authority to override the AI recommendation, and their reason is logged in the immutable audit trail.",
         "Human judgment always supersedes the model, and override data serves as valuable ground truth for future model retraining.",
         "Sir, investigator ke paas full rights hain AI prediction ko override karne ke. Wo apna reason note me likh kar status change kar sakta hai, jo audit log me save ho jata hai."),

        ("Q100. Why did you use NetworkX instead of a graph database like Neo4j?",
         "For our 1,020-node benchmark dataset, NetworkX runs entirely in Python memory with microsecond execution latency and zero external DB overhead.",
         "Neo4j is an enterprise persistence graph database suited for millions of nodes; for our research prototype, NetworkX integrated seamlessly with Scikit-learn.",
         "Sir, 1,020 nodes ke liye NetworkX in-memory Python library bahut fast hai aur zero infrastructure overhead deti hai. Production scale me millions of nodes ke liye hum Neo4j me migrate kar sakte hain."),

        ("Q101. What is the biggest weakness of your project?",
         "The lack of multimodal image verification for damaged vehicles and reliance on an in-memory graph structure.",
         "Fraudsters can still submit fabricated photographs of car damage from the internet because our system evaluates metadata, not pixel data.",
         "Sir, sabse badi limitation ye hai ki isme car damage ki photos ka computer vision verification shamil nahi hai, system text aur relational metadata par rely karta hai."),

        ("Q102. Can a fraudster bypass your duplicate detection by changing a few words in the invoice?",
         "No, because Token Jaccard and TF-IDF Cosine similarity measure semantic and token overlap, not exact character matches.",
         "Changing a few words leaves the majority of high-IDF terms intact, keeping the similarity score above the detection threshold.",
         "Sir, nahi bypass kar sakta! Hum exact matching ke sath TF-IDF aur Jaccard similarity use karte hain, isliye 2-3 words badalne par bhi overall token match pakad me aa jata hai."),

        ("Q103. Why did you use SQLite or Supabase instead of MongoDB?",
         "Insurance claim data is inherently relational with strict foreign key constraints between policies, claimants, vehicles, and line-item invoices.",
         "Relational SQL enforces schema integrity and ACID transactions, whereas NoSQL document stores risk data inconsistency across claims.",
         "Sir, insurance data strictly relational hota hai jahan claim, policy aur vehicle ka strict relationship hota hai. PostgreSQL ACID properties aur foreign key integrity guarantee karta hai."),

        ("Q104. What if two identical accidents happen at the exact same location genuinely?",
         "The system checks multiple independent attributes: claimant IDs, vehicle VINs, policy inception dates, and insurance history.",
         "High narrative similarity will trigger a duplicate check, but low graph centrality and clean ML features will keep the composite score in the desk review band, not auto-rejection.",
         "Sir, agar genuine incident ho to location match hone par bhi VIN aur claimant clean honge, jisse composite score medium band me aayega aur investigator desk review karke clear kar dega."),

        ("Q105. If you had 6 more months, what single feature would you add?",
         "I would implement a Graph Neural Network (GraphSAGE) combined with a Computer Vision model for vehicle damage photos.",
         "This would create a truly multimodal end-to-end fraud intelligence platform processing tabular, network, and visual evidence jointly.",
         "Sir, agar mujhe 6 months milein to mai vehicle damage photos ke liye Computer Vision (CNN) aur heuristic graph ki jagah Graph Neural Networks (GraphSAGE) add karunga.")
    ]

    for q, sa, da, va in l5_questions:
        add_qa_card(doc, q, sa, da, va)

    # =========================================================================
    # SECTION 32 – RAPID FIRE QUESTIONS (50 QUESTIONS)
    # =========================================================================
    add_heading_1(doc, "SECTION 32 – RAPID FIRE QUESTIONS (50 CONCISE FLASHCARDS)")

    add_body(doc, "External viva me jab examiner speed se quick 1-line definitions puchta hai, to ye 50 rapid-fire answers direct bolne hain:")

    rf_data = [
        ["No.", "Rapid Fire Question", "1-Line Spoken Answer (Hinglish)"],
        ["1", "What is XGBoost?", "Extreme Gradient Boosting - sequential decision trees jo previous errors ko minimize karte hain."],
        ["2", "What is Overfitting?", "Jab model training data ratta maar leta hai aur unseen test data par fail ho jata hai."],
        ["3", "What is Underfitting?", "Jab model itna simple hota hai ki wo training data ke basic patterns bhi nahi seekh pata."],
        ["4", "What is Precision?", "Flag kiye gaye total claims me se kitne claims sach me fraudulent nikle (TP / (TP + FP))."],
        ["5", "What is Recall?", "Total actual fraud claims me se model ne kitne percent frauds successfully pakad liye."],
        ["6", "What is F1-Score?", "Precision aur Recall ka balanced harmonic mean."],
        ["7", "What is a Node?", "Graph me kisi individual entity (jaise Claimant, Vehicle, ya Invoice) ka representation."],
        ["8", "What is an Edge?", "Graph me do nodes ke beech ka relationship ya link (jaise 'owns', 'billed_by')."],
        ["9", "What is Degree Centrality?", "Kisi node ke direct connections ki sankhya divided by total possible connections."],
        ["10", "What is PageRank?", "Iterative algorithm jo incoming links ki quantity aur quality ke basis par node importance batata hai."],
        ["11", "What is Betweenness Centrality?", "Ye measure karta hai ki koi node alag-alag groups ke beech kitna bada bridge hai."],
        ["12", "What is Connected Component?", "Graph ka ek aisa sub-network jisme sabhi nodes aapas me internally connected hote hain."],
        ["13", "What is Isolation Forest?", "Unsupervised algorithm jo random splits lagakar rare anomalies ko quickly isolate karta hai."],
        ["14", "What is Path Length?", "Isolation tree me root se leaf tak kisi observation ko isolate karne me lage splits ka count."],
        ["15", "What is Local Outlier Factor?", "Density-based outlier detection jo point ko uske k-neighbors ki density se compare karta hai."],
        ["16", "What is One-Class SVM?", "Normal training data ke charo taraf boundary banakar outliers ko separate karne wala model."],
        ["17", "What is SHAP?", "Shapley Additive exPlanations - game theory based Explainable AI framework."],
        ["18", "What is Shapley Value?", "Prediction outcome me kisi individual feature ka fair mathematical contribution."],
        ["19", "What is SequenceMatcher?", "Python difflib ka algorithm jo longest matching contiguous text sequences find karta hai."],
        ["20", "What is Jaccard Similarity?", "Size of Intersection divided by Size of Union of two token sets."],
        ["21", "What is TF-IDF?", "Term Frequency - Inverse Document Frequency jo common words ko downweight karta hai."],
        ["22", "What is Cosine Similarity?", "Do vectors ke beech ka angle cosine, jo unki directional similarity measure karta hai."],
        ["23", "What is FastAPI?", "High-performance, async Python web framework jo Pydantic data validation use karta hai."],
        ["24", "What is Pydantic?", "Python me data parsing aur type validation library jo strict schemas enforce karti hai."],
        ["25", "What is REST API?", "Stateless client-server architecture jo standard HTTP methods use karti hai."],
        ["26", "What is PostgreSQL?", "Advanced, open-source object-relational database jo ACID properties guarantee karta hai."],
        ["27", "What is Supabase?", "Open-source Firebase alternative jo managed PostgreSQL, Auth, aur Storage provide karta hai."],
        ["28", "What is Supavisor?", "Supabase ka scalable connection pooler jo port 6543 par serverless connections handle karta hai."],
        ["29", "What is JWT?", "JSON Web Token - securely signed token jo stateless authentication ke liye use hota hai."],
        ["30", "What is React?", "Meta dwara banayi gayi component-based JavaScript library for building user interfaces."],
        ["31", "What is Vite?", "Next-generation frontend build tool jo ultra-fast development server (HMR) provide karta hai."],
        ["32", "What is TypeScript?", "JavaScript ka statically typed superset jo compile-time par errors pakadta hai."],
        ["33", "What is TailwindCSS?", "Utility-first CSS framework jo fast aur modern UI styling allow karta hai."],
        ["34", "What is NetworkX?", "Python library for the creation, manipulation, and study of complex graph networks."],
        ["35", "What is PR-AUC?", "Precision-Recall curve ka area, jo imbalanced datasets me ROC-AUC se zyada reliable hota hai."],
        ["36", "What is ROC-AUC?", "True Positive Rate vs False Positive Rate curve ka area across all decision thresholds."],
        ["37", "What is True Positive?", "Actual fraud claim jise model ne correctly fraud classify kiya."],
        ["38", "What is False Positive?", "Clean legitimate claim jise model ne galti se fraud flag kar diya."],
        ["39", "What is False Negative?", "Actual fraud claim jise model miss kar gaya aur clean bol diya (highest risk)."],
        ["40", "What is True Negative?", "Legitimate claim jise model ne correctly legitimate classify kiya."],
        ["41", "What is Class Imbalance?", "Jab ek class (clean claims) doosri class (fraud) se sankhya me bahut zyada ho."],
        ["42", "What is scale_pos_weight?", "XGBoost parameter jo minority fraud class ko heavy loss penalty deta hai."],
        ["43", "What is Data Leakage?", "Jab training ke dauran aisi information use ho jaye jo inference time par available na ho."],
        ["44", "What is Temporal Split?", "Time ke hisab se data split karna - past data train me, future data test me."],
        ["45", "What is Ego-Network?", "Kisi ek specific central node aur uske direct 1 ya 2-hop neighbors ka local graph."],
        ["46", "What is Min-Max Normalization?", "Values ko (X - min) / (max - min) formula se 0 se 1 ke scale me fit karna."],
        ["47", "What is Decision Support System?", "Aisa software jo human experts ko final decision lene me assist karta hai, replace nahi karta."],
        ["48", "What is Vercel?", "Cloud platform optimized for hosting fast static frontend applications and SPAs."],
        ["49", "What is Render?", "Cloud hosting platform jo backend Python web services aur containers run karta hai."],
        ["50", "What is SIU?", "Special Investigation Unit - insurance company ka specialized fraud audit department."]
    ]
    add_table_data(doc, rf_data, [0.6, 2.4, 4.0])

    # =========================================================================
    # SECTION 33 – “WHY DID YOU USE THIS?” QUESTIONS (14 QUESTIONS)
    # =========================================================================
    add_heading_1(doc, "SECTION 33 – “WHY DID YOU USE THIS?” ARCHITECTURAL JUSTIFICATIONS")

    why_questions = [
        ("1. Why XGBoost?",
         "XGBoost is the proven state-of-the-art for tabular structured data, offering built-in regularization, native missing value handling, and scale_pos_weight for imbalance.",
         "Deep learning overfits on tabular datasets, and Random Forest cannot optimize gradient residuals sequentially.",
         "Sir, tabular structured data par XGBoost sabse highest accuracy deta hai. Isme missing values aur class imbalance ke liye built-in support hai, aur ye decision trees ko sequentially optimize karta hai."),

        ("2. Why Isolation Forest?",
         "It isolates rare anomalies with O(n log n) linear time complexity without requiring labels or assuming normal Gaussian distribution.",
         "Traditional distance algorithms (like k-means) suffer from curse of dimensionality; Isolation Forest works via fast random sub-space cuts.",
         "Sir, Isolation Forest bina kisi labels ke unusual claims pakad leta hai. Ye fast hai aur normal distribution ka koi false assumption nahi banata."),

        ("3. Why NetworkX?",
         "NetworkX is natively integrated into Python Data Science stack, allowing seamless graph extraction from Pandas DataFrames and feeding metrics directly into ML matrices.",
         "For our 1,020-node graph, an external graph database like Neo4j would introduce unnecessary network latency and deployment complexity.",
         "Sir, NetworkX Python me natively chalta hai, isliye hum Pandas data se instant graph bana sakte hain aur centrality scores ko direct ML model me feed kar sakte hain."),

        ("4. Why PostgreSQL?",
         "Insurance data requires strict relational integrity (foreign keys between claimants, vehicles, invoices) and ACID transactional consistency.",
         "NoSQL databases lack strict relational joins, risking orphaned claims and corrupted financial ledger records.",
         "Sir, insurance me claims, invoices aur vehicles ka strict relational connection hota hai. PostgreSQL ACID properties aur foreign key constraints guarantee karta hai."),

        ("5. Why Supabase?",
         "Supabase provides a production-grade managed PostgreSQL 15 database with built-in JWT authentication, connection pooling, and automated backups.",
         "It eliminates manual Linux database server maintenance, allowing focus entirely on Data Science and ML pipelines.",
         "Sir, Supabase managed PostgreSQL provide karta hai jisme connection pooling aur secure JWT authentication built-in hota hai, jisse devops overhead zero ho jata hai."),

        ("6. Why FastAPI?",
         "FastAPI delivers asynchronous non-blocking IO, native Pydantic v2 data validation, and automatic OpenAPI Swagger documentation.",
         "Django is too monolithic and heavy; Flask lacks native async support and automatic request body type checking.",
         "Sir, FastAPI asynchronous hai, bahut fast hai, aur Pydantic se automatic request validation karta hai. Sath hi interactive Swagger API docs free me generate ho jate hain."),

        ("7. Why React?",
         "React's virtual DOM, declarative component architecture, and massive ecosystem enable building responsive interactive dashboards and live graph visualizers.",
         "State changes (like changing a claim's status) update only the affected UI components without full page reloads.",
         "Sir, React component-based library hai jo dynamic UI ke liye best hai. Investigator bina page reload kiye claims filter kar sakta hai aur live graph dekh sakta hai."),

        ("8. Why TypeScript?",
         "TypeScript adds static type definitions to JavaScript, catching API contract mismatches and null pointer bugs at compile-time rather than runtime in production.",
         "Strict interfaces (Claim, RiskScore, GraphNode) ensure frontend components never crash due to unexpected backend JSON changes.",
         "Sir, TypeScript compile time par bugs pakad leta hai. Backend Pydantic schemas aur frontend TypeScript interfaces exact match hote hain, jisse runtime crash nahi hota."),

        ("9. Why SHAP?",
         "SHAP is mathematically grounded in game theory (Shapley values), guaranteeing properties of local accuracy, missingness, and consistency that heuristic feature importances lack.",
         "Default tree feature importances (Gini/Gain) can be biased toward high-cardinality features; SHAP provides true directional attribution (+/-).",
         "Sir, SHAP mathematically proven technique hai jo batati hai ki kis feature ne risk score badhaya aur kisne ghataya. Gini importance directional insight nahi de sakti."),

        ("10. Why TF-IDF?",
         "TF-IDF balances term frequency with document rarity, ensuring common words (like 'car', 'damaged') don't inflate similarity, while rare terms (like 'whiplash') highlight duplicate narratives.",
         "Simple bag-of-words or word counts give too much weight to meaningless stop words.",
         "Sir, TF-IDF common generic words ki value kam kar deta hai aur jo rare words duplicate narrative me use hue hain unhe highlight karta hai."),

        ("11. Why Cosine Similarity?",
         "Cosine similarity measures the angle between two text vectors rather than magnitude, making it invariant to document length.",
         "A short invoice description and a long detailed repair narrative with identical terminology will correctly show high semantic alignment.",
         "Sir, Cosine similarity do text documents ke beech angle measure karti hai, isliye text chhota ho ya lamba, wo content ki true similarity pakad leti hai."),

        ("12. Why Jaccard Similarity?",
         "Jaccard similarity measures exact token set overlap (|A ∩ B| / |A ∪ B|) without requiring vector embedding models.",
         "It is highly intuitive, mathematically bounded between 0 and 1, and lightning-fast for checking matching invoice line items.",
         "Sir, Jaccard formula bahut simple aur fast hai. Invoice ke itemized parts aur bills check karne ke liye ye perfect token overlap score deta hai."),

        ("13. Why Vercel?",
         "Vercel offers global edge CDN delivery, automatic SSL, preview deployments, and sub-second asset caching tailored for modern Vite React applications.",
         "It provides high availability with zero manual server configuration.",
         "Sir, Vercel React frontend ko globally fast CDN par serve karta hai, with automatic HTTPS aur zero maintenance."),

        ("14. Why Render?",
         "Render hosts containerized Python web services natively with auto-deploy on Git push, environment variable management, and reliable uptime.",
         "It provides a dedicated cloud environment to run our FastAPI Uvicorn ASGI server reliably.",
         "Sir, Render cloud par hamara FastAPI server safely run hota hai with automated deployment and zero devops headache.")
    ]

    for q, sa, da, va in why_questions:
        add_qa_card(doc, q, sa, da, va)

    # =========================================================================
    # SECTION 34 – “WHAT IF?” QUESTIONS (10 SCENARIOS)
    # =========================================================================
    add_heading_1(doc, "SECTION 34 – “WHAT IF?” REAL-WORLD SCENARIO DEFENSE")

    what_if_questions = [
        ("Scenario 1: What if a legitimate claim is incorrectly flagged as suspicious by the system?",
         "The claim moves into the Desk Review / SIU audit queue where a human investigator verifies the documents.",
         "The investigator sees the SHAP explanation, recognizes that the high claim amount was justified by a luxury vehicle, overrides the AI flag, and approves the claim. No innocent policyholder is automatically rejected.",
         "Sir, hamara system autonomous judge nahi hai! Flag hone par claim human investigator ke desk review me jayega, wo genuine bill verify karke override approve kar dega."),

        ("Scenario 2: What if a completely new type of fraud occurs that is not present in historical data?",
         "Supervised XGBoost will likely score it low, but the unsupervised Isolation Forest and Graph Centrality will flag the anomaly.",
         "Because the transaction deviates statistically from normal claim distributions or connects to high-degree hubs, the composite formula catches it.",
         "Sir, agar fraud bilkul naya hai to supervised ML fail ho sakta hai, lekin hamara Unsupervised Anomaly Detector aur Graph Module use abnormal behavior ki wajah se pakad lenge."),

        ("Scenario 3: What if two claims have very similar narratives but are actually two different accidents?",
         "The duplicate similarity score will be high, but the other three signals (ML risk, anomaly, graph) will remain low.",
         "The composite score will remain below the Critical threshold, placing the claim in Standard Review where an investigator quickly notes different locations and clears it.",
         "Sir, duplicate score high aane par bhi agar baki 3 scores (ML, Anomaly, Graph) clean hain, to composite score low rahega aur human desk review me claim safely clear ho jayega."),

        ("Scenario 4: What if an auto-repair shop genuinely handles a very high volume of legitimate claims?",
         "While its degree centrality will be high, its claims will show clean invoices, diverse independent claimants, and low anomaly scores.",
         "The multi-signal framework ensures high degree alone cannot push a claim into the Critical fraud band without corroborating tabular or duplicate evidence.",
         "Sir, high degree hone ke bawajood agar garage ke claims clean hain aur duplicate bills nahi hain, to baki signals risk score ko balance rakhenge."),

        ("Scenario 5: What if incoming claim data has multiple missing values?",
         "FastAPI Pydantic validation rejects critical missing IDs, while continuous missing features are handled natively by XGBoost's default split routing.",
         "Median imputation and categorical 'UNKNOWN' encoding ensure pipelines never crash on incomplete records.",
         "Sir, missing values par system crash nahi hota. Pydantic invalid data reject karta hai aur XGBoost missing values ko automatically handle kar leta hai."),

        ("Scenario 6: What if the database goes down during claim ingestion?",
         "FastAPI catches the connection exception and returns HTTP 503 with a retry-after header; client payloads are not lost.",
         "In production, ingestion messages are buffered in a queue (like Redis or Kafka) until database connectivity recovers.",
         "Sir, DB drop hone par system 503 error return karta hai aur message queue incoming claim data ko buffer karke loss hone se bachati hai."),

        ("Scenario 7: What if fraudsters coordinate to keep all claim amounts under $2,000 to evade tabular ML?",
         "Tabular ML will see low dollar amounts, but the Graph Engine will spot that all 15 claimants used the same towing company and shared phone numbers.",
         "The high graph centrality and community detection score will escalate the entire cluster to the Critical triage band.",
         "Sir, yahi graph analysis ki power hai! Claim amount chhota hone par bhi jab unke shared phone number aur shared towing company graph me connect honge, to pura syndicate pakad me aa jayega."),

        ("Scenario 8: What if an investigator disagrees with the AI risk score?",
         "The investigator overrides the recommendation in the application UI, changing status from ESCALATED to CLOSED.",
         "The system logs the investigator's ID, override reason, and timestamp in the audit_logs table for future model retraining.",
         "Sir, human investigator ka decision final hota hai. Wo AI recommendation ko override karke reason note me enter kar sakta hai, jo audit log me permanently store ho jata hai."),

        ("Scenario 9: What if the model performance drifts over time as fraud patterns evolve?",
         "We monitor PR-AUC and false positive rates monthly using confirmed SIU investigation outcomes.",
         "When drift is detected, the automated pipeline triggers model retraining on the latest 12 months of confirmed claims.",
         "Sir, time ke sath fraud tactics badalte hain. Hum monthly false positive rate monitor karte hain aur naye confirmed cases ke sath model ko re-train karte hain."),

        ("Scenario 10: What if the external examiner asks you to prove that the graph is connected?",
         "I will show scripts/validate_graph.py output and Section 12 metrics: 1,020 nodes, 2,615 edges, and 153 claims sharing 167 invoices.",
         "The live NetworkX ego-network endpoint (/claims/{id}/network) renders immediate multi-hop topological connections in real-time.",
         "Sir, mai turant terminal par scripts/validate_graph.py run karke dikha dunga jisme 1,020 nodes aur 2,615 edges mathematically validated hain.")
    ]

    for q, sa, da, va in what_if_questions:
        add_qa_card(doc, q, sa, da, va)

    # =========================================================================
    # SECTION 35 – EXTERNAL EXAMINER CHALLENGE QUESTIONS (17 DEEP QUESTIONS)
    # =========================================================================
    add_heading_1(doc, "SECTION 35 – EXTERNAL EXAMINER CHALLENGE QUESTIONS (DEEP DEFENSE)")

    add_body(doc, "External viva me Senior Professors aur Industry Evaluators jo advanced trap questions puchte hain, unke authoritative defenses:")

    challenge_questions = [
        ("1. Why do you call this a 'Graph-Enhanced' system rather than a Graph Neural Network?",
         "Because we extract explicit graph-theoretic topological metrics (Degree, PageRank, Betweenness) via NetworkX and inject them into a multi-signal ensemble.",
         "GNNs learn latent node embeddings through message passing layers; our system uses explicit, highly interpretable graph centrality metrics tailored for regulatory transparency.",
         "Sir, humne ise 'Graph-Enhanced' isliye kaha kyunki hum graph topology se explicit features (Degree, PageRank) nikal kar apne composite decision pipeline me inject karte hain, jo fully explainable hai."),

        ("2. What specific additional information does the graph provide that tabular ML cannot see?",
         "Relational co-occurrence and multi-hop entity sharing across distinct policyholders.",
         "Tabular ML sees each row in isolation; the graph sees that Claim A and Claim B share an invoice number, and Claim B and Claim C share an auto-repair shop, exposing the syndicate.",
         "Sir, tabular ML har claim ko akele dekhta hai. Graph un hidden connections ko dikhata hai jahan do alag-alag log same fake bill ya same shady mechanic ko use kar rahe hote hain."),

        ("3. Why isn't a normal relational SQL query sufficient to find shared invoices?",
         "SQL joins can find 1-hop exact matches, but fail on multi-hop indirect collusion (Claimant A -> Car B -> Garage C -> Doctor D -> Claimant E).",
         "Multi-hop graph traversal in SQL requires expensive, deeply nested recursive CTEs that do not scale; NetworkX computes arbitrary-depth paths efficiently.",
         "Sir, SQL sirf direct matching (1-hop) kar sakta hai. Lekin syndicate fraud me indirect 3-hop ya 4-hop connections hote hain jise SQL recursive joins se nikalna extremely slow aur complex hota hai."),

        ("4. What is the fundamental difference between duplicate detection and fraud detection?",
         "Duplicate detection is a deterministic identity check; fraud detection is a probabilistic risk evaluation.",
         "A duplicate might be an accidental administrative error by an insurance clerk; fraud requires intent to deceive for unlawful financial gain.",
         "Sir, duplicate detection sirf copy-paste ya repeated submission check karta hai, jabki fraud detection intentional crime aur calculated deceit ko identify karta hai."),

        ("5. Why use supervised and unsupervised methods together in one pipeline?",
         "Supervised models catch known historical fraud typologies; Unsupervised models catch novel, zero-day fraud rings.",
         "Relying solely on supervised models creates a blindspot for new tactics; relying solely on unsupervised creates excessive false positives.",
         "Sir, supervised model purane sikhaye gaye fraud pakadta hai aur unsupervised model naye unusual fraud pakadta hai. Dono milkar 360-degree protection dete hain."),

        ("6. How did you validate your model against data leakage?",
         "By implementing a strict temporal train-test split (224 train / 96 test) and fitting all scalers and graph windows strictly on historical data.",
         "No future claim information or post-investigation fraud flags were accessible to the model during test prediction.",
         "Sir, humne random split ke bajay temporal time-based split kiya, aur scaling tatha imputation sirf training data par fit kiya taaki test data me koi leak na ho."),

        ("7. Which metric is more important in insurance fraud: Precision or Recall, and why?",
         "It depends on the business objective, but generally Recall is prioritized for detection, while High-Band Precision is prioritized for SIU action.",
         "Missing a $50,000 fraud claim (False Negative) costs the insurer far more than spending 30 minutes verifying an honest claim (False Positive).",
         "Sir, insurance me Recall sabse zyada important hai kyunki ek bhi missed fraud (False Negative) company ko lakho rupaye ka loss deta hai. Lekin investigator ka time bachane ke liye High band me precision 85%+ honi chahiye."),

        ("8. How would you validate this model if deployed in a real insurance firm tomorrow?",
         "Through Shadow Deployment (A/B testing in silent mode alongside existing rule engines) for 90 days.",
         "We would compare the system's triage flags against confirmed SIU field investigation resolutions without letting the AI influence active claims initially.",
         "Sir, hum shadow deployment karenge jahan model 90 din tak background me live claims ko score karega, aur hum verify karenge ki SIU officers ke manual findings se model kitna match karta hai."),

        ("9. How would you scale the graph to 10 million claims?",
         "Replace in-memory NetworkX with a distributed graph database like Neo4j, Amazon Neptune, or Apache HugeGraph.",
         "We would use Apache Spark GraphX for offline batch centrality calculations and Redis for real-time sub-graph ego-network caching.",
         "Sir, 10 million claims ke liye hum NetworkX ko distributed graph DB jaise Neo4j ya AWS Neptune se replace karenge, aur offline calculations ke liye Apache Spark use karenge."),

        ("10. What is the mathematical meaning of Shapley efficiency?",
         "The sum of all feature Shapley values plus the base expected value equals the exact model output: f(x) = E[f(x)] + sum(phi_i).",
         "This guarantees that the explanation completely accounts for the difference between the base rate and the current prediction without leaving residual unexplained risk.",
         "Sir, Shapley efficiency ka matlab hai ki sabhi feature attributions ko add karne par exact model prediction value ban jati hai, koi unexplained gap nahi rehta."),

        ("11. Why didn't you use SMOTE for handling class imbalance?",
         "SMOTE synthesizes synthetic tabular rows by linear interpolation between neighbors, creating ghost entities that do not exist in the graph.",
         "Interpolated tabular rows break graph topological integrity; instead, we used cost-sensitive scale_pos_weight in XGBoost.",
         "Sir, SMOTE tabular data me fake points bana deta hai jinka graph me koi real connection nahi hota. Isliye humne synthetic oversampling ke bajay cost-sensitive weighting use ki."),

        ("12. What was the exact fraud prevalence in your dataset?",
         "16.25% (52 fraudulent claims out of 320 total claims).",
         "Legitimate claims comprised 83.75% (268 claims), yielding an imbalance ratio of approximately 5.15 to 1.",
         "Sir, exact verified fraud prevalence 16.25% hai (320 me se 52 fraud claims aur 268 clean claims)."),

        ("13. What is the Ratcliff-Obershelp algorithm's formula for similarity?",
         "Similarity = 2 * M / (|S1| + |S2|), where M is the total count of characters in matching contiguous subsequences.",
         "It rewards shared substring chunks while heavily penalizing transposition and character deletion.",
         "Sir, formula hai 2 * M divided by total characters of both strings, jo common matching substrings par based hota hai."),

        ("14. Can your model replace a human insurance claim investigator?",
         "No. The system is designed strictly as a Decision Support System (DSS) to triage, prioritize, and explain evidence.",
         "Legal claim denials require human accountability, regulatory compliance, and physical field validation that AI cannot provide.",
         "Sir, bilkul nahi! System investigator ko replace karne ke liye nahi, unki efficiency badhane ke liye hai. Final legal decision hamesha human officer hi leta hai."),

        ("15. Why does your composite formula use static weights (0.45, 0.25, 0.15, 0.15)?",
         "Static weights provide absolute transparency, deterministic reproducibility, and regulatory auditability required by insurance compliance.",
         "While a meta-learner (stacking classifier) could learn dynamic weights, it introduces a second-level black box that insurance regulators frequently reject.",
         "Sir, static weights isliye use kiye taaki calculation transparent aur auditable rahe. Insurance regulators ko explain karna aasan hota hai ki kis signal ka kitna contribution hai."),

        ("16. How does your system handle data privacy regulations (like DPDP Act or GDPR)?",
         "Personally Identifiable Information (PII) like national IDs and phone numbers are hashed or masked in transit and at rest.",
         "Role-based access control (RBAC) ensures only authorized SIU officers can view unmasked claimant contact details.",
         "Sir, sensitive personal data ko hash kiya jata hai aur role-based access control ensure karta hai ki sirf authorized SIU officers hi unmasked data dekh sakein."),

        ("17. What is the single most compelling reason to adopt your system over existing solutions?",
         "It increases SIU investigation precision from 20% to 85.19% while safely auto-clearing 94.17% of low-risk claims.",
         "Insurers save millions in undetected fraud leakage while simultaneously speeding up genuine claim settlements for honest customers.",
         "Sir, sabse bada reason ye hai ki ye High risk claims me precision 20% se badhakar 85.19% kar deta hai, aur genuine customers ke claims ko 94.17% clean rate ke sath fast approve karta hai.")
    ]

    for q, sa, da, va in challenge_questions:
        add_qa_card(doc, q, sa, da, va)
