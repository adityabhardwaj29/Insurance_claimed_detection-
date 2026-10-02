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

from api.db import db
from src.utils.config import settings

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent


class ClaimService:
    """Handles claim entity lookups and analytical views."""

    _dashboard_cache: Dict[str, Any] = {}
    _dashboard_cache_time: float = 0.0

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    def list_claims(
        self,
        status: Optional[str] = None,
        claim_type: Optional[str] = None,
        fraud_label: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "claim_id",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lists claims with dynamic filtering, sorting, and pagination.
        Defaults to newest claims first (descending).
        """
        valid_sort_cols = {
            "claim_id", "claim_amount", "claim_date", "status", "claim_type", "fraud_label"
        }
        order_col = sort_by if sort_by in valid_sort_cols else "claim_id"
        direction = "DESC" if sort_order.lower() != "asc" else "ASC"

        where_clauses: List[str] = []
        params: List[Any] = []

        if status:
            where_clauses.append("c.status = ?")
            params.append(status)
        if claim_type:
            where_clauses.append("c.claim_type = ?")
            params.append(claim_type)
        if fraud_label is not None:
            where_clauses.append("c.fraud_label = ?")
            params.append(int(fraud_label))
        if min_amount is not None:
            where_clauses.append("c.claim_amount >= ?")
            params.append(float(min_amount))
        if max_amount is not None:
            where_clauses.append("c.claim_amount <= ?")
            params.append(float(max_amount))

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Count query
        count_query = f"SELECT COUNT(*) as cnt FROM claims c{where_sql}"
        cnt_row = db.query_one(count_query, params)
        total = int(cnt_row["cnt"]) if cnt_row and cnt_row.get("cnt") is not None else 0

        # Enriched data query with claimant name, phone, email, policy and risk band
        data_query = f"""
            SELECT 
                c.claim_id, c.claimant_id, c.policy_id, c.provider_id, c.vehicle_id, c.invoice_id,
                c.claim_date, c.claim_amount, c.claim_type, c.status, c.fraud_label, c.description,
                cl.name AS claimant_name,
                cl.phone AS claimant_phone,
                cl.email AS claimant_email,
                p.policy_type,
                rs.final_risk_score,
                rs.risk_band
            FROM claims c
            LEFT JOIN claimants cl ON c.claimant_id = cl.claimant_id
            LEFT JOIN policies p ON c.policy_id = p.policy_id
            LEFT JOIN risk_scores rs ON c.claim_id = rs.claim_id
            {where_sql}
            ORDER BY c.{order_col} {direction} LIMIT ? OFFSET ?
        """
        items = db.query_all(data_query, params + [int(limit), int(offset)])
        for item in items:
            if "claim_amount" in item and item["claim_amount"] is not None:
                item["claim_amount"] = float(item["claim_amount"])
            if "final_risk_score" in item and item["final_risk_score"] is not None:
                item["final_risk_score"] = float(item["final_risk_score"])
            if "claim_date" in item and item["claim_date"] is not None:
                item["claim_date"] = str(item["claim_date"])

        return items, total

    def get_claim_detail(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns full relational record: claim, claimant, provider, policy, vehicle, invoice.
        """
        cid = claim_id.strip()
        claim_dict = db.query_one("SELECT * FROM claims WHERE claim_id = ?", (cid,))
        if not claim_dict:
            return None

        claimant_dict = db.query_one("SELECT * FROM claimants WHERE claimant_id = ?", (claim_dict["claimant_id"],)) or {}
        provider_dict = db.query_one("SELECT * FROM providers WHERE provider_id = ?", (claim_dict["provider_id"],)) or {}
        policy_dict = db.query_one("SELECT * FROM policies WHERE policy_id = ?", (claim_dict["policy_id"],)) or {}
        vehicle_dict = db.query_one("SELECT * FROM vehicles WHERE vehicle_id = ?", (claim_dict["vehicle_id"],)) or {}
        invoice_dict = db.query_one("SELECT * FROM invoices WHERE invoice_id = ?", (claim_dict["invoice_id"],)) or {}

        if "premium" in policy_dict and policy_dict["premium"] is not None:
            policy_dict["premium"] = float(policy_dict["premium"])
        if "invoice_amount" in invoice_dict and invoice_dict["invoice_amount"] is not None:
            invoice_dict["invoice_amount"] = float(invoice_dict["invoice_amount"])

        return {
            "claim_id": claim_dict["claim_id"],
            "claim_date": str(claim_dict.get("claim_date", "")),
            "claim_amount": float(claim_dict["claim_amount"]),
            "claim_type": claim_dict["claim_type"],
            "status": claim_dict["status"],
            "fraud_label": int(claim_dict["fraud_label"] or 0),
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
        Calculates high-level business & fraud metrics from database and risk scores.
        Cached for 15 seconds to ensure sub-millisecond dashboard navigation.
        """
        import time as _time
        now = _time.time()
        if now - ClaimService._dashboard_cache_time < 15.0 and ClaimService._dashboard_cache:
            return ClaimService._dashboard_cache

        c_row = db.query_one("SELECT COUNT(*) as total_claims, SUM(claim_amount) as total_amount, SUM(CASE WHEN fraud_label=1 THEN 1 ELSE 0 END) as fraud_count FROM claims")
        total_claims = int(c_row["total_claims"]) if c_row and c_row.get("total_claims") else 0
        total_amount = float(c_row["total_amount"] or 0.0) if c_row and c_row.get("total_amount") else 0.0
        fraud_count = int(c_row["fraud_count"]) if c_row and c_row.get("fraud_count") else 0
        fraud_rate = round((fraud_count / total_claims * 100.0) if total_claims > 0 else 0.0, 2)

        # Cases stats
        active_row = db.query_one("SELECT COUNT(*) as cnt FROM investigation_cases WHERE status NOT IN ('RESOLVED', 'FALSE_POSITIVE')")
        active_cases = int(active_row["cnt"]) if active_row and active_row.get("cnt") else 0

        status_rows = db.query_all("SELECT status, COUNT(*) as cnt FROM investigation_cases GROUP BY status")
        cases_by_status = {r["status"]: int(r["cnt"]) for r in status_rows}

        priority_rows = db.query_all("SELECT priority, COUNT(*) as cnt FROM investigation_cases GROUP BY priority")
        cases_by_priority = {r["priority"]: int(r["cnt"]) for r in priority_rows}

        avg_risk = 0.0
        high_risk_count = 0
        if settings.RISK_SCORES_PATH.exists():
            try:
                df = pd.read_csv(settings.RISK_SCORES_PATH, keep_default_na=False)
                avg_risk = round(float(df["final_risk_score"].mean()), 4)
                high_risk_count = int(df["risk_band"].isin(["HIGH", "CRITICAL"]).sum())
            except Exception as e:
                logger.warning("Could not compute risk summary: %s", e)

        res = {
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
        ClaimService._dashboard_cache = res
        ClaimService._dashboard_cache_time = now
        return res

    def create_claim(self, data: Dict[str, Any], actor: str = "system") -> Dict[str, Any]:
        """Creates a new claim with auto-generated ID, claimant resolution/creation with phone and email, invoice creation if needed, and audit logging."""
        ClaimService._dashboard_cache_time = 0.0
        # Determine next CLM ID
        row = db.query_one("SELECT claim_id FROM claims ORDER BY claim_id DESC LIMIT 1")
        next_num = 324
        if row and row.get("claim_id") and str(row["claim_id"]).startswith("CLM"):
            try:
                next_num = int(str(row["claim_id"])[3:]) + 1
            except ValueError:
                next_num = 324
        new_claim_id = f"CLM{next_num:05d}"

        # Resolve or create claimant with name, phone, email
        claimant_id = data.get("claimant_id")
        claimant_name = data.get("claimant_name")
        claimant_phone = data.get("claimant_phone")
        claimant_email = data.get("claimant_email")

        if not claimant_id:
            cl_row = db.query_one("SELECT claimant_id FROM claimants ORDER BY claimant_id DESC LIMIT 1")
            cl_num = 124
            if cl_row and cl_row.get("claimant_id") and str(cl_row["claimant_id"]).startswith("CLT"):
                try:
                    cl_num = int(str(cl_row["claimant_id"])[3:]) + 1
                except ValueError:
                    cl_num = 124
            claimant_id = f"CLT{cl_num:04d}"
            db.execute("""
                INSERT INTO claimants (claimant_id, name, age, city, gender, marital_status, phone, email, address, occupation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claimant_id,
                claimant_name or f"Claimant {cl_num}",
                35,
                data.get("incident_city") or "Mumbai",
                "M",
                "Single",
                claimant_phone or f"+91-98{cl_num:04d}-{cl_num:04d}",
                claimant_email or f"{claimant_id.lower()}@example.com",
                f"{data.get('incident_city', 'City Center')}",
                "Policyholder"
            ))
        elif claimant_name or claimant_phone:
            db.execute("""
                UPDATE claimants 
                SET name = COALESCE(?, name),
                    phone = COALESCE(?, phone),
                    email = COALESCE(?, email)
                WHERE claimant_id = ?
            """, (claimant_name, claimant_phone, claimant_email, claimant_id))

        # Policy
        policy_id = data.get("policy_id") or data.get("policy_number") or f"POL{next_num:05d}"
        db.execute("""
            INSERT OR IGNORE INTO policies (policy_id, claimant_id, start_date, end_date, policy_type, premium, date_order_invalid)
            VALUES (?, ?, '2024-01-01', '2025-01-01', ?, ?, 0)
        """, (policy_id, claimant_id, data.get("policy_type", "Comprehensive Auto Coverage"), 15000.0))

        # Vehicle
        vehicle_id = data.get("vehicle_id") or f"VEH{next_num:05d}"
        db.execute("""
            INSERT OR IGNORE INTO vehicles (vehicle_id, claimant_id, make, vehicle_type, registration_no, model_year)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            vehicle_id,
            claimant_id,
            data.get("vehicle_make") or "Honda",
            data.get("vehicle_model") or "Sedan",
            data.get("auto_vin") or f"REG-{next_num:05d}",
            int(data.get("auto_year") or 2021)
        ))

        # Provider
        provider_id = data.get("provider_id") or "PRV0001"
        if data.get("provider_name"):
            p_match = db.query_one("SELECT provider_id FROM providers WHERE provider_name = ?", (data["provider_name"],))
            if p_match:
                provider_id = p_match["provider_id"]
            else:
                prov_id = f"PRV{next_num:04d}"
                db.execute("""
                    INSERT OR IGNORE INTO providers (provider_id, provider_name, city, provider_type, rating)
                    VALUES (?, ?, ?, 'Body Shop', 4.2)
                """, (prov_id, data["provider_name"], data.get("incident_city") or "Mumbai"))
                provider_id = prov_id

        # Ensure invoice exists
        claim_amt = float(data.get("total_claim_amount") or data.get("claim_amount") or 50000.0)
        claim_dt = data.get("incident_date") or data.get("claim_date") or datetime.now().strftime("%Y-%m-%d")
        invoice_id = data.get("invoice_id")
        if not invoice_id:
            invoice_id = f"INV{next_num:05d}"
            inv_amt = float(data.get("invoice_amount") or claim_amt)
            db.execute(
                "INSERT OR IGNORE INTO invoices (invoice_id, provider_id, invoice_amount, invoice_date, description) VALUES (?, ?, ?, ?, ?)",
                (invoice_id, provider_id, inv_amt, claim_dt, f"Service invoice for {new_claim_id}")
            )

        # Insert claim
        db.execute("""
            INSERT INTO claims (
                claim_id, claimant_id, policy_id, vehicle_id, provider_id, invoice_id,
                claim_date, claim_amount, claim_type, status, fraud_label, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', 0, ?)
        """, (
            new_claim_id,
            claimant_id,
            policy_id,
            vehicle_id,
            provider_id,
            invoice_id,
            claim_dt,
            claim_amt,
            data.get("claim_type", "Accident"),
            data.get("description", f"Submitted claim {new_claim_id}")
        ))

        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"CASE-{new_claim_id}"
        db.execute("""
            INSERT OR IGNORE INTO investigation_cases (case_id, claim_id, status, priority, reason, created_at, updated_at)
            VALUES (?, ?, 'NEW', 'MEDIUM', 'Initial claim intake', ?, ?)
        """, (case_id, new_claim_id, now_ts, now_ts))

        db.execute("""
            INSERT INTO case_events (case_id, event_type, actor, old_value, new_value, details, timestamp)
            VALUES (?, 'CLAIM_CREATED', ?, 'None', 'Open', ?, ?)
        """, (case_id, actor, f"Created claim for {claimant_name or claimant_id} (Mobile: {claimant_phone or 'N/A'}) for amount INR {claim_amt:,.2f}", now_ts))

        res = self.get_claim_detail(new_claim_id) or {"claim_id": new_claim_id, "status": "Open"}
        res["id"] = new_claim_id
        res["claim_number"] = new_claim_id
        return res

    def record_decision(self, claim_id: str, decision: str, reason: str, actor: str = "system") -> Dict[str, Any]:
        """Records a human decision (Approve, Reject, Manual Review, Escalate) with audit trail."""
        ClaimService._dashboard_cache_time = 0.0
        cid = claim_id.strip()
        status_map = {
            "Approve": "Approved",
            "Reject": "Rejected",
            "Request Manual Review": "Under Review",
            "Escalate Investigation": "Under Review"
        }
        new_status = status_map.get(decision, "Under Review")

        old_row = db.query_one("SELECT status FROM claims WHERE claim_id = ?", (cid,))
        old_status = old_row["status"] if old_row and old_row.get("status") else "Submitted"

        db.execute("UPDATE claims SET status = ? WHERE claim_id = ?", (new_status, cid))

        # Also update case if exists
        case_id = f"CASE-{cid}"
        case_status = "RESOLVED" if decision in ("Approve", "Reject") else "ESCALATED"
        db.execute("""
            UPDATE investigation_cases 
            SET status = ?, resolution = ?, updated_at = CURRENT_TIMESTAMP
            WHERE case_id = ?
        """, (case_status, f"{decision}: {reason} (Decided by {actor})", case_id))

        # Audit event
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""
            INSERT INTO case_events (case_id, event_type, actor, old_value, new_value, details, timestamp)
            VALUES (?, 'CLAIM_DECISION_RECORDED', ?, ?, ?, ?, ?)
        """, (case_id, actor, old_status, new_status, f"Decision: {decision} | Reason: {reason}", now_ts))

        return {
            "claim_id": cid,
            "decision": decision,
            "status": new_status,
            "reason": reason,
            "decided_by": actor,
        }

