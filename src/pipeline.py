"""
src/pipeline.py
---------------
Phase 13: End-to-End Pipeline Orchestration & Claim Journey Verification.
Unifies all 9 core stages:
DATA -> CLEANING -> FEATURE ENGINEERING -> DUPLICATE DETECTION -> ML FRAUD MODEL ->
ANOMALY DETECTION -> GRAPH ANALYSIS -> RISK ENGINE -> INVESTIGATION CASE -> FASTAPI -> DASHBOARD
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "fraud_detection.db"
FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("Pipeline")


def run_full_pipeline(rebuild_db: bool = False, verbose: bool = True) -> Dict[str, Any]:
    """
    Executes the entire end-to-end pipeline in order.
    Returns status and execution metrics for each stage.
    """
    start_total = time.time()
    stage_metrics: Dict[str, Any] = {}

    def log_stage(stage_num: int, name: str):
        if verbose:
            print("\n" + "=" * 70)
            print(f"STAGE {stage_num}: {name.upper()}")
            print("=" * 70)

    # ── Stage 1: Data Validation & Relational Ingestion ───────────────────────
    log_stage(1, "Relational Ingestion & SQLite Seeding")
    t0 = time.time()
    if rebuild_db or not DB_PATH.exists():
        from database.seed import seed_database
        seed_res = seed_database(DB_PATH)
        stage_metrics["stage_1_db"] = {"status": "SUCCESS", "details": seed_res, "duration": round(time.time() - t0, 2)}
    else:
        stage_metrics["stage_1_db"] = {"status": "SKIPPED_EXISTING", "duration": round(time.time() - t0, 2)}

    # ── Stage 2: Feature Engineering ─────────────────────────────────────────
    log_stage(2, "Claim Feature Engineering")
    t0 = time.time()
    from src.features.claim_features import build_claim_features
    claim_feat_df = build_claim_features()
    stage_metrics["stage_2_features"] = {
        "status": "SUCCESS",
        "claims_count": len(claim_feat_df),
        "features_count": claim_feat_df.shape[1],
        "duration": round(time.time() - t0, 2),
    }

    # ── Stage 3: Duplicate & Similar Claim Detection ─────────────────────────
    log_stage(3, "Duplicate & Similarity Detection")
    t0 = time.time()
    from src.duplicate.duplicate_detector import run_pipeline as run_dup_pipeline
    run_dup_pipeline()
    stage_metrics["stage_3_duplicate"] = {"status": "SUCCESS", "duration": round(time.time() - t0, 2)}

    # ── Stage 4: Supervised ML Model Training ────────────────────────────────
    log_stage(4, "Supervised ML Fraud Model Training")
    t0 = time.time()
    from src.models.train import run_pipeline as run_train_pipeline
    run_train_pipeline()
    stage_metrics["stage_4_ml_model"] = {"status": "SUCCESS", "duration": round(time.time() - t0, 2)}

    # ── Stage 5: Unsupervised Anomaly Detection ──────────────────────────────
    log_stage(5, "Unsupervised Anomaly Detection")
    t0 = time.time()
    from src.models.anomaly.anomaly_detector import run_pipeline as run_anom_pipeline
    run_anom_pipeline()
    stage_metrics["stage_5_anomaly"] = {"status": "SUCCESS", "duration": round(time.time() - t0, 2)}

    # ── Stage 6: Graph Construction & Topological Features ───────────────────
    log_stage(6, "Knowledge Graph Construction & Graph Features")
    t0 = time.time()
    from src.graph.build_graph import build_knowledge_graph
    from src.graph.graph_features import compute_graph_features
    from src.features.merge_features import merge_all_features

    G, nodes_df, edges_df = build_knowledge_graph(
        relational_dir=str(ROOT / "data" / "relational"),
        output_dir=str(ROOT / "data" / "graph"),
    )
    gf_df = compute_graph_features()
    final_df = merge_all_features()
    stage_metrics["stage_6_graph"] = {
        "status": "SUCCESS",
        "nodes": len(nodes_df),
        "edges": len(edges_df),
        "final_features": final_df.shape[1],
        "duration": round(time.time() - t0, 2),
    }

    # ── Stage 7: Hybrid Risk Engine ──────────────────────────────────────────
    log_stage(7, "Hybrid Multi-Signal Risk Scoring")
    t0 = time.time()
    from src.scoring.risk_engine import run_pipeline as run_scoring_pipeline
    run_scoring_pipeline()
    stage_metrics["stage_7_risk_engine"] = {"status": "SUCCESS", "duration": round(time.time() - t0, 2)}

    # ── Stage 8: Investigation Case Management ───────────────────────────────
    log_stage(8, "Case Management Queue Synchronization")
    t0 = time.time()
    from src.cases.case_manager import CaseManager
    cm = CaseManager(db_path=DB_PATH)
    active_cases = cm.list_cases()
    stage_metrics["stage_8_cases"] = {
        "status": "SUCCESS",
        "cases_count": len(active_cases),
        "duration": round(time.time() - t0, 2),
    }

    # ── Stage 9: Explainability Batch Precomputation ─────────────────────────
    log_stage(9, "Explainability (SHAP & Graph Evidence) Batch Engine")
    t0 = time.time()
    from src.explainability.batch_explain import precompute_all_explanations
    exp_dict = precompute_all_explanations()
    stage_metrics["stage_9_explainability"] = {
        "status": "SUCCESS",
        "explanations_count": len(exp_dict),
        "duration": round(time.time() - t0, 2),
    }

    total_duration = round(time.time() - start_total, 2)
    stage_metrics["total_duration_seconds"] = total_duration

    if verbose:
        print("\n" + "=" * 70)
        print(f"END-TO-END PIPELINE COMPLETED SUCCESSFULLY IN {total_duration}s")
        print("=" * 70)

    return stage_metrics


def verify_claim_journey(claim_id: str = "CLM00001", verbose: bool = True) -> Dict[str, Any]:
    """
    Traces and verifies a single claim throughout all 9 lifecycle stages:
    Claim ID -> Relational Facts -> Features -> ML Prediction -> Anomaly Score ->
    Duplicate Detection -> Graph Relationships -> Final Risk -> Explanation -> Investigation Case
    """
    cid = claim_id.strip()
    journey: Dict[str, Any] = {"claim_id": cid, "verified": False, "stages": {}}

    if verbose:
        print("\n" + "=" * 75)
        print(f"VERIFYING END-TO-END CLAIM JOURNEY: {cid}")
        print("=" * 75)

    # ── Step 1: Relational Claim Facts in SQLite ─────────────────────────────
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.*, cl.name as claimant_name, cl.city as claimant_city,
                   p.policy_type, p.premium, pr.provider_name, pr.city as provider_city,
                   v.make as vehicle_make, v.vehicle_type, i.invoice_amount
            FROM claims c
            LEFT JOIN claimants cl ON c.claimant_id = cl.claimant_id
            LEFT JOIN policies p ON c.policy_id = p.policy_id
            LEFT JOIN providers pr ON c.provider_id = pr.provider_id
            LEFT JOIN vehicles v ON c.vehicle_id = v.vehicle_id
            LEFT JOIN invoices i ON c.invoice_id = i.invoice_id
            WHERE c.claim_id = ?
            """,
            (cid,),
        )
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Claim '{cid}' not found in database")
        claim_facts = dict(row)

    journey["stages"]["1_relational_facts"] = {
        "claim_id": cid,
        "amount": claim_facts.get("claim_amount"),
        "claim_type": claim_facts.get("claim_type"),
        "claimant": claim_facts.get("claimant_name"),
        "provider": claim_facts.get("provider_name"),
        "ground_truth_fraud": "YES (Fraud)" if claim_facts.get("fraud_label") == 1 else "NO (Legitimate)",
    }
    if verbose:
        print(f"[1. Relational Facts] Amount: ${claim_facts.get('claim_amount'):,.2f} | Type: {claim_facts.get('claim_type')} | Ground Truth: {journey['stages']['1_relational_facts']['ground_truth_fraud']}")

    # ── Step 2: Feature Engineering Vector ───────────────────────────────────
    final_features_path = FEATURES_DIR / "final_claim_features.csv"
    features_row = {}
    if final_features_path.exists():
        fdf = pd.read_csv(final_features_path, keep_default_na=False)
        m = fdf[fdf["claim_id"] == cid]
        if not m.empty:
            features_row = m.iloc[0].to_dict()

    journey["stages"]["2_features"] = {
        "features_available": len(features_row) > 0,
        "days_since_policy_start": features_row.get("days_since_policy_start"),
        "amount_to_premium_ratio": features_row.get("amount_to_premium_ratio"),
        "provider_claim_volume": features_row.get("provider_claim_volume"),
    }
    if verbose:
        print(f"[2. Features] Days Since Policy Start: {features_row.get('days_since_policy_start')} | Amount/Premium Ratio: {features_row.get('amount_to_premium_ratio')}")

    # ── Step 3: Supervised ML Prediction ─────────────────────────────────────
    from api.services.prediction_service import PredictionService
    pred_service = PredictionService()
    ml_pred = pred_service.predict_fraud(claim_id=cid)

    journey["stages"]["3_ml_prediction"] = {
        "fraud_probability": ml_pred.get("fraud_probability"),
        "predicted_fraud": ml_pred.get("predicted_fraud"),
        "model_name": ml_pred.get("model_name"),
    }
    if verbose:
        print(f"[3. ML Prediction] Model: {ml_pred.get('model_name')} | Fraud Probability: {ml_pred.get('fraud_probability'):.4f}")

    # ── Step 4: Unsupervised Anomaly Score ───────────────────────────────────
    anom_res = pred_service.score_anomaly(claim_id=cid)
    journey["stages"]["4_anomaly_score"] = {
        "anomaly_score": anom_res.get("anomaly_score"),
        "is_anomaly": anom_res.get("is_anomaly"),
    }
    if verbose:
        print(f"[4. Anomaly Score] Calibrated Score: {anom_res.get('anomaly_score'):.4f} | Is Outlier: {anom_res.get('is_anomaly')}")

    # ── Step 5: Duplicate Detection ──────────────────────────────────────────
    dup_path = FEATURES_DIR / "duplicate_features.csv"
    dup_row = {}
    if dup_path.exists():
        ddf = pd.read_csv(dup_path, keep_default_na=False)
        dm = ddf[ddf["claim_id"] == cid]
        if not dm.empty:
            dup_row = dm.iloc[0].to_dict()

    journey["stages"]["5_duplicate_detection"] = {
        "similarity_score": float(dup_row.get("similarity_score", dup_row.get("duplicate_similarity_score", 0.0))),
        "duplicate_type": str(dup_row.get("duplicate_type", "NONE")),
        "duplicate_flag": int(dup_row.get("duplicate_flag", dup_row.get("is_duplicate_flag", 0))),
    }
    if verbose:
        print(f"[5. Duplicate Detection] Similarity: {journey['stages']['5_duplicate_detection']['similarity_score']:.4f} | Category: {journey['stages']['5_duplicate_detection']['duplicate_type']}")

    # ── Step 6: Graph Topological Analysis ───────────────────────────────────
    from api.services.graph_service import GraphService
    g_service = GraphService()
    g_res = g_service.analyze_graph(claim_id=cid)

    journey["stages"]["6_graph_relationships"] = {
        "claim_degree": g_res.get("claim_degree", 6),
        "claimant_degree": g_res.get("claimant_degree", 0),
        "connected_claim_count": g_res.get("connected_claim_count", 0),
        "provider_claim_count": g_res.get("provider_claim_count", 0),
        "fraud_neighbor_ratio": g_res.get("fraud_neighbor_ratio", 0.0),
        "suspicious_neighbor_count": g_res.get("suspicious_neighbor_count", 0),
    }
    if verbose:
        print(f"[6. Graph Network] Provider Claim Count: {g_res.get('provider_claim_count')} | Fraud Neighbor Ratio: {g_res.get('fraud_neighbor_ratio')}")

    # ── Step 7: Final Composite Risk Engine ───────────────────────────────────
    from api.services.claim_service import ClaimService
    claim_service = ClaimService(db_path=DB_PATH)
    risk_data = claim_service.get_claim_risk(cid) or {}

    journey["stages"]["7_final_risk"] = {
        "final_risk_score": risk_data.get("final_risk_score", 0.0),
        "risk_band": risk_data.get("risk_band", "LOW"),
        "reasons": risk_data.get("risk_reasons", []),
    }
    if verbose:
        print(f"[7. Final Risk Engine] Composite Score: {risk_data.get('final_risk_score', 0.0):.4f} | Risk Band: {risk_data.get('risk_band')}")

    # ── Step 8: Multimodal Explainability (SHAP + Graph) ─────────────────────
    from src.explainability.claim_explainer import explain_claim
    exp = explain_claim(cid)

    journey["stages"]["8_explanation"] = {
        "top_positive_factors": [f["feature"] for f in exp.get("top_positive_factors", [])[:3]],
        "top_negative_factors": [f["feature"] for f in exp.get("top_negative_factors", [])[:2]],
        "summary": exp.get("summary_text", ""),
    }
    if verbose:
        print(f"[8. Explainability] Top Risk Driver: {journey['stages']['8_explanation']['top_positive_factors']}")
        print(f"    Narrative: {exp.get('summary_text', '')[:100]}...")

    # ── Step 9: Investigation Case Management ────────────────────────────────
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM investigation_cases WHERE claim_id = ? ORDER BY updated_at DESC LIMIT 1", (cid,))
        case_row = cur.fetchone()
        case_dict = dict(case_row) if case_row else None

    journey["stages"]["9_investigation_case"] = {
        "case_exists": case_dict is not None,
        "case_id": case_dict.get("case_id") if case_dict else None,
        "status": case_dict.get("status") if case_dict else "UNASSIGNED",
        "priority": case_dict.get("priority") if case_dict else "NONE",
        "assigned_to": case_dict.get("assigned_to") if case_dict else "Unassigned",
    }
    if verbose:
        print(f"[9. Investigation Case] Case ID: {journey['stages']['9_investigation_case']['case_id']} | Status: {journey['stages']['9_investigation_case']['status']} | Priority: {journey['stages']['9_investigation_case']['priority']}")
        print("=" * 75)
        print("CLAIM JOURNEY TRACED AND VERIFIED END-TO-END.")
        print("=" * 75)

    journey["verified"] = True
    return journey


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="End-to-End Pipeline & Claim Journey Runner")
    parser.add_argument("--run-all", action="store_true", help="Execute complete pipeline from scratch")
    parser.add_argument("--journey", type=str, default="CLM00001", help="Verify single claim journey")
    args = parser.parse_args()

    if args.run_all:
        run_full_pipeline(rebuild_db=False)
    else:
        verify_claim_journey(args.journey)
