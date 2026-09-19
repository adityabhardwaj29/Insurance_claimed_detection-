"""
api/services/customer_service.py
--------------------------------
Service for customer/claimant management, identity lookups, and 360-degree risk profiling.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from api.db import db
from api.schemas.customer_schema import CustomerCreate

logger = logging.getLogger(__name__)


class CustomerService:
    """Handles customer lookup, creation, and relational 360 profile synthesis."""

    @staticmethod
    def search_customers(query: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Searches claimants across ID, name, city, phone, and email."""
        if query and query.strip():
            q = f"%{query.strip().lower()}%"
            sql = """
                SELECT * FROM claimants 
                WHERE lower(claimant_id) LIKE ? 
                   OR lower(name) LIKE ? 
                   OR lower(city) LIKE ? 
                   OR lower(phone) LIKE ? 
                   OR lower(email) LIKE ?
                ORDER BY claimant_id ASC 
                LIMIT ? OFFSET ?
            """
            return db.query_all(sql, (q, q, q, q, q, limit, offset))

        sql = "SELECT * FROM claimants ORDER BY claimant_id ASC LIMIT ? OFFSET ?"
        return db.query_all(sql, (limit, offset))

    @staticmethod
    def get_customer_by_id(claimant_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single claimant record."""
        return db.query_one("SELECT * FROM claimants WHERE claimant_id = ?", (claimant_id.strip(),))

    @staticmethod
    def create_customer(data: CustomerCreate) -> Dict[str, Any]:
        """Creates a new claimant/customer record with auto-sequenced ID."""
        # Find highest ID
        rows = db.query_all("SELECT claimant_id FROM claimants ORDER BY claimant_id DESC LIMIT 1")
        next_num = 1
        if rows:
            latest = rows[0]["claimant_id"]
            if latest.startswith("CLT"):
                try:
                    next_num = int(latest[3:]) + 1
                except ValueError:
                    next_num = 121
        new_id = f"CLT{next_num:04d}"

        sql = """
            INSERT INTO claimants (claimant_id, name, age, city, gender, marital_status, phone, email, address, occupation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        db.execute(sql, (
            new_id,
            data.name,
            data.age,
            data.city,
            data.gender,
            data.marital_status,
            data.phone or f"+91-98{next_num:04d}",
            data.email or f"{data.name.lower().replace(' ', '.')}@example.com",
            data.address,
            data.occupation,
        ))

        return CustomerService.get_customer_by_id(new_id) or {"claimant_id": new_id, "name": data.name}

    @staticmethod
    def get_customer_360(claimant_id: str) -> Optional[Dict[str, Any]]:
        """Synthesizes customer 360 view with policies, vehicles, claims, and fraud risk history."""
        cust = CustomerService.get_customer_by_id(claimant_id)
        if not cust:
            return None

        cid = claimant_id.strip()
        policies = db.query_all("SELECT * FROM policies WHERE claimant_id = ? ORDER BY start_date DESC", (cid,))
        vehicles = db.query_all("SELECT * FROM vehicles WHERE claimant_id = ?", (cid,))
        claims = db.query_all("""
            SELECT c.*, r.final_risk_score, r.risk_band 
            FROM claims c 
            LEFT JOIN risk_scores r ON c.claim_id = r.claim_id
            WHERE c.claimant_id = ? 
            ORDER BY c.claim_date DESC
        """, (cid,))

        total_claims_count = len(claims)
        total_claim_amount = sum(float(c.get("claim_amount") or 0.0) for c in claims)
        fraud_alert_count = sum(
            1 for c in claims 
            if c.get("fraud_label") == 1 or c.get("risk_band") in ("HIGH", "CRITICAL")
        )

        return {
            "customer": cust,
            "policies": policies,
            "vehicles": vehicles,
            "claims": claims,
            "total_claims_count": total_claims_count,
            "total_claim_amount": total_claim_amount,
            "fraud_alert_count": fraud_alert_count,
        }
