"""
api/services/case_service.py
----------------------------
Service layer providing fraud investigation case management capabilities.
Integrates domain logic in src.cases.case_manager with FastAPI routes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from src.cases.case_manager import CaseManager
from src.cases.investigation import build_investigation_dossier
from src.cases.models import CaseStatus, CasePriority


class CaseService:
    """
    Facade service for case management operations.
    """

    def __init__(self, db_path: Optional[str | Path] = None):
        self.manager = CaseManager(db_path=db_path)

    def create_case(
        self,
        claim_id: str,
        risk_score: Optional[float] = None,
        risk_band: Optional[str] = None,
        priority: Optional[str] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        assigned_to: Optional[str] = None,
        case_id: Optional[str] = None,
        actor: str = "SYSTEM",
    ) -> Dict[str, Any]:
        """Creates an investigation case."""
        case = self.manager.create_case(
            claim_id=claim_id,
            risk_score=risk_score,
            risk_band=risk_band,
            priority=priority,
            reason=reason,
            notes=notes,
            assigned_to=assigned_to,
            case_id=case_id,
            actor=actor,
        )
        return case.to_dict()

    def update_status(
        self,
        case_id: str,
        status: str,
        actor: str = "INVESTIGATOR",
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates case status with audit trail."""
        case = self.manager.update_status(
            case_id=case_id,
            new_status=status,
            actor=actor,
            reason=reason,
        )
        return case.to_dict()

    def assign_investigator(
        self,
        case_id: str,
        investigator: str,
        actor: str = "SUPERVISOR",
    ) -> Dict[str, Any]:
        """Assigns investigator to a case."""
        case = self.manager.assign_investigator(
            case_id=case_id,
            investigator=investigator,
            actor=actor,
        )
        return case.to_dict()

    def add_note(
        self,
        case_id: str,
        author: str,
        note_text: str,
    ) -> Dict[str, Any]:
        """Adds a timestamped investigator note."""
        note = self.manager.add_note(
            case_id=case_id,
            author=author,
            note_text=note_text,
        )
        return note.to_dict()

    def get_case_history(self, case_id: str) -> Dict[str, Any]:
        """Retrieves chronological events and notes."""
        return self.manager.get_case_history(case_id=case_id)

    def resolve_case(
        self,
        case_id: str,
        resolution_status: str,
        resolution_notes: str,
        actor: str = "INVESTIGATOR",
    ) -> Dict[str, Any]:
        """
        Resolves case without automated fraud marking.
        Human-in-the-loop decision recorded in audit log.
        """
        case = self.manager.resolve_case(
            case_id=case_id,
            resolution_status=resolution_status,
            resolution_notes=resolution_notes,
            actor=actor,
        )
        return case.to_dict()

    def patch_case(
        self,
        case_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
        resolution: Optional[str] = None,
        actor: str = "INVESTIGATOR",
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Partially updates case attributes."""
        case = self.manager.patch_case(
            case_id=case_id,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            notes=notes,
            resolution=resolution,
            actor=actor,
            reason=reason,
        )
        return case.to_dict()


    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single case by ID."""
        case = self.manager.get_case(case_id)
        return case.to_dict() if case else None

    def list_cases(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        min_risk: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Lists cases matching filter criteria."""
        cases = self.manager.list_cases(
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            min_risk=min_risk,
            limit=limit,
            offset=offset,
        )
        return [c.to_dict() for c in cases]

    def get_case_statistics(self) -> Dict[str, Any]:
        """Returns aggregate operational statistics."""
        return self.manager.get_case_statistics()

    def get_dossier(self, case_id: str) -> Dict[str, Any]:
        """Assembles full evidence dossier."""
        return build_investigation_dossier(case_id=case_id, db_path=self.manager.db_path)


# Module-level convenience functions matching user prompt
_default_service: Optional[CaseService] = None


def _get_service() -> CaseService:
    global _default_service
    if _default_service is None:
        _default_service = CaseService()
    return _default_service


def create_case(
    claim_id: str,
    risk_score: Optional[float] = None,
    risk_band: Optional[str] = None,
    priority: Optional[str] = None,
    reason: Optional[str] = None,
    notes: Optional[str] = None,
    assigned_to: Optional[str] = None,
    case_id: Optional[str] = None,
    actor: str = "SYSTEM",
) -> Dict[str, Any]:
    return _get_service().create_case(
        claim_id=claim_id,
        risk_score=risk_score,
        risk_band=risk_band,
        priority=priority,
        reason=reason,
        notes=notes,
        assigned_to=assigned_to,
        case_id=case_id,
        actor=actor,
    )


def update_status(
    case_id: str,
    status: str,
    actor: str = "INVESTIGATOR",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    return _get_service().update_status(
        case_id=case_id, status=status, actor=actor, reason=reason
    )


def assign_investigator(
    case_id: str,
    investigator: str,
    actor: str = "SUPERVISOR",
) -> Dict[str, Any]:
    return _get_service().assign_investigator(
        case_id=case_id, investigator=investigator, actor=actor
    )


def add_notes(
    case_id: str,
    author: str,
    note_text: str,
) -> Dict[str, Any]:
    return _get_service().add_note(
        case_id=case_id, author=author, note_text=note_text
    )


def view_case_history(case_id: str) -> Dict[str, Any]:
    return _get_service().get_case_history(case_id=case_id)


def resolve_case(
    case_id: str,
    resolution_status: str,
    resolution_notes: str,
    actor: str = "INVESTIGATOR",
) -> Dict[str, Any]:
    return _get_service().resolve_case(
        case_id=case_id,
        resolution_status=resolution_status,
        resolution_notes=resolution_notes,
        actor=actor,
    )
