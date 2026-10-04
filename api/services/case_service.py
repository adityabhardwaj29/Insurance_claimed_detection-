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
        try:
            from api.db import db
            if db and db.is_postgres:
                row = db.query_one(
                    """
                    SELECT c.*, cl.claim_amount as total_claim_amount, cl.claim_type, clt.name as claimant_name
                    FROM investigation_cases c
                    LEFT JOIN claims cl ON c.claim_id = cl.claim_id
                    LEFT JOIN claimants clt ON cl.claimant_id = clt.claimant_id
                    WHERE c.case_id = %s
                    """,
                    (case_id,),
                )
                if row:
                    return {
                        "case_id": row["case_id"],
                        "claim_id": row["claim_id"],
                        "risk_score": float(row["risk_score"] or 0.0),
                        "risk_band": str(row["risk_band"] or "LOW"),
                        "priority": str(row["priority"] or "MEDIUM"),
                        "status": str(row["status"] or "NEW"),
                        "assigned_to": row["assigned_to"],
                        "reason": row["reason"],
                        "notes": row["notes"],
                        "resolution": row["resolution"],
                        "created_at": str(row["created_at"])[:19] if row.get("created_at") else None,
                        "updated_at": str(row["updated_at"])[:19] if row.get("updated_at") else None,
                    }
        except Exception:
            pass
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
        try:
            from api.db import db
            if db and db.is_postgres:
                query = """
                    SELECT c.case_id, c.claim_id, c.risk_score, c.risk_band, c.priority,
                           c.status, c.assigned_to, c.reason, c.notes, c.resolution,
                           c.created_at, c.updated_at,
                           cl.claim_amount as total_claim_amount,
                           cl.claim_type,
                           clt.name as claimant_name
                    FROM investigation_cases c
                    LEFT JOIN claims cl ON c.claim_id = cl.claim_id
                    LEFT JOIN claimants clt ON cl.claimant_id = clt.claimant_id
                    WHERE 1=1
                """
                params = []
                if status:
                    query += " AND UPPER(c.status) = UPPER(%s)"
                    params.append(status)
                if priority:
                    query += " AND UPPER(c.priority) = UPPER(%s)"
                    params.append(priority)
                if assigned_to:
                    query += " AND c.assigned_to = %s"
                    params.append(assigned_to)
                if min_risk is not None:
                    query += " AND c.risk_score >= %s"
                    params.append(float(min_risk))

                query += " ORDER BY c.updated_at DESC LIMIT %s OFFSET %s"
                params.extend([int(limit), int(offset)])

                rows = db.query_all(query, tuple(params))
                if rows:
                    results = []
                    for r in rows:
                        results.append({
                            "case_id": r["case_id"],
                            "claim_id": r["claim_id"],
                            "risk_score": float(r["risk_score"] or 0.0),
                            "risk_band": str(r["risk_band"] or "LOW"),
                            "priority": str(r["priority"] or "MEDIUM"),
                            "status": str(r["status"] or "NEW"),
                            "assigned_to": r["assigned_to"],
                            "reason": r["reason"],
                            "notes": r["notes"],
                            "resolution": r["resolution"],
                            "created_at": str(r["created_at"])[:19] if r.get("created_at") else "",
                            "updated_at": str(r["updated_at"])[:19] if r.get("updated_at") else "",
                        })
                    return results
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Error querying PostgreSQL cases: %s", e)

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
        try:
            from api.db import db
            if db and db.is_postgres:
                tot_r = db.query_one("SELECT COUNT(*) as cnt FROM investigation_cases")
                total = tot_r["cnt"] if tot_r else 0
                s_rows = db.query_all("SELECT status, COUNT(*) as cnt FROM investigation_cases GROUP BY status")
                p_rows = db.query_all("SELECT priority, COUNT(*) as cnt FROM investigation_cases GROUP BY priority")
                return {
                    "total_cases": total,
                    "by_status": {r["status"]: r["cnt"] for r in s_rows},
                    "by_priority": {r["priority"]: r["cnt"] for r in p_rows},
                }
        except Exception:
            pass
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
