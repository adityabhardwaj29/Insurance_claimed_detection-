"""
api/main.py
-----------
Production-grade FastAPI application for Graph-Enhanced Insurance Claim Fraud Detection.
Includes CORS configuration, logging middleware, structured error handling,
and full OpenAPI documentation.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.utils.config import settings
from api.routes.claims import router as claims_router
from api.routes.cases import router as cases_router
from api.routes.analytics import router as analytics_router
from api.routes.predictions import router as predictions_router
from api.routes.auth import router as auth_router
from api.routes.customers import router as customers_router
from api.routes.policies import router as policies_router
from api.routes.providers import router as providers_router
from api.routes.documents import router as documents_router
from api.routes.reports import router as reports_router
from api.routes.audit_logs import router as audit_logs_router
from api.routes.health import router as health_router
from api.schemas.response_schema import HealthResponse


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing and logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


# Global Exception Handlers
@app.exception_handler(sqlite3.IntegrityError)
async def integrity_error_handler(request: Request, exc: sqlite3.IntegrityError):
    logger.error("Database integrity error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Database integrity error: {str(exc)}"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Let FastAPI HTTPExceptions bubble through to their own handlers
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"},
    )


# Register domain routers (supporting both /api/* and legacy routes)
app.include_router(claims_router)
app.include_router(claims_router, prefix="/api")
app.include_router(cases_router)
app.include_router(cases_router, prefix="/api")
app.include_router(analytics_router)
app.include_router(analytics_router, prefix="/api")
app.include_router(predictions_router)
app.include_router(predictions_router, prefix="/api")

app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(policies_router)
app.include_router(providers_router)
app.include_router(documents_router)
app.include_router(reports_router)
app.include_router(audit_logs_router)
app.include_router(health_router)



@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """
    Verifies service health, database connectivity, and model artifact readiness.
    """
    db_ok = False
    total_claims = 0

    if settings.DATABASE_PATH.exists():
        try:
            with sqlite3.connect(settings.DATABASE_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM claims")
                total_claims = cur.fetchone()[0]
                db_ok = True
        except Exception as e:
            logger.warning("Database health probe failed: %s", e)

    models_ready = {
        "fraud_xgboost": settings.FRAUD_MODEL_PATH.exists(),
        "anomaly_isolation_forest": settings.ANOMALY_MODEL_PATH.exists(),
        "risk_scores_table": settings.RISK_SCORES_PATH.exists(),
        "graph_features": settings.ROOT.joinpath("data/features/graph_features.csv").exists(),
    }

    return {
        "status": "ok" if db_ok else "degraded",
        "database_connected": db_ok,
        "models_ready": models_ready,
        "total_claims": total_claims,
        "version": settings.API_VERSION,
    }
