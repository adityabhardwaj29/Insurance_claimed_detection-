"""
api/services/policy_service.py
------------------------------
Service for policy administration and automated coverage eligibility verification.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.db import db
from api.schemas.policy_schema import PolicyCreate, PolicyVerifyResponse

logger = logging.getLogger(__name__)


class PolicyService:
    """Manages policy lookups, creation, and automated underwriting checks."""

    @staticmethod
    def list_policies(claimant_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Lists policies, optionally filtered by claimant."""
        if claimant_id:
            return db.query_all(
                "SELECT * FROM policies WHERE claimant_id = ? ORDER BY start_date DESC LIMIT ? OFFSET ?",
                (claimant_id.strip(), limit, offset)
            )
        return db.query_all("SELECT * FROM policies ORDER BY policy_id ASC LIMIT ? OFFSET ?", (limit, offset))

    @staticmethod
    def get_policy_by_id(policy_id: str) -> Optional[Dict[str, Any]]:
        """Fetches policy details."""
        return db.query_one("SELECT * FROM policies WHERE policy_id = ?", (policy_id.strip(),))

    @staticmethod
    def create_policy(data: PolicyCreate) -> Dict[str, Any]:
        """Creates a new policy record."""
        sql = """
            INSERT INTO policies (policy_id, claimant_id, start_date, end_date, policy_type, premium, date_order_invalid)
            VALUES (?, ?, ?, ?, ?, ?, FALSE)
        """
        db.execute(sql, (
            data.policy_id,
            data.claimant_id,
            data.start_date,
            data.end_date,
            data.policy_type,
            data.premium,
        ))
        return PolicyService.get_policy_by_id(data.policy_id) or data.model_dump()

    @staticmethod
    def verify_policy(policy_id: str, incident_date_str: str, claim_amount: float) -> PolicyVerifyResponse:
        """
        Automated verification:
        1. Policy exists in registry.
        2. Policy is active and not expired on incident date.
        3. Incident date falls within coverage window [start_date, end_date].
        4. Claim amount does not exceed available coverage limit.
        5. Historical claim frequency count on this policy.
        """
        pol = PolicyService.get_policy_by_id(policy_id)
        if not pol:
            return PolicyVerifyResponse(
                policy_id=policy_id,
                is_valid=False,
                is_active=False,
                date_covered=False,
                coverage_available=False,
                coverage_amount=0.0,
                previous_claims_count=0,
                message=f"Policy {policy_id} does not exist in registry."
            )

        # Count previous claims
        claims_rows = db.query_all("SELECT COUNT(*) as cnt FROM claims WHERE policy_id = ?", (policy_id,))
        prev_count = claims_rows[0]["cnt"] if claims_rows else 0

        coverage_limit = float(pol.get("coverage_amount") or 500000.0)
        start_str = str(pol.get("start_date") or "")
        end_str = str(pol.get("end_date") or "")

        date_covered = True
        try:
            inc_dt = datetime.strptime(incident_date_str[:10], "%Y-%m-%d")
            if start_str and end_str:
                st_dt = datetime.strptime(start_str[:10], "%Y-%m-%d")
                en_dt = datetime.strptime(end_str[:10], "%Y-%m-%d")
                date_covered = (st_dt <= inc_dt <= en_dt)
        except Exception as e:
            logger.debug("Date parsing error in policy check: %s", e)
            date_covered = True

        coverage_available = (claim_amount <= coverage_limit)
        is_active = (pol.get("status", "Active") == "Active" and not pol.get("date_order_invalid", False))
        is_valid = (is_active and date_covered and coverage_available)

        msg_parts = []
        if not is_active:
            msg_parts.append("Policy is currently inactive or has invalid date bounds.")
        if not date_covered:
            msg_parts.append(f"Incident date {incident_date_str} falls outside coverage period ({start_str} to {end_str}).")
        if not coverage_available:
            msg_parts.append(f"Claim amount INR {claim_amount:,.2f} exceeds policy coverage limit INR {coverage_limit:,.2f}.")
        if is_valid:
            msg_parts.append(f"Policy verified active. Coverage valid for INR {claim_amount:,.2f}. Previous claims: {prev_count}.")

        return PolicyVerifyResponse(
            policy_id=policy_id,
            is_valid=is_valid,
            is_active=is_active,
            date_covered=date_covered,
            coverage_available=coverage_available,
            coverage_amount=coverage_limit,
            previous_claims_count=prev_count,
            message=" | ".join(msg_parts)
        )
