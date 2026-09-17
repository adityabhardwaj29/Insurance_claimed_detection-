"""
api/routes/cases.py
-------------------
FastAPI routes for Fraud Investigation Case Management (Phase 9).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from api.schemas.case_schema import (
    CaseAssignRequest,
    CaseCreateRequest,
    CaseHistoryResponse,
    CaseNoteCreateRequest,
    CaseNoteResponse,
    CaseResolveRequest,
    CaseResponse,
    CaseStatusUpdateRequest,
)
from api.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])
service = CaseService()


@router.get("", response_model=List[CaseResponse])
def list_investigation_cases(
    status: Optional[str] = Query(None, description="Filter by case status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by investigator"),
    min_risk: Optional[float] = Query(None, description="Minimum risk score"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List investigation cases with optional filtering."""
    return service.list_cases(
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        min_risk=min_risk,
        limit=limit,
        offset=offset,
    )


@router.get("/stats/summary")
def get_case_statistics():
    """Returns queue breakdown and operational counts."""
    return service.get_case_statistics()


@router.get("/{case_id}", response_model=CaseResponse)
def get_case_by_id(case_id: str):
    """Fetch an individual case by case_id."""
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return case


@router.post("", response_model=CaseResponse, status_code=201)
def create_investigation_case(req: CaseCreateRequest):
    """Create a new case in the investigation queue."""
    try:
        return service.create_case(
            claim_id=req.claim_id,
            risk_score=req.risk_score,
            risk_band=req.risk_band,
            priority=req.priority,
            reason=req.reason,
            notes=req.notes,
            assigned_to=req.assigned_to,
            case_id=req.case_id,
            actor=req.actor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/status", response_model=CaseResponse)
def update_case_status(case_id: str, req: CaseStatusUpdateRequest):
    """Update case status following allowed lifecycle transitions."""
    try:
        return service.update_status(
            case_id=case_id,
            status=req.status,
            actor=req.actor,
            reason=req.reason,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{case_id}/assign", response_model=CaseResponse)
def assign_investigator_to_case(case_id: str, req: CaseAssignRequest):
    """Assign human investigator to a case."""
    try:
        return service.assign_investigator(
            case_id=case_id,
            investigator=req.investigator,
            actor=req.actor,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=201)
def add_case_note(case_id: str, req: CaseNoteCreateRequest):
    """Append a timestamped investigator note."""
    try:
        return service.add_note(
            case_id=case_id,
            author=req.author,
            note_text=req.note_text,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}/history", response_model=CaseHistoryResponse)
def get_case_history(case_id: str):
    """Fetch complete chronological timeline of events and notes."""
    try:
        return service.get_case_history(case_id=case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")


@router.post("/{case_id}/resolve", response_model=CaseResponse)
def resolve_investigation_case(case_id: str, req: CaseResolveRequest):
    """
    Resolve case with investigator conclusion (human-in-the-loop).
    """
    try:
        return service.resolve_case(
            case_id=case_id,
            resolution_status=req.resolution_status,
            resolution_notes=req.resolution_notes,
            actor=req.actor,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{case_id}/dossier")
def get_investigation_dossier(case_id: str):
    """Fetch complete assembled evidence dossier for investigator review."""
    try:
        return service.get_dossier(case_id=case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
