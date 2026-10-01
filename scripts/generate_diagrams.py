"""
scripts/generate_diagrams.py
-----------------------------
Generates high-resolution, professional academic diagrams for the
Bachelor of Data Science Blackbook report using matplotlib.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("docs/figures", exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

# --- 1. System Architecture ---
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background boxes
    p_box = patches.FancyBboxPatch((5, 70), 90, 24, boxstyle="round,pad=1.5", fc="#F0F4F8", ec="#0F2C59", lw=1.5)
    a_box = patches.FancyBboxPatch((5, 34), 90, 31, boxstyle="round,pad=1.5", fc="#F8FAFC", ec="#0F2C59", lw=1.5)
    d_box = patches.FancyBboxPatch((5, 4), 90, 24, boxstyle="round,pad=1.5", fc="#F0F4F8", ec="#0F2C59", lw=1.5)
    ax.add_patch(p_box)
    ax.add_patch(a_box)
    ax.add_patch(d_box)

    # Titles
    ax.text(8, 90, "PRESENTATION TIER (Edge CDN)", fontsize=11, fontweight='bold', color="#0F2C59")
    ax.text(8, 61, "APPLICATION & ANALYTICS TIER (Container Microservice)", fontsize=11, fontweight='bold', color="#0F2C59")
    ax.text(8, 24, "PERSISTENT DATA TIER (Managed Relational Store)", fontsize=11, fontweight='bold', color="#0F2C59")

    # Presentation items
    b1 = patches.FancyBboxPatch((10, 74), 38, 13, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#1E3A8A", lw=1.2)
    b2 = patches.FancyBboxPatch((52, 74), 38, 13, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#1E3A8A", lw=1.2)
    ax.add_patch(b1)
    ax.add_patch(b2)
    ax.text(29, 82, "Officer Web Portal (React 18 / Vite / TS)", ha='center', va='center', fontsize=9.5, fontweight='bold')
    ax.text(29, 77, "Vercel Edge CDN: insurance-claimed-detection.vercel.app", ha='center', va='center', fontsize=8, color="#4B5563")
    ax.text(71, 82, "Forensic Analytics Console (Streamlit)", ha='center', va='center', fontsize=9.5, fontweight='bold')
    ax.text(71, 77, "Streamlit Cloud: insurance-fraud-analytics.streamlit.app", ha='center', va='center', fontsize=8, color="#4B5563")

    # Application items
    gateway = patches.FancyBboxPatch((10, 48), 80, 10, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.2)
    ax.add_patch(gateway)
    ax.text(50, 53, "FastAPI Microservice Gateway (Render: fraudshield-api-3j07.onrender.com)\nDual Route Mounting (/api/* & /*) | JWT RBAC Security | OpenAPI 3.1", ha='center', va='center', fontsize=9, fontweight='bold')

    services = [
        ("ClaimService", 10, 36, 18),
        ("XGBoost ML", 30, 36, 18),
        ("Isolation Forest", 50, 36, 19),
        ("NetworkX Graph", 71, 36, 19)
    ]
    for name, x, y, w in services:
        sb = patches.FancyBboxPatch((x, y), w, 9, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#3B82F6", lw=1)
        ax.add_patch(sb)
        ax.text(x + w/2, y + 4.5, name, ha='center', va='center', fontsize=8.5, fontweight='bold')

    # Data items
    db1 = patches.FancyBboxPatch((10, 7), 38, 14, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.2)
    db2 = patches.FancyBboxPatch((52, 7), 38, 14, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.2)
    ax.add_patch(db1)
    ax.add_patch(db2)
    ax.text(29, 15, "Supabase PostgreSQL 15 Store", ha='center', va='center', fontsize=9.5, fontweight='bold')
    ax.text(29, 10, "Claims, Claimants, Policies, Vehicles, Invoices", ha='center', va='center', fontsize=8, color="#4B5563")
    ax.text(71, 15, "Supavisor Connection Pooler", ha='center', va='center', fontsize=9.5, fontweight='bold')
    ax.text(71, 10, "IPv4 Transaction Routing (Port 6543) / AWS Mumbai", ha='center', va='center', fontsize=8, color="#4B5563")

    # Arrows
    ax.annotate('', xy=(29, 59), xytext=(29, 73), arrowprops=dict(arrowstyle="->", lw=1.5, color="#0F2C59"))
    ax.annotate('', xy=(71, 22), xytext=(71, 73), arrowprops=dict(arrowstyle="->", lw=1.5, color="#0F2C59", ls='--'))
    ax.annotate('', xy=(50, 22), xytext=(50, 35), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#0F2C59"))

    plt.tight_layout()
    plt.savefig("docs/figures/system_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 2. End-to-End Fraud Detection Workflow ---
def create_fraud_workflow():
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 50)
    ax.axis('off')

    steps = [
        ("1. Intake & Validation", "Portal / API POST\nPydantic Check", 5, 20),
        ("2. Feature Pipeline", "38 Relational &\nBehavioral Ratios", 23, 20),
        ("3. Multi-Engine Run", "XGBoost, Isolation\nForest & NetworkX", 41, 20),
        ("4. Hybrid Scoring", "Empirical Fusion\nFormula in [0, 1]", 59, 20),
        ("5. Triage Banding", "CRITICAL / HIGH\nMEDIUM / LOW", 77, 20),
        ("6. SIU Investigation", "Dossier & Graph\nCase Lifecycle", 95, 20)
    ]

    for title, desc, x, y in steps:
        box = patches.FancyBboxPatch((x, y), 14, 18, boxstyle="round,pad=0.8", fc="#F8FAFC", ec="#0F2C59", lw=1.3)
        ax.add_patch(box)
        ax.text(x + 7, y + 13, title, ha='center', va='center', fontsize=8, fontweight='bold', color="#0F2C59")
        ax.text(x + 7, y + 6, desc, ha='center', va='center', fontsize=7.5, color="#334155")

    for i in range(len(steps) - 1):
        x_start = steps[i][2] + 14.5
        x_end = steps[i+1][2] - 0.5
        ax.annotate('', xy=(x_end, 29), xytext=(x_start, 29), arrowprops=dict(arrowstyle="->", lw=1.5, color="#0F2C59"))

    plt.tight_layout()
    plt.savefig("docs/figures/fraud_workflow.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 3. Confusion Matrix ---
def create_confusion_matrix():
    fig, ax = plt.subplots(figsize=(5, 4.5), dpi=300)
    # Actual test set confusion matrix from models/fraud_model/metadata.json:
    # TN=66, FP=12, FN=15, TP=3
    cm = np.array([[66, 12], [15, 3]])
    cax = ax.matshow(cm, cmap='Blues', alpha=0.85)

    for i in range(2):
        for j in range(2):
            val = cm[i, j]
            label = f"{val}\n" + ("(TN)" if i==0 and j==0 else "(FP)" if i==0 and j==1 else "(FN)" if i==1 and j==0 else "(TP)")
            color = "white" if val > 30 else "black"
            ax.text(j, i, label, ha='center', va='center', fontsize=11, fontweight='bold', color=color)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Pred Legit (0)', 'Pred Fraud (1)'], fontsize=9.5, fontweight='bold')
    ax.set_yticklabels(['Actual Legit (0)', 'Actual Fraud (1)'], fontsize=9.5, fontweight='bold')
    ax.set_xlabel('Predicted Class', fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel('Ground Truth Class', fontsize=10, fontweight='bold', labelpad=8)
    ax.set_title('XGBoost Fraud Model: Test Confusion Matrix\n(Threshold = 0.50, Test N = 96)', fontsize=11, fontweight='bold', pad=15, color="#0F2C59")

    fig.colorbar(cax, shrink=0.75)
    plt.tight_layout()
    plt.savefig("docs/figures/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 4. Entity-Relationship Diagram ---
def create_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    entities = [
        ("CLAIMANTS", ["PK claimant_id", "name", "age, city, gender"], 5, 65, 24, 26),
        ("POLICIES", ["PK policy_id", "FK claimant_id", "policy_type, premium", "start_date, end_date"], 38, 65, 24, 26),
        ("VEHICLES", ["PK vehicle_id", "FK claimant_id", "make, model_year", "registration_no"], 71, 65, 24, 26),
        ("PROVIDERS", ["PK provider_id", "name, city", "provider_type", "rating (0-5)"], 5, 15, 24, 26),
        ("INVOICES", ["PK invoice_id", "FK provider_id", "amount, date", "description"], 38, 15, 24, 26),
        ("CLAIMS", ["PK claim_id", "FK claimant_id", "FK policy_id, FK vehicle_id", "FK provider_id, FK invoice_id", "claim_amount, date", "fraud_label (0/1)"], 71, 10, 26, 36),
    ]

    for name, cols, x, y, w, h in entities:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.5)
        ax.add_patch(box)
        header = patches.FancyBboxPatch((x, y + h - 8), w, 8, boxstyle="round,pad=0.2", fc="#0F2C59", ec="#0F2C59", lw=1)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 4, name, ha='center', va='center', fontsize=9, fontweight='bold', color="#FFFFFF")
        for idx, col in enumerate(cols):
            prefix = "• "
            fw = 'bold' if "PK" in col or "FK" in col else 'normal'
            ax.text(x + 2, y + h - 13 - (idx * 5), prefix + col, fontsize=7.5, fontweight=fw, color="#1F2937")

    # Connectors
    ax.annotate('1:N holds', xy=(38, 78), xytext=(29, 78), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('1:N owns', xy=(71, 78), xytext=(62, 78), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('1:N issues', xy=(38, 28), xytext=(29, 28), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('1:N attached', xy=(71, 28), xytext=(62, 28), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('1:N covers', xy=(75, 46), xytext=(50, 65), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))

    plt.tight_layout()
    plt.savefig("docs/figures/er_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 5. State Diagram ---
def create_state_diagram():
    fig, ax = plt.subplots(figsize=(9, 4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 45)
    ax.axis('off')

    states = [
        ("NEW", "Queue Placement\nRisk >= 0.55", 8, 20),
        ("UNDER_REVIEW", "Investigator Assigned\nPreliminary Inquiry", 30, 20),
        ("ESCALATED", "Forensic / Field\nSyndicate Audit", 52, 20),
        ("RESOLVED", "Fraud Confirmed\nPayment Denied", 75, 28),
        ("FALSE_POSITIVE", "Claim Cleared\nApproved Payout", 75, 10)
    ]

    for name, desc, x, y in states:
        color = "#EF4444" if name=="RESOLVED" else "#10B981" if name=="FALSE_POSITIVE" else "#F8FAFC"
        tcolor = "#FFFFFF" if name in ["RESOLVED", "FALSE_POSITIVE"] else "#0F2C59"
        ecolor = "#DC2626" if name=="RESOLVED" else "#059669" if name=="FALSE_POSITIVE" else "#0F2C59"
        box = patches.FancyBboxPatch((x, y), 18, 14, boxstyle="round,pad=0.6", fc=color, ec=ecolor, lw=1.4)
        ax.add_patch(box)
        ax.text(x + 9, y + 9.5, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color=tcolor)
        ax.text(x + 9, y + 4.5, desc, ha='center', va='center', fontsize=7, color="#FFFFFF" if name in ["RESOLVED", "FALSE_POSITIVE"] else "#475569")

    # Connectors
    ax.annotate('', xy=(30, 27), xytext=(26, 27), arrowprops=dict(arrowstyle="->", lw=1.3, color="#0F2C59"))
    ax.annotate('', xy=(52, 27), xytext=(48, 27), arrowprops=dict(arrowstyle="->", lw=1.3, color="#0F2C59"))
    ax.annotate('', xy=(75, 34), xytext=(70, 29), arrowprops=dict(arrowstyle="->", lw=1.3, color="#DC2626"))
    ax.annotate('', xy=(75, 17), xytext=(70, 25), arrowprops=dict(arrowstyle="->", lw=1.3, color="#059669"))

    plt.tight_layout()
    plt.savefig("docs/figures/state_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 6. Gantt Chart ---
def create_gantt_chart():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    tasks = [
        "1. Schema Design & Data Setup",
        "2. Feature Pipeline & Duplicate Engine",
        "3. Supervised XGBoost & Isolation Forest",
        "4. NetworkX Graph & Hybrid Risk Fusion",
        "5. FastAPI Microservice & React UI",
        "6. Cloud Deployment & Validation"
    ]
    starts = [1, 4, 7, 10, 13, 15]
    durations = [3, 3, 3, 3, 3, 2]

    y_pos = np.arange(len(tasks))
    ax.barh(y_pos, durations, left=starts, height=0.5, align='center', color='#1E3A8A', alpha=0.9, edgecolor='#0F2C59')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=9, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlabel('Project Timeline (Academic Weeks 1 to 16)', fontsize=10, fontweight='bold', labelpad=10)
    ax.set_xlim(0, 17)
    ax.set_xticks(range(1, 17))
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("docs/figures/gantt_chart.png", dpi=300, bbox_inches='tight')
    plt.close()

print("Generating diagrams...")
create_system_architecture()
create_fraud_workflow()
create_confusion_matrix()
create_er_diagram()
create_state_diagram()
create_gantt_chart()
print("All diagrams generated in docs/figures/ successfully.")
