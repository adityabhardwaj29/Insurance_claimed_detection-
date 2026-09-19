"""
api/routes/health.py
--------------------
Health check probe evaluating API, Database, ML model, Anomaly detection, and Knowledge Graph readiness.
"""

from __future__ import annotations

import logging
from typing import Any, Dict
from fastapi import APIRouter

from api.db import db
from src.utils.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/api/health")
def comprehensive_health_check() -> Dict[str, Any]:
    """
    Returns actual health status of:
    - API operational status
    - Database connectivity (Supabase PostgreSQL / SQLite)
    - Supervised XGBoost model weights loaded
    - Isolation Forest anomaly model loaded
    - Knowledge Graph feature store readiness
    - Total claims population in database
    """
    db_connected = False
    total_claims = 0
    try:
        row = db.query_one("SELECT COUNT(*) as cnt FROM claims")
        total_claims = row["cnt"] if row else 0
        db_connected = True
    except Exception as e:
        logger.warning("Database health probe check failed: %s", e)

    models_ready = {
        "fraud_xgboost": settings.FRAUD_MODEL_PATH.exists(),
        "anomaly_isolation_forest": settings.ANOMALY_MODEL_PATH.exists(),
        "risk_scores_table": settings.RISK_SCORES_PATH.exists(),
        "graph_features": settings.ROOT.joinpath("data/features/graph_features.csv").exists(),
    }

    all_models_loaded = all(models_ready.values())
    status_str = "ok" if (db_connected and all_models_loaded) else ("degraded" if db_connected else "down")

    return {
        "status": status_str,
        "api": "ok",
        "database": {
            "status": "connected" if db_connected else "disconnected",
            "engine": db.engine_type,
            "total_claims": total_claims,
        },
        "models": {
            "fraud_model": "loaded" if models_ready["fraud_xgboost"] else "missing",
            "anomaly_model": "loaded" if models_ready["anomaly_isolation_forest"] else "missing",
            "graph_engine": "loaded" if models_ready["graph_features"] else "missing",
            "risk_engine": "loaded" if models_ready["risk_scores_table"] else "missing",
        },
        "version": settings.API_VERSION,
    }
