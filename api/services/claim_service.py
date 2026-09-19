"""
api/services/claim_service.py
-----------------------------
Service layer for claim queries, relational entity lookups, risk details,
duplicate detection metrics, and explainability.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.utils.config import settings

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


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

        # Load Phase 12 SHAP & Graph explanations if available
        exp_file = ROOT / "data" / "features" / "claim_explanations.json"
        top_factors = []
        top_pos = []
        top_neg = []
        graph_exp = {}
        if exp_file.exists():
            try:
                import json
                with open(exp_file, "r", encoding="utf-8") as f:
                    all_exp = json.load(f)
                    if claim_id in all_exp:
                        e = all_exp[claim_id]
                        top_factors = e.get("top_factors", [])
                        top_pos = e.get("top_positive_factors", [])
                        top_neg = e.get("top_negative_factors", [])
                        graph_exp = e.get("graph_explanation", {})
            except Exception:
                pass

        return {
            "claim_id": claim_id,
            "final_risk_score": score,
            "risk_band": band,
            "signals": signals,
            "weights": weights,
            "reasons": reasons,
            "summary": summary,
            "fraud_probability": signals["fraud_probability"],
            "top_factors": top_factors,
            "top_positive_factors": top_pos,
            "top_negative_factors": top_neg,
            "graph_explanation": graph_exp,
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

    def create_claim(self, data: Dict[str, Any], actor: str = "system") -> Dict[str, Any]:
        """Creates a new claim with auto-generated ID, invoice creation if needed, and audit logging."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Determine next CLM ID
            cur.execute("SELECT claim_id FROM claims ORDER BY claim_id DESC LIMIT 1")
            row = cur.fetchone()
            next_num = 321
            if row and row[0].startswith("CLM"):
                try:
                    next_num = int(row[0][3:]) + 1
                except ValueError:
                    next_num = 321
            new_claim_id = f"CLM{next_num:05d}"

            # Ensure invoice exists
            invoice_id = data.get("invoice_id")
            if not invoice_id:
                invoice_id = f"INV{next_num:05d}"
                inv_amt = float(data.get("invoice_amount") or data.get("claim_amount") or 10000.0)
                cur.execute(
                    "INSERT OR IGNORE INTO invoices (invoice_id, provider_id, invoice_amount, invoice_date, description) VALUES (?, ?, ?, ?, ?)",
                    (invoice_id, data["provider_id"], inv_amt, data["claim_date"], f"Service invoice for {new_claim_id}")
                )

            # Insert claim
            cur.execute("""
                INSERT INTO claims (
                    claim_id, claimant_id, policy_id, vehicle_id, provider_id, invoice_id,
                    claim_date, claim_amount, claim_type, status, fraud_label, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', 0, ?)
            """, (
                new_claim_id,
                data["claimant_id"],
                data["policy_id"],
                data["vehicle_id"],
                data["provider_id"],
                invoice_id,
                data["claim_date"],
                float(data["claim_amount"]),
                data.get("claim_type", "Accident"),
                data.get("description", f"Submitted claim {new_claim_id}")
            ))

            # Record event
            cur.execute("""
                CREATE TABLE IF NOT EXISTS case_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id VARCHAR(30),
                    event_type TEXT,
                    actor TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            case_id = f"CASE-{new_claim_id}"
            cur.execute("""
                INSERT OR IGNORE INTO investigation_cases (case_id, claim_id, status, priority, reason, created_at, updated_at)
                VALUES (?, ?, 'NEW', 'MEDIUM', 'Initial claim intake', ?, ?)
            """, (case_id, new_claim_id, now_ts, now_ts))

            cur.execute("""
                INSERT INTO case_events (case_id, event_type, actor, old_value, new_value, details, timestamp)
                VALUES (?, 'CLAIM_CREATED', ?, 'None', 'Open', ?, ?)
            """, (case_id, actor, f"Created claim for amount INR {float(data['claim_amount']):,.2f}", now_ts))

            conn.commit()

        return self.get_claim_detail(new_claim_id) or {"claim_id": new_claim_id, "status": "Open"}

    def record_decision(self, claim_id: str, decision: str, reason: str, actor: str = "system") -> Dict[str, Any]:
        """Records a human decision (Approve, Reject, Manual Review, Escalate) with audit trail."""
        cid = claim_id.strip()
        status_map = {
            "Approve": "Approved",
            "Reject": "Rejected",
            "Request Manual Review": "Under Review",
            "Escalate Investigation": "Under Review"
        }
        new_status = status_map.get(decision, "Under Review")

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM claims WHERE claim_id = ?", (cid,))
            old_row = cur.fetchone()
            old_status = old_row[0] if old_row else "Submitted"

            cur.execute("UPDATE claims SET status = ? WHERE claim_id = ?", (new_status, cid))

            # Also update case if exists
            case_id = f"CASE-{cid}"
            case_status = "RESOLVED" if decision in ("Approve", "Reject") else "ESCALATED"
            cur.execute("""
                UPDATE investigation_cases 
                SET status = ?, resolution = ?, updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
            """, (case_status, f"{decision}: {reason} (Decided by {actor})", case_id))

            # Audit event
            now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO case_events (case_id, event_type, actor, old_value, new_value, details, timestamp)
                VALUES (?, 'CLAIM_DECISION_RECORDED', ?, ?, ?, ?, ?)
            """, (case_id, actor, old_status, new_status, f"Decision: {decision} | Reason: {reason}", now_ts))

            conn.commit()

        return {
            "claim_id": cid,
            "decision": decision,
            "status": new_status,
            "reason": reason,
            "decided_by": actor,
        }

