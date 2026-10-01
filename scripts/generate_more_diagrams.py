"""
scripts/generate_more_diagrams.py
----------------------------------
Generates the remaining high-resolution UML and DFD diagrams for the Blackbook.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("docs/figures", exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

# --- 7. DFD Level 0 Context & Level 1 ---
def create_dfd_context():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # External Entity
    user_box = patches.FancyBboxPatch((8, 20), 22, 20, boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.5)
    ax.add_patch(user_box)
    ax.text(19, 32, "EXTERNAL ENTITY", ha='center', va='center', fontsize=8, fontweight='bold', color="#64748B")
    ax.text(19, 26, "Claims Officer /\nSIU Investigator", ha='center', va='center', fontsize=9.5, fontweight='bold', color="#0F2C59")

    # Context Process
    proc_circle = plt.Circle((50, 30), 16, fc="#F8FAFC", ec="#0F2C59", lw=1.8)
    ax.add_patch(proc_circle)
    ax.text(50, 34, "0.0", ha='center', va='center', fontsize=11, fontweight='bold', color="#1E3A8A")
    ax.text(50, 27, "Graph-Enhanced\nClaim Fraud Detection\nDecision Support System", ha='center', va='center', fontsize=8, fontweight='bold', color="#0F2C59")

    # Data Store Entity
    db_box = patches.FancyBboxPatch((74, 20), 22, 20, boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#0F2C59", lw=1.5)
    ax.add_patch(db_box)
    ax.text(85, 32, "DATA STORE", ha='center', va='center', fontsize=8, fontweight='bold', color="#64748B")
    ax.text(85, 26, "Supabase PostgreSQL\nRelational Store\n(D1 Claims & Cases)", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#0F2C59")

    # Flows
    ax.annotate('Claim Query / Case Update', xy=(34, 34), xytext=(30, 34), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('Risk Scores / Dossier', xy=(30, 26), xytext=(34, 26), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('Write Mutations', xy=(74, 34), xytext=(66, 34), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('Fetch History / Centralities', xy=(66, 26), xytext=(74, 26), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))

    plt.tight_layout()
    plt.savefig("docs/figures/dfd_context.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 8. Use Case Diagram ---
def create_use_case_diagram():
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # System boundary box
    sys_box = patches.FancyBboxPatch((30, 5), 65, 90, boxstyle="square,pad=1.0", fc="#FAFAFA", ec="#0F2C59", lw=1.5)
    ax.add_patch(sys_box)
    ax.text(62.5, 92, "FraudShield AI Decision Support System", ha='center', va='center', fontsize=10.5, fontweight='bold', color="#0F2C59")

    # Actors
    ax.text(12, 65, "Claims Officer\n(Persona: Intake)", ha='center', va='center', fontsize=9, fontweight='bold', color="#0F2C59")
    ax.plot([12, 12], [70, 76], color="#0F2C59", lw=2)
    ax.plot([8, 16], [73, 73], color="#0F2C59", lw=2)
    ax.plot([12, 9], [70, 66], color="#0F2C59", lw=2)
    ax.plot([12, 15], [70, 66], color="#0F2C59", lw=2)
    ax.add_patch(plt.Circle((12, 78), 2.5, fc="#FFFFFF", ec="#0F2C59", lw=2))

    ax.text(12, 20, "SIU Investigator\n(Persona: Forensic)", ha='center', va='center', fontsize=9, fontweight='bold', color="#0F2C59")
    ax.plot([12, 12], [25, 31], color="#0F2C59", lw=2)
    ax.plot([8, 16], [28, 28], color="#0F2C59", lw=2)
    ax.plot([12, 9], [25, 21], color="#0F2C59", lw=2)
    ax.plot([12, 15], [25, 21], color="#0F2C59", lw=2)
    ax.add_patch(plt.Circle((12, 33), 2.5, fc="#FFFFFF", ec="#0F2C59", lw=2))

    use_cases = [
        ("UC-1: Authenticate & Provision JWT", 62.5, 83),
        ("UC-2: Intake Claim & Execute Validation", 62.5, 71),
        ("UC-3: View Claims Queue & Risk Tiers", 62.5, 59),
        ("UC-4: Query Customer 360 Dossier", 62.5, 47),
        ("UC-5: Inspect Graph Collusion Subnetwork", 62.5, 35),
        ("UC-6: Review Local SHAP Attributions", 62.5, 23),
        ("UC-7: Transition Case State & Log Notes", 62.5, 11)
    ]

    for title, x, y in use_cases:
        ellipse = patches.Ellipse((x, y), 50, 7.5, fc="#FFFFFF", ec="#1E3A8A", lw=1.2)
        ax.add_patch(ellipse)
        ax.text(x, y, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#1E293B")

    # Lines from actors to use cases
    for i in range(4):
        ax.plot([16, 38], [73, use_cases[i][2]], color="#64748B", lw=1, ls="--")
    for i in range(2, 7):
        ax.plot([16, 38], [28, use_cases[i][2]], color="#64748B", lw=1, ls="--")

    plt.tight_layout()
    plt.savefig("docs/figures/use_case_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 9. Class Diagram ---
def create_class_diagram():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    classes = [
        ("ClaimModel", ["+ claim_id: str", "+ claimant_id: str", "+ claim_amount: float", "+ claim_date: str", "+ fraud_label: int"], 5, 55, 25, 38),
        ("ClaimService", ["- db: DatabasePool", "+ get_claim(id): Claim", "+ list_claims(filters): List", "+ create_claim(data): str"], 38, 55, 28, 38),
        ("RiskScoringEngine", ["- weights: ComponentWeights", "+ calculate_score(ml, an, dup, gr): float", "+ classify_band(score): str"], 70, 55, 28, 38),
        ("GraphService", ["- graph: nx.Graph", "+ get_subgraph(claim_id): Dict", "+ get_entity_metrics(id): Dict"], 38, 8, 28, 35),
        ("CaseManager", ["- valid_transitions: Dict", "+ create_case(claim_id): str", "+ update_status(id, status): bool", "+ add_note(id, note): str"], 70, 8, 28, 35)
    ]

    for name, methods, x, y, w, h in classes:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0.2", fc="#FFFFFF", ec="#0F2C59", lw=1.4)
        ax.add_patch(box)
        header = patches.FancyBboxPatch((x, y + h - 8), w, 8, boxstyle="square,pad=0.2", fc="#0F2C59", ec="#0F2C59", lw=1)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 4, name, ha='center', va='center', fontsize=9.5, fontweight='bold', color="#FFFFFF")
        for idx, m in enumerate(methods):
            ax.text(x + 1.5, y + h - 14 - (idx * 5.5), m, fontsize=7.5, color="#1F2937")

    # Relations
    ax.annotate('', xy=(38, 74), xytext=(30, 74), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('', xy=(70, 74), xytext=(66, 74), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('', xy=(52, 43), xytext=(52, 55), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))
    ax.annotate('', xy=(84, 43), xytext=(84, 55), arrowprops=dict(arrowstyle="->", lw=1.2, color="#0F2C59"))

    plt.tight_layout()
    plt.savefig("docs/figures/class_diagram.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 10. Deployment Architecture ---
def create_deployment_architecture():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    clouds = [
        ("Vercel Edge Platform", "Global CDN Distribution\nReact 18 / Vite SPA\nURL: insurance-claimed-detection.vercel.app\nEdge Rewrites: /api/* -> Render", 5, 12, 28, 38),
        ("Render Cloud Infrastructure", "Linux Container Web Service\nPython 3.13 / Uvicorn ASGI Server\nURL: fraudshield-api-3j07.onrender.com\nArtifacts: XGBoost & Scalers", 36, 12, 28, 38),
        ("Supabase Cloud (AWS Mumbai)", "PostgreSQL 15 Managed DB\nSupavisor Transaction Pooler (Port 6543)\nTables: claims, users, audit_logs\nHost: aws-0-ap-south-1.pooler.supabase.com", 67, 12, 28, 38)
    ]

    for name, desc, x, y, w, h in clouds:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.0", fc="#F8FAFC", ec="#0F2C59", lw=1.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 6, name, ha='center', va='center', fontsize=9.5, fontweight='bold', color="#0F2C59")
        ax.text(x + w/2, y + h/2 - 2, desc, ha='center', va='center', fontsize=7.8, color="#334155")

    # Connectors
    ax.annotate('HTTPS (TLS 1.3)\nProxy /api', xy=(36, 31), xytext=(33, 31), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#1E3A8A"))
    ax.annotate('Pooled TCP (SSL)\nPort 6543', xy=(67, 31), xytext=(64, 31), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#1E3A8A"))

    plt.tight_layout()
    plt.savefig("docs/figures/deployment_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()

# --- 11. Feature Engineering Breakdown ---
def create_feature_pipeline():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis('off')

    categories = [
        ("Financial Discrepancy", "• claim_to_premium_ratio\n• invoice_to_claim_ratio\n• amount_p90_outlier_flag\n• total_claimed_to_date", 4, 10, 21, 30),
        ("Temporal Anomalies", "• days_since_policy_start\n• claim_age_days\n• early_inception_claim_flag\n• policy_duration_ratio", 28, 10, 21, 30),
        ("Behavioral Frequency", "• claimant_claim_frequency\n• provider_claim_volume\n• serial_claimant_flag\n• provider_dispute_rate", 52, 10, 21, 30),
        ("Graph Topology Signals", "• degree centralities\n• claimant & provider PageRank\n• fraud_neighbor_ratio\n• repeated_entity_pairs", 76, 10, 21, 30),
    ]

    for name, items, x, y, w, h in categories:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", fc="#F0F4F8", ec="#0F2C59", lw=1.3)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 5, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color="#0F2C59")
        ax.text(x + 2, y + h/2 - 2, items, ha='left', va='center', fontsize=7.5, color="#1F2937")

    plt.tight_layout()
    plt.savefig("docs/figures/feature_pipeline.png", dpi=300, bbox_inches='tight')
    plt.close()

create_dfd_context()
create_use_case_diagram()
create_class_diagram()
create_deployment_architecture()
create_feature_pipeline()
print("All extended diagrams created.")
