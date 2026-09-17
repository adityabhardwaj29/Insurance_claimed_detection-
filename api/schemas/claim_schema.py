"""
api/schemas/claim_schema.py
---------------------------
Pydantic schemas for Claim queries, risk breakdowns, graph subnetworks,
duplicates, and explanations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClaimListItem(BaseModel):
    claim_id: str
    claimant_id: str
    policy_id: str
    provider_id: str
    vehicle_id: str
    invoice_id: str
    claim_date: Optional[str] = None
    claim_amount: float
    claim_type: str
    status: str
    fraud_label: int


class ClaimDetailResponse(BaseModel):
    claim_id: str
    claim_date: Optional[str] = None
    claim_amount: float
    claim_type: str
    status: str
    fraud_label: int
    description: Optional[str] = None
    claimant: Dict[str, Any]
    provider: Dict[str, Any]
    policy: Dict[str, Any]
    vehicle: Dict[str, Any]
    invoice: Dict[str, Any]


class ClaimRiskResponse(BaseModel):
    claim_id: str
    final_risk_score: float
    risk_band: str
    fraud_probability: float
    anomaly_score: float
    duplicate_score: float
    graph_risk_score: float
    risk_reasons: List[str]


class ClaimGraphResponse(BaseModel):
    claim_id: str
    claimant_id: str
    provider_id: str
    claimant_degree: int
    provider_claim_count: int
    fraud_neighbor_ratio: float
    suspicious_neighbor_count: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class ClaimDuplicatesResponse(BaseModel):
    claim_id: str
    duplicate_similarity_score: float
    dup_type: str
    matched_claim_id: Optional[str] = None
    is_duplicate_flag: int
    matching_attributes: List[str]


class ClaimExplanationResponse(BaseModel):
    claim_id: str
    final_risk_score: float
    risk_band: str
    signals: Dict[str, float]
    weights: Dict[str, float]
    reasons: List[str]
    summary: str
