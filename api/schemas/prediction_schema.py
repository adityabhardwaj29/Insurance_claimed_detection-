"""
api/schemas/prediction_schema.py
--------------------------------
Pydantic schemas for predictive inference, unsupervised anomaly scoring,
and graph topology analysis endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """
    Inference request for supervised fraud model.
    Can supply an existing claim_id OR feature values directly.
    """
    claim_id: Optional[str] = None
    claim_amount: Optional[float] = Field(None, json_schema_extra={"example": 55000.0})
    claim_type: Optional[str] = Field(None, json_schema_extra={"example": "Accident"})
    policy_type: Optional[str] = Field(None, json_schema_extra={"example": "Comprehensive"})
    vehicle_type: Optional[str] = Field(None, json_schema_extra={"example": "SUV"})
    vehicle_make: Optional[str] = Field(None, json_schema_extra={"example": "Tata"})
    provider_type: Optional[str] = Field(None, json_schema_extra={"example": "Garage"})
    claimant_city: Optional[str] = Field(None, json_schema_extra={"example": "Mumbai"})
    features: Optional[Dict[str, Any]] = None


class PredictResponse(BaseModel):
    claim_id: Optional[str] = None
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    fraud_prediction: int = Field(..., description="0 = legitimate, 1 = predicted fraud")
    risk_tier: str
    model_name: str = "XGBoost"


class AnomalyScoreRequest(BaseModel):
    """
    Inference request for unsupervised anomaly scoring.
    Can supply claim_id OR custom features.
    """
    claim_id: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class AnomalyScoreResponse(BaseModel):
    claim_id: Optional[str] = None
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    model_name: str = "IsolationForest"
    details: Dict[str, Any] = {}


class GraphAnalysisRequest(BaseModel):
    """
    Request for graph risk analysis of a claim or network entity.
    """
    claim_id: Optional[str] = None
    claimant_id: Optional[str] = None
    provider_id: Optional[str] = None


class GraphAnalysisResponse(BaseModel):
    claim_id: Optional[str] = None
    graph_risk_score: float = Field(..., ge=0.0, le=1.0)
    claimant_degree: int
    provider_claim_count: int
    fraud_neighbor_ratio: float
    suspicious_neighbor_count: int
    repeated_claimant_provider: int
    connected_claim_count: int
    network_summary: str
