"""
api/routes/providers.py
-----------------------
Endpoints for healthcare & service provider directory, claim history, and collusion network lookups.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.db import db
from api.schemas.auth_schema import UserProfileResponse
from api.services.auth_service import get_current_user

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=List[Dict[str, Any]])
def list_providers(
    provider_type: Optional[str] = Query(None, description="Filter by Surveyor, Dealer, Garage, Hospital"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Lists registered service providers."""
    if provider_type:
        sql = "SELECT * FROM providers WHERE provider_type = ? ORDER BY provider_name ASC LIMIT ? OFFSET ?"
        return db.query_all(sql, (provider_type, limit, offset))
    sql = "SELECT * FROM providers ORDER BY provider_name ASC LIMIT ? OFFSET ?"
    return db.query_all(sql, (limit, offset))


@router.get("/{provider_id}")
def get_provider_profile(
    provider_id: str,
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """
    Returns full provider profile including claim history, invoice totals,
    connected claimants, and historical risk flag frequency.
    """
    pid = provider_id.strip()
    prov = db.query_one("SELECT * FROM providers WHERE provider_id = ?", (pid,))
    if not prov:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")

    claims = db.query_all("""
        SELECT c.*, r.final_risk_score, r.risk_band 
        FROM claims c 
        LEFT JOIN risk_scores r ON c.claim_id = r.claim_id
        WHERE c.provider_id = ?
        ORDER BY c.claim_date DESC
    """, (pid,))

    invoices = db.query_all("SELECT * FROM invoices WHERE provider_id = ?", (pid,))

    total_claims = len(claims)
    total_invoiced = sum(float(inv.get("invoice_amount") or 0.0) for inv in invoices)
    flagged_claims = sum(1 for c in claims if c.get("fraud_label") == 1 or c.get("risk_band") in ("HIGH", "CRITICAL"))

    unique_claimants = len(set(c.get("claimant_id") for c in claims if c.get("claimant_id")))

    return {
        "provider": prov,
        "claims": claims,
        "invoices": invoices,
        "total_claims": total_claims,
        "total_invoiced_amount": total_invoiced,
        "flagged_claims_count": flagged_claims,
        "unique_claimants_served": unique_claimants,
    }
