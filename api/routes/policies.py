"""
api/routes/policies.py
----------------------
Endpoints for policy management and real-time coverage verification.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.schemas.auth_schema import UserProfileResponse
from api.schemas.policy_schema import PolicyCreate, PolicyVerifyRequest, PolicyVerifyResponse
from api.services.auth_service import get_current_user, require_role
from api.services.policy_service import PolicyService

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=List[Dict[str, Any]])
def list_policies(
    claimant_id: Optional[str] = Query(None, description="Filter by customer ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Retrieves list of registered policies."""
    return PolicyService.list_policies(claimant_id=claimant_id, limit=limit, offset=offset)


@router.get("/{policy_id}")
def get_policy(
    policy_id: str,
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Retrieves specific policy details."""
    pol = PolicyService.get_policy_by_id(policy_id)
    if not pol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy {policy_id} not found")
    return pol


@router.post("", status_code=status.HTTP_201_CREATED)
def create_policy(
    data: PolicyCreate,
    current_user: UserProfileResponse = Depends(require_role(["CLAIMS_OFFICER", "ADMIN"])),
):
    """Registers a new insurance policy."""
    return PolicyService.create_policy(data)


@router.post("/verify", response_model=PolicyVerifyResponse)
def verify_policy_coverage(
    req: PolicyVerifyRequest,
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """
    Performs automated underwriting verification:
    Validates active policy period, date coverage, amount limits, and prior claim counts.
    """
    return PolicyService.verify_policy(
        policy_id=req.policy_id,
        incident_date_str=req.incident_date,
        claim_amount=req.claim_amount,
    )
