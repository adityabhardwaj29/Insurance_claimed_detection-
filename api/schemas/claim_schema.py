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
    claimant_name: Optional[str] = None
    claimant_phone: Optional[str] = None
    claimant_email: Optional[str] = None
    policy_type: Optional[str] = None
    final_risk_score: Optional[float] = None
    risk_band: Optional[str] = None


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
    fraud_probability: Optional[float] = None
    top_factors: Optional[List[Dict[str, Any]]] = None
    top_positive_factors: Optional[List[Dict[str, Any]]] = None
    top_negative_factors: Optional[List[Dict[str, Any]]] = None
    graph_explanation: Optional[Dict[str, Any]] = None


class ClaimCreateRequest(BaseModel):
    claimant_id: Optional[str] = None
    claimant_name: Optional[str] = None
    claimant_phone: Optional[str] = None
    claimant_email: Optional[str] = None
    policy_id: Optional[str] = None
    policy_number: Optional[str] = None
    vehicle_id: Optional[str] = None
    provider_id: Optional[str] = None
    provider_name: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    auto_year: Optional[int] = None
    auto_vin: Optional[str] = None
    invoice_id: Optional[str] = None
    claim_date: Optional[str] = None
    incident_date: Optional[str] = None
    claim_amount: Optional[float] = None
    total_claim_amount: Optional[float] = None
    injury_claim: Optional[float] = 0.0
    property_claim: Optional[float] = 0.0
    vehicle_claim: Optional[float] = 0.0
    claim_type: Optional[str] = "Accident"
    description: Optional[str] = None
    incident_time: Optional[str] = None
    incident_location: Optional[str] = None
    incident_type: Optional[str] = None
    collision_type: Optional[str] = None
    incident_severity: Optional[str] = None
    incident_state: Optional[str] = None
    incident_city: Optional[str] = None
    incident_hour_of_the_day: Optional[int] = None
    number_of_vehicles_involved: Optional[int] = None
    witnesses: Optional[int] = None
    bodily_injuries: Optional[int] = None
    police_report_available: Optional[str] = None
    police_report: Optional[bool] = False
    severity: Optional[str] = "Medium"
    invoice_amount: Optional[float] = None
    service_type: Optional[str] = "Inspection & Repair"
    status: Optional[str] = "Submitted"


class ClaimDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(Approve|Reject|Request Manual Review|Escalate Investigation)$")
    reason: str = Field(..., min_length=2)

