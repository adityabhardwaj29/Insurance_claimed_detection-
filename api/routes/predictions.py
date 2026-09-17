"""
api/routes/predictions.py
-------------------------
FastAPI routes for real-time model inference, anomaly evaluation,
and graph topology analysis.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.prediction_schema import (
    AnomalyScoreRequest,
    AnomalyScoreResponse,
    GraphAnalysisRequest,
    GraphAnalysisResponse,
    PredictRequest,
    PredictResponse,
)
from api.services.graph_service import GraphService
from api.services.prediction_service import PredictionService

router = APIRouter(tags=["predictions"])
prediction_service = PredictionService()
graph_service = GraphService()


@router.post("/predict", response_model=PredictResponse)
def predict_fraud(req: PredictRequest):
    """
    Computes real-time fraud probability using trained supervised XGBoost pipeline.
    Accepts an existing claim_id OR feature values.
    """
    return prediction_service.predict_fraud(
        claim_id=req.claim_id,
        claim_amount=req.claim_amount,
        claim_type=req.claim_type,
        policy_type=req.policy_type,
        vehicle_type=req.vehicle_type,
        vehicle_make=req.vehicle_make,
        provider_type=req.provider_type,
        claimant_city=req.claimant_city,
        features=req.features,
    )


@router.post("/anomaly-score", response_model=AnomalyScoreResponse)
def score_anomaly(req: AnomalyScoreRequest):
    """
    Evaluates unsupervised anomaly risk using calibrated Isolation Forest ensemble.
    """
    return prediction_service.score_anomaly(
        claim_id=req.claim_id,
        features=req.features,
    )


@router.post("/graph-analysis", response_model=GraphAnalysisResponse)
def analyze_graph(req: GraphAnalysisRequest):
    """
    Computes graph topological metrics and risk scores for input entity context.
    """
    return graph_service.analyze_graph(
        claim_id=req.claim_id,
        claimant_id=req.claimant_id,
        provider_id=req.provider_id,
    )
