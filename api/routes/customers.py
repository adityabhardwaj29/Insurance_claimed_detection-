"""
api/routes/customers.py
-----------------------
Endpoints for customer intake, search, and 360-degree profile views.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.schemas.auth_schema import UserProfileResponse
from api.schemas.customer_schema import Customer360Response, CustomerCreate, CustomerResponse
from api.services.auth_service import get_current_user, require_role
from api.services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=List[CustomerResponse])
def search_customers(
    q: Optional[str] = Query(None, description="Search query across name, ID, phone, city"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Searches customer/claimant directory."""
    return CustomerService.search_customers(query=q, limit=limit, offset=offset)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    current_user: UserProfileResponse = Depends(require_role(["CLAIMS_OFFICER", "ADMIN", "SUPERVISOR"])),
):
    """Registers a new customer profile."""
    return CustomerService.create_customer(data)


@router.get("/{claimant_id}", response_model=Customer360Response)
def get_customer_360(
    claimant_id: str,
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Retrieves complete 360-degree customer dossier with policies, claims, and fraud alert history."""
    profile = CustomerService.get_customer_360(claimant_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {claimant_id} not found")
    return profile
