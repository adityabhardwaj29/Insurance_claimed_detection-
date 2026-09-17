"""
src/cases/models.py
-------------------
Data models, enums, and transition rules for Fraud Investigation Case Management.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class CaseStatus(str, Enum):
    """
    Lifecycle statuses for an investigation case.
    Human-in-the-loop: a claim is NEVER automatically marked confirmed fraud.
    """
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class CasePriority(str, Enum):
    """Operational priority for triage queue sorting."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CaseEventType(str, Enum):
    """Immutable audit event types."""
    CASE_CREATED = "CASE_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    INVESTIGATOR_ASSIGNED = "INVESTIGATOR_ASSIGNED"
    NOTE_ADDED = "NOTE_ADDED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    CASE_RESOLVED = "CASE_RESOLVED"


# Permitted status transitions in human investigation workflow
VALID_TRANSITIONS: Dict[CaseStatus, List[CaseStatus]] = {
    CaseStatus.NEW: [
        CaseStatus.UNDER_REVIEW,
        CaseStatus.FALSE_POSITIVE,
    ],
    CaseStatus.UNDER_REVIEW: [
        CaseStatus.ESCALATED,
        CaseStatus.RESOLVED,
        CaseStatus.FALSE_POSITIVE,
        CaseStatus.NEW,  # return to queue if unassigned
    ],
    CaseStatus.ESCALATED: [
        CaseStatus.RESOLVED,
        CaseStatus.FALSE_POSITIVE,
        CaseStatus.UNDER_REVIEW,  # return for additional inquiry
    ],
    CaseStatus.RESOLVED: [
        CaseStatus.UNDER_REVIEW,  # reopen if new evidence arrives
    ],
    CaseStatus.FALSE_POSITIVE: [
        CaseStatus.UNDER_REVIEW,  # reopen if new evidence arrives
    ],
}


def is_valid_transition(current: str | CaseStatus, target: str | CaseStatus) -> bool:
    """Checks if a case status transition is allowed by workflow policy."""
    try:
        cur_enum = CaseStatus(current)
        tgt_enum = CaseStatus(target)
    except ValueError:
        return False

    if cur_enum == tgt_enum:
        return True
    return tgt_enum in VALID_TRANSITIONS.get(cur_enum, [])


@dataclass
class CaseNote:
    """Individual timestamped note created by an investigator."""
    note_id: Optional[int]
    case_id: str
    author: str
    note_text: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CaseEvent:
    """Immutable audit trail entry for a state mutation."""
    event_id: Optional[int]
    case_id: str
    event_type: str
    actor: str
    old_value: Optional[str]
    new_value: Optional[str]
    details: Optional[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InvestigationCase:
    """
    Representation of an investigation case record.
    """
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
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
