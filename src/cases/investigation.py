"""
src/cases/investigation.py
--------------------------
Compiles comprehensive investigator dossiers and evidence summaries.
Assembles relational claim records, entity relationships, model sub-scores,
and chronological case history for human investigator review.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.cases.case_manager import CaseManager, DEFAULT_DB

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


def build_investigation_dossier(
    case_id: str,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Builds a full evidence dossier for an investigator reviewing a flagged claim.

    Parameters
    ----------
    case_id : str
        The unique case identifier (e.g., 'CASE-CLM00001').
    db_path : Path, optional
        Path to SQLite database file.

    Returns
    -------
    dict with:
      - case: Case record metadata
      - claim: Core claim fact attributes
      - claimant: Individual background and demographics
      - provider: Repair/medical provider details & rating
      - policy: Policy coverage terms & dates
      - vehicle: Vehicle characteristics
      - invoice: Associated billing invoice
      - risk_breakdown: Multi-signal risk decomposition
      - timeline: Chronological history of investigator notes & state transitions
    """
    manager = CaseManager(db_path=db_path)
    case = manager.get_case(case_id)
    if not case:
        raise KeyError(f"Investigation case '{case_id}' not found")

    cid = case.claim_id
    history = manager.get_case_history(case_id)

    db_file = Path(db_path) if db_path else DEFAULT_DB
    claim_details: Dict[str, Any] = {}
    claimant_details: Dict[str, Any] = {}
    provider_details: Dict[str, Any] = {}
    policy_details: Dict[str, Any] = {}
    vehicle_details: Dict[str, Any] = {}
    invoice_details: Dict[str, Any] = {}

    if db_file.exists():
        with sqlite3.connect(db_file) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Claim query
            cur.execute("SELECT * FROM claims WHERE claim_id = ?", (cid,))
            row = cur.fetchone()
            if row:
                claim_details = dict(row)
                pid = row["policy_id"]
                clt_id = row["claimant_id"]
                prv_id = row["provider_id"]
                veh_id = row["vehicle_id"]
                inv_id = row["invoice_id"]

                # Claimant
                cur.execute("SELECT * FROM claimants WHERE claimant_id = ?", (clt_id,))
                clt_row = cur.fetchone()
                if clt_row:
                    claimant_details = dict(clt_row)

                # Provider
                cur.execute("SELECT * FROM providers WHERE provider_id = ?", (prv_id,))
                prv_row = cur.fetchone()
                if prv_row:
                    provider_details = dict(prv_row)

                # Policy
                cur.execute("SELECT * FROM policies WHERE policy_id = ?", (pid,))
                pol_row = cur.fetchone()
                if pol_row:
                    policy_details = dict(pol_row)

                # Vehicle
                cur.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (veh_id,))
                veh_row = cur.fetchone()
                if veh_row:
                    vehicle_details = dict(veh_row)

                # Invoice
                cur.execute("SELECT * FROM invoices WHERE invoice_id = ?", (inv_id,))
                inv_row = cur.fetchone()
                if inv_row:
                    invoice_details = dict(inv_row)

    # Risk signals breakdown from Phase 8 output
    risk_breakdown: Dict[str, Any] = {
        "final_risk_score": case.risk_score,
        "risk_band": case.risk_band,
        "priority": case.priority,
        "reasons": case.reason.split(" | ") if case.reason else [],
    }

    risk_file = ROOT / "data" / "features" / "final_risk_scores.csv"
    if risk_file.exists():
        try:
            scores_df = pd.read_csv(risk_file, keep_default_na=False)
            match = scores_df[scores_df["claim_id"] == cid]
            if not match.empty:
                r = match.iloc[0]
                risk_breakdown.update({
                    "fraud_probability": float(r.get("fraud_probability", 0.0)),
                    "anomaly_score": float(r.get("anomaly_score", 0.0)),
                    "duplicate_score": float(r.get("duplicate_score", 0.0)),
                    "graph_risk_score": float(r.get("graph_risk_score", 0.0)),
                })
        except Exception as e:
            logger.warning("Could not read risk breakdown: %s", e)

    return {
        "case": case.to_dict(),
        "claim": claim_details,
        "claimant": claimant_details,
        "provider": provider_details,
        "policy": policy_details,
        "vehicle": vehicle_details,
        "invoice": invoice_details,
        "risk_breakdown": risk_breakdown,
        "notes": history["notes"],
        "events": history["events"],
    }


def investigation_summary(claim: Any, signals: Any) -> Dict[str, Any]:
    """
    Backwards-compatible investigation summary helper.
    """
    return {
        "claim": claim,
        "signals": signals,
        "review_required": True,
        "human_decision_pending": True,
    }
