"""
api/schemas/response_schema.py
------------------------------
Standard response envelopes, health metrics, and dashboard summary schemas.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    database_connected: bool
    models_ready: Dict[str, bool]
    total_claims: int
    version: str


class PaginationMetadata(BaseModel):
    total: int
    limit: int
    offset: int
    returned: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMetadata


class DashboardSummaryResponse(BaseModel):
    total_claims: int
    total_claim_amount: float
    fraud_claims_count: int
    fraud_rate_pct: float
    active_cases_count: int
    cases_by_status: Dict[str, int]
    cases_by_priority: Dict[str, int]
    average_risk_score: float
    high_risk_claims_count: int
