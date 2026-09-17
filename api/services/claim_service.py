"""
api/services/claim_service.py
-----------------------------
Service layer for claim queries, relational entity lookups, risk details,
duplicate detection metrics, and explainability.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.utils.config import settings

logger = logging.getLogger(__name__)


class ClaimService:
    """Handles claim entity lookups and analytical views."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_claims(
        self,
        status: Optional[str] = None,
        claim_type: Optional[str] = None,
        fraud_label: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "claim_id",
        sort_order: str = "asc",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lists claims with dynamic filtering, sorting, and pagination.
        """
        valid_sort_cols = {
            "claim_id", "claim_amount", "claim_date", "status", "claim_type", "fraud_label"
        }
        order_col = sort_by if sort_by in valid_sort_cols else "claim_id"
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        where_clauses: List[str] = []
        params: List[Any] = []

        if status:
            where_clauses.append("status = ?")
            params.append(status)
        if claim_type:
            where_clauses.append("claim_type = ?")
            params.append(claim_type)
        if fraud_label is not None:
            where_clauses.append("fraud_label = ?")
            params.append(int(fraud_label))
        if min_amount is not None:
            where_clauses.append("claim_amount >= ?")
            params.append(float(min_amount))
        if max_amount is not None:
            where_clauses.append("claim_amount <= ?")
            params.append(float(max_amount))

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        with self._get_connection() as conn:
            cur = conn.cursor()

            # Count query
            count_query = f"SELECT COUNT(*) FROM claims{where_sql}"
            cur.execute(count_query, params)
            total = cur.fetchone()[0]

            # Data query
            data_query = (
                f"SELECT * FROM claims{where_sql} "
                f"ORDER BY {order_col} {direction} LIMIT ? OFFSET ?"
            )
            cur.execute(data_query, params + [int(limit), int(offset)])
            items = [dict(r) for r in cur.fetchall()]

        return items, total

    def get_claim_detail(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns full relational record: claim, claimant, provider, policy, vehicle, invoice.
        """
        cid = claim_id.strip()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM claims WHERE claim_id = ?", (cid,))
            c_row = cur.fetchone()
            if not c_row:
                return None
            claim_dict = dict(c_row)

            # Claimant
            cur.execute("SELECT * FROM claimants WHERE claimant_id = ?", (claim_dict["claimant_id"],))
            clt = cur.fetchone()
            claimant_dict = dict(clt) if clt else {}

            # Provider
            cur.execute("SELECT * FROM providers WHERE provider_id = ?", (claim_dict["provider_id"],))
            prv = cur.fetchone()
            provider_dict = dict(prv) if prv else {}

            # Policy
            cur.execute("SELECT * FROM policies WHERE policy_id = ?", (claim_dict["policy_id"],))
            pol = cur.fetchone()
            policy_dict = dict(pol) if pol else {}

            # Vehicle
            cur.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (claim_dict["vehicle_id"],))
            veh = cur.fetchone()
            vehicle_dict = dict(veh) if veh else {}

            # Invoice
            cur.execute("SELECT * FROM invoices WHERE invoice_id = ?", (claim_dict["invoice_id"],))
            inv = cur.fetchone()
            invoice_dict = dict(inv) if inv else {}

        return {
            "claim_id": claim_dict["claim_id"],
            "claim_date": claim_dict.get("claim_date"),
            "claim_amount": float(claim_dict["claim_amount"]),
            "claim_type": claim_dict["claim_type"],
            "status": claim_dict["status"],
            "fraud_label": int(claim_dict["fraud_label"]),
            "description": claim_dict.get("description"),
            "claimant": claimant_dict,
            "provider": provider_dict,
            "policy": policy_dict,
            "vehicle": vehicle_dict,
            "invoice": invoice_dict,
        }

    def get_claim_risk(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Returns Phase 8 risk score, risk band, component scores, and reasons."""
        cid = claim_id.strip()
        if not settings.RISK_SCORES_PATH.exists():
            return None

        df = pd.read_csv(settings.RISK_SCORES_PATH, keep_default_na=False)
        match = df[df["claim_id"] == cid]
        if match.empty:
            return None

        r = match.iloc[0]
        reasons_str = str(r.get("risk_reasons", ""))
        reasons_list = [rs.strip() for rs in reasons_str.split("|") if rs.strip()]

        return {
            "claim_id": cid,
            "final_risk_score": float(r["final_risk_score"]),
            "risk_band": str(r["risk_band"]),
            "fraud_probability": float(r["fraud_probability"]),
            "anomaly_score": float(r["anomaly_score"]),
            "duplicate_score": float(r["duplicate_score"]),
            "graph_risk_score": float(r["graph_risk_score"]),
            "risk_reasons": reasons_list,
        }

    def get_claim_duplicates(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Returns Phase 3 duplicate detection analysis for claim."""
        cid = claim_id.strip()
        dup_file = settings.ROOT / "data" / "features" / "duplicate_features.csv"
        if not dup_file.exists():
            return None

        df = pd.read_csv(dup_file, keep_default_na=False)
        match = df[df["claim_id"] == cid]
        if match.empty:
            return None

        r = match.iloc[0]
        sim_score = float(r.get("duplicate_similarity_score", r.get("dup_similarity_score", 0.0)))
        dup_type = str(r.get("duplicate_type", r.get("dup_type", "NONE")))
        matched_id = r.get("matched_claim_id")
        if pd.isna(matched_id) or not str(matched_id).strip():
            matched_id = None
        else:
            matched_id = str(matched_id).strip()

        is_dup = int(r.get("is_duplicate_flag", 1 if sim_score >= 0.50 else 0))

        # Determine matching attributes if present
        matching_attrs = []
        if sim_score > 0.40:
            matching_attrs.append("claim_amount")
        if sim_score > 0.50:
            matching_attrs.append("vehicle_make_type")
        if sim_score > 0.60:
            matching_attrs.append("provider_location")

        return {
            "claim_id": cid,
            "duplicate_similarity_score": round(sim_score, 4),
            "dup_type": dup_type,
            "matched_claim_id": matched_id,
            "is_duplicate_flag": is_dup,
            "matching_attributes": matching_attrs,
        }

    def get_claim_explanation(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Compiles explainable evidence factors, weights, and narrative explanation.
        """
        risk_data = self.get_claim_risk(claim_id)
        if not risk_data:
            return None

        weights = {
            "fraud_probability": 0.45,
            "anomaly_score": 0.25,
            "duplicate_score": 0.15,
            "graph_risk_score": 0.15,
        }

        signals = {
            "fraud_probability": risk_data["fraud_probability"],
            "anomaly_score": risk_data["anomaly_score"],
            "duplicate_score": risk_data["duplicate_score"],
            "graph_risk_score": risk_data["graph_risk_score"],
        }

        score = risk_data["final_risk_score"]
        band = risk_data["risk_band"]
        reasons = risk_data["risk_reasons"]

        summary = (
            f"Claim {claim_id} is classified as {band} risk (score: {score:.4f}). "
            f"Key driving signals: ML fraud probability={signals['fraud_probability']:.2f} (weight 45%), "
            f"unsupervised anomaly={signals['anomaly_score']:.2f} (weight 25%), "
            f"duplicate similarity={signals['duplicate_score']:.2f} (weight 15%), "
            f"graph risk={signals['graph_risk_score']:.2f} (weight 15%)."
        )
        if reasons:
            summary += f" Specific risk triggers detected: {len(reasons)} factor(s)."

        return {
            "claim_id": claim_id,
            "final_risk_score": score,
            "risk_band": band,
            "signals": signals,
            "weights": weights,
            "reasons": reasons,
            "summary": summary,
        }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Calculates high-level business & fraud metrics from SQLite DB and risk scores.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), SUM(claim_amount), SUM(CASE WHEN fraud_label=1 THEN 1 ELSE 0 END) FROM claims")
            c_row = cur.fetchone()
            total_claims = c_row[0] or 0
            total_amount = float(c_row[1] or 0.0)
            fraud_count = c_row[2] or 0
            fraud_rate = round((fraud_count / total_claims * 100.0) if total_claims > 0 else 0.0, 2)

            # Cases stats
            cur.execute("SELECT COUNT(*) FROM investigation_cases WHERE status NOT IN ('RESOLVED', 'FALSE_POSITIVE')")
            active_cases = cur.fetchone()[0] or 0

            cur.execute("SELECT status, COUNT(*) FROM investigation_cases GROUP BY status")
            cases_by_status = dict(cur.fetchall())

            cur.execute("SELECT priority, COUNT(*) FROM investigation_cases GROUP BY priority")
            cases_by_priority = dict(cur.fetchall())

        avg_risk = 0.0
        high_risk_count = 0
        if settings.RISK_SCORES_PATH.exists():
            try:
                df = pd.read_csv(settings.RISK_SCORES_PATH, keep_default_na=False)
                avg_risk = round(float(df["final_risk_score"].mean()), 4)
                high_risk_count = int(df["risk_band"].isin(["HIGH", "CRITICAL"]).sum())
            except Exception as e:
                logger.warning("Could not compute risk summary: %s", e)

        return {
            "total_claims": total_claims,
            "total_claim_amount": round(total_amount, 2),
            "fraud_claims_count": fraud_count,
            "fraud_rate_pct": fraud_rate,
            "active_cases_count": active_cases,
            "cases_by_status": cases_by_status,
            "cases_by_priority": cases_by_priority,
            "average_risk_score": avg_risk,
            "high_risk_claims_count": high_risk_count,
        }
