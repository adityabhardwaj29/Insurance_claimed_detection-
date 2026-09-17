"""
api/routes/analytics.py
-----------------------
FastAPI routes for dashboard summary and operational analytics.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.response_schema import DashboardSummaryResponse
from api.services.claim_service import ClaimService

router = APIRouter(tags=["dashboard"])
claim_service = ClaimService()


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary():
    """
    Returns high-level business, claims, fraud rates, and queue operational KPIs.
    All data is derived from actual SQLite tables and Phase 8 risk scoring outputs.
    """
    return claim_service.get_dashboard_summary()


@router.get("/analytics/summary", response_model=DashboardSummaryResponse)
def get_analytics_summary_alias():
    """Alias for /dashboard/summary."""
    return claim_service.get_dashboard_summary()
