"""
api/schemas/policy_schema.py
----------------------------
Pydantic schemas for policy creation, retrieval, and automated coverage validation.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class PolicyCreate(BaseModel):
    policy_id: str = Field(..., pattern="^POL[0-9]{4,}$")
    claimant_id: str
    start_date: str
    end_date: str
    policy_type: str = Field("Comprehensive", pattern="^(Comprehensive|Zero Dep|Third Party|Health|Property)$")
    premium: float = Field(..., gt=0)
    coverage_amount: Optional[float] = 500000.0
    deductible: Optional[float] = 2000.0


class PolicyVerifyRequest(BaseModel):
    policy_id: str
    incident_date: str
    claim_amount: float


class PolicyVerifyResponse(BaseModel):
    policy_id: str
    is_valid: bool
    is_active: bool
    date_covered: bool
    coverage_available: bool
    coverage_amount: float
    previous_claims_count: int
    message: str
