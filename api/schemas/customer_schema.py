"""
api/schemas/customer_schema.py
------------------------------
Pydantic schemas for customer intake, search, and 360-degree risk history profiles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=18, le=100)
    city: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|O)$")
    marital_status: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None


class CustomerResponse(BaseModel):
    claimant_id: str
    name: str
    age: Optional[int] = None
    city: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None


class Customer360Response(BaseModel):
    customer: CustomerResponse
    policies: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    total_claims_count: int
    total_claim_amount: float
    fraud_alert_count: int
    vehicles: List[Dict[str, Any]]
