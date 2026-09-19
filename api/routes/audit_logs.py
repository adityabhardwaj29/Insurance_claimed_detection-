"""
api/routes/audit_logs.py
------------------------
Endpoints for immutable system and case audit trail querying.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query

from api.db import db
from api.schemas.auth_schema import UserProfileResponse
from api.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"])


@router.get("", response_model=List[Dict[str, Any]])
def list_audit_logs(
    actor: Optional[str] = Query(None, description="Filter by user or actor"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: UserProfileResponse = Depends(require_role(["ADMIN", "SUPERVISOR", "ANALYST", "INVESTIGATOR", "CLAIMS_OFFICER"])),
):
    """
    Retrieves chronological immutable audit log events across all cases and system actions.
    """
    # Query case_events
    where_clauses = []
    params = []
    if actor:
        where_clauses.append("actor = ?")
        params.append(actor)
    if event_type:
        where_clauses.append("event_type = ?")
        params.append(event_type)

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    sql = f"SELECT * FROM case_events{where_sql} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    try:
        return db.query_all(sql, params)
    except Exception:
        return []
