"""
api/schemas/case_schema.py
--------------------------
Pydantic schemas for Investigation Case Management API endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseCreateRequest(BaseModel):
    claim_id: str
    risk_score: Optional[float] = None
    risk_band: Optional[str] = None
    priority: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    case_id: Optional[str] = None
    actor: str = "SYSTEM"


class CaseStatusUpdateRequest(BaseModel):
    status: str
    actor: str = "INVESTIGATOR"
    reason: Optional[str] = None


class CaseAssignRequest(BaseModel):
    investigator: str
    actor: str = "SUPERVISOR"


class CaseNoteCreateRequest(BaseModel):
    author: str
    note_text: str


class CaseResolveRequest(BaseModel):
    resolution_status: str
    resolution_notes: str
    actor: str = "INVESTIGATOR"


class CasePatchRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    resolution: Optional[str] = None
    actor: str = "INVESTIGATOR"
    reason: Optional[str] = None



class CaseResponse(BaseModel):
    case_id: str
    claim_id: str
    risk_score: float
    risk_band: str
    priority: str
    status: str
    assigned_to: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    resolution: Optional[str] = None
    created_at: str
    updated_at: str


class CaseNoteResponse(BaseModel):
    note_id: Optional[int] = None
    case_id: str
    author: str
    note_text: str
    created_at: str


class CaseEventResponse(BaseModel):
    event_id: Optional[int] = None
    case_id: str
    event_type: str
    actor: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None
    timestamp: str


class CaseHistoryResponse(BaseModel):
    case: CaseResponse
    events: List[CaseEventResponse]
    notes: List[CaseNoteResponse]
