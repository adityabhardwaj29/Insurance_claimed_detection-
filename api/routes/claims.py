"""
api/routes/claims.py
--------------------
FastAPI router for claim querying, risk breakdown, graph subnetwork,
duplicate detection, and explainability endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from api.schemas.claim_schema import (
    ClaimDetailResponse,
    ClaimDuplicatesResponse,
    ClaimExplanationResponse,
    ClaimGraphResponse,
    ClaimListItem,
    ClaimRiskResponse,
)
from api.schemas.response_schema import PaginatedResponse, PaginationMetadata
from api.services.claim_service import ClaimService
from api.services.graph_service import GraphService

router = APIRouter(prefix="/claims", tags=["claims"])
claim_service = ClaimService()
graph_service = GraphService()


@router.get("", response_model=PaginatedResponse[ClaimListItem])
def list_claims(
    status: Optional[str] = Query(None, description="Filter by claim status (e.g. Open, Approved)"),
    claim_type: Optional[str] = Query(None, description="Filter by claim type (e.g. Accident, Theft)"),
    fraud_label: Optional[int] = Query(None, description="Filter by synthetic ground-truth fraud label (0 or 1)"),
    min_amount: Optional[float] = Query(None, description="Minimum claim amount"),
    max_amount: Optional[float] = Query(None, description="Maximum claim amount"),
    sort_by: str = Query("claim_id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort direction (asc or desc)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Lists insurance claims with dynamic filtering, sorting, and pagination.
    """
    items, total = claim_service.list_claims(
        status=status,
        claim_type=claim_type,
        fraud_label=fraud_label,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "returned": len(items),
        },
    }


@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim(claim_id: str):
    """
    Retrieves full relational details for an individual claim:
    claimant, provider, policy, vehicle, and invoice.
    """
    detail = claim_service.get_claim_detail(claim_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found")
    return detail


@router.get("/{claim_id}/risk", response_model=ClaimRiskResponse)
def get_claim_risk(claim_id: str):
    """
    Retrieves composite fraud risk score, operational risk band,
    and 4 sub-signal components from Phase 8.
    """
    risk = claim_service.get_claim_risk(claim_id)
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk score not found for claim '{claim_id}'")
    return risk


@router.get("/{claim_id}/graph", response_model=ClaimGraphResponse)
def get_claim_graph(claim_id: str):
    """
    Retrieves the ego subnetwork surrounding the claim:
    claimant, provider, policy, vehicle, connected claims, and graph centrality metrics.
    """
    sub = graph_service.get_claim_subnetwork(claim_id)
    if not sub:
        raise HTTPException(status_code=404, detail=f"Graph data not found for claim '{claim_id}'")
    return sub


@router.get("/{claim_id}/duplicates", response_model=ClaimDuplicatesResponse)
def get_claim_duplicates(claim_id: str):
    """
    Retrieves pairwise duplicate similarity score, cluster type,
    and matching attributes from Phase 3 duplicate detector.
    """
    dup = claim_service.get_claim_duplicates(claim_id)
    if not dup:
        raise HTTPException(status_code=404, detail=f"Duplicate analysis not found for claim '{claim_id}'")
    return dup


@router.get("/{claim_id}/explanation", response_model=ClaimExplanationResponse)
def get_claim_explanation(claim_id: str):
    """
    Returns explainable AI decomposition: component weights,
    triggered reason codes, and human-readable narrative summary.
    """
    exp = claim_service.get_claim_explanation(claim_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Explanation not found for claim '{claim_id}'")
    return exp
