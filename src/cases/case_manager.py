"""
src/cases/case_manager.py
-------------------------
Core investigation case management engine for Phase 9.

Implements full lifecycle management:
  - Queue creation from risk threshold triggers
  - Human investigator assignment
  - Audited status transitions
  - Running case notes
  - Case history and audit trail
  - Human-review resolution without automated label manipulation
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.cases.models import (
    CaseEvent,
    CaseEventType,
    CaseNote,
    CasePriority,
    CaseStatus,
    InvestigationCase,
    is_valid_transition,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = ROOT / "database" / "fraud_detection.db"
DEFAULT_RISK_SCORES = ROOT / "data" / "features" / "final_risk_scores.csv"

SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id     TEXT NOT NULL PRIMARY KEY,
    claim_id    TEXT NOT NULL REFERENCES claims(claim_id),
    risk_score  REAL CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_band   TEXT CHECK (risk_band IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    priority    TEXT CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status      TEXT NOT NULL CHECK (status IN ('NEW','UNDER_REVIEW','ESCALATED','RESOLVED','FALSE_POSITIVE')),
    assigned_to TEXT,
    reason      TEXT,
    notes       TEXT,
    resolution  TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_notes (
    note_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     TEXT NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    author      TEXT NOT NULL,
    note_text   TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_events (
    event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     TEXT NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
    event_type  TEXT NOT NULL,
    actor       TEXT NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    details     TEXT,
    timestamp   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cases_claim_id      ON investigation_cases(claim_id);
CREATE INDEX IF NOT EXISTS idx_cases_status        ON investigation_cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_priority      ON investigation_cases(priority);
CREATE INDEX IF NOT EXISTS idx_cases_assigned_to   ON investigation_cases(assigned_to);
CREATE INDEX IF NOT EXISTS idx_case_notes_case     ON case_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_case_events_case    ON case_events(case_id);
"""


def _utc_now() -> str:
    """Returns current UTC timestamp formatted as ISO8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CaseManager:
    """
    Manages the lifecycle of fraud investigation cases.
    Backed by SQLite database.
    """

    def __init__(self, db_path: Optional[str | Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection with foreign keys enabled and row factory."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Ensures the required tables and indexes exist."""
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_DDL)

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
    ) -> InvestigationCase:
        """
        Creates a new investigation case for a claim.

        If risk_score/risk_band are not provided, attempts lookup from
        final_risk_scores.csv.
        """
        cid = claim_id.strip()
        actual_case_id = case_id.strip() if case_id else f"CASE-{cid}"

        # If risk metrics omitted, lookup from risk scoring table if available
        if (risk_score is None or risk_band is None) and DEFAULT_RISK_SCORES.exists():
            try:
                df = pd.read_csv(DEFAULT_RISK_SCORES, keep_default_na=False)
                match = df[df["claim_id"] == cid]
                if not match.empty:
                    row = match.iloc[0]
                    if risk_score is None:
                        risk_score = float(row.get("final_risk_score", 0.0))
                    if risk_band is None:
                        risk_band = str(row.get("risk_band", "LOW"))
                    if reason is None:
                        reason = str(row.get("risk_reasons", ""))
            except Exception as e:
                logger.warning("Could not lookup risk scores for %s: %s", cid, e)

        final_risk_score = float(risk_score) if risk_score is not None else 0.0
        final_risk_band = str(risk_band).upper() if risk_band else "LOW"
        final_priority = str(priority).upper() if priority else final_risk_band

        # Validate priority and risk_band
        if final_priority not in CasePriority.__members__:
            final_priority = "MEDIUM"
        if final_risk_band not in CasePriority.__members__:
            final_risk_band = "LOW"

        now = _utc_now()
        initial_status = CaseStatus.NEW.value

        with self._get_connection() as conn:
            # Check if case already exists
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM investigation_cases WHERE case_id = ?", (actual_case_id,))
            if cur.fetchone():
                raise ValueError(f"Case with ID '{actual_case_id}' already exists")

            cur.execute(
                """
                INSERT INTO investigation_cases (
                    case_id, claim_id, risk_score, risk_band, priority,
                    status, assigned_to, reason, notes, resolution,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actual_case_id,
                    cid,
                    final_risk_score,
                    final_risk_band,
                    final_priority,
                    initial_status,
                    assigned_to,
                    reason,
                    notes,
                    None,
                    now,
                    now,
                ),
            )

            # Record creation event
            cur.execute(
                """
                INSERT INTO case_events (
                    case_id, event_type, actor, old_value, new_value, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actual_case_id,
                    CaseEventType.CASE_CREATED.value,
                    actor,
                    None,
                    initial_status,
                    f"Case created for claim {cid} with priority {final_priority}",
                    now,
                ),
            )

            if notes:
                cur.execute(
                    """
                    INSERT INTO case_notes (case_id, author, note_text, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (actual_case_id, actor, notes, now),
                )

        logger.info("Created investigation case %s for claim %s", actual_case_id, cid)
        return InvestigationCase(
            case_id=actual_case_id,
            claim_id=cid,
            risk_score=final_risk_score,
            risk_band=final_risk_band,
            priority=final_priority,
            status=initial_status,
            assigned_to=assigned_to,
            reason=reason,
            notes=notes,
            resolution=None,
            created_at=now,
            updated_at=now,
        )

    def create_cases_from_risk_scores(
        self,
        risk_scores_path: Optional[str | Path] = None,
        min_risk_score: float = 0.50,
        risk_bands: Optional[List[str]] = None,
        actor: str = "SYSTEM",
    ) -> List[InvestigationCase]:
        """
        Scans risk scores and populates the investigation queue for all
        claims crossing the risk threshold that do not already have a case.
        """
        path = Path(risk_scores_path) if risk_scores_path else DEFAULT_RISK_SCORES
        if not path.exists():
            raise FileNotFoundError(f"Risk scores file not found: {path}")

        df = pd.read_csv(path, keep_default_na=False)
        allowed_bands = set(risk_bands) if risk_bands else {"HIGH", "CRITICAL"}

        # Filter claims crossing criteria
        candidates = df[
            (df["final_risk_score"] >= min_risk_score)
            | (df["risk_band"].isin(allowed_bands))
        ]

        created: List[InvestigationCase] = []
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT claim_id FROM claims")
            valid_claims = {row["claim_id"] for row in cur.fetchall()}
            cur.execute("SELECT claim_id FROM investigation_cases")
            existing_claims = {row["claim_id"] for row in cur.fetchall()}

        for _, row in candidates.iterrows():
            cid = str(row["claim_id"])
            if cid not in valid_claims or cid in existing_claims:
                continue

            case = self.create_case(
                claim_id=cid,
                risk_score=float(row["final_risk_score"]),
                risk_band=str(row["risk_band"]),
                priority=str(row["risk_band"]),
                reason=str(row.get("risk_reasons", "")),
                actor=actor,
            )
            created.append(case)

        logger.info("Auto-queued %d new cases from risk scores", len(created))
        return created

    def get_case(self, case_id: str) -> Optional[InvestigationCase]:
        """Retrieves an investigation case by case_id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM investigation_cases WHERE case_id = ?", (case_id,))
            row = cur.fetchone()
            if not row:
                return None
            return InvestigationCase(
                case_id=row["case_id"],
                claim_id=row["claim_id"],
                risk_score=float(row["risk_score"]),
                risk_band=row["risk_band"],
                priority=row["priority"],
                status=row["status"],
                assigned_to=row["assigned_to"],
                reason=row["reason"],
                notes=row["notes"],
                resolution=row["resolution"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def get_case_by_claim_id(self, claim_id: str) -> Optional[InvestigationCase]:
        """Retrieves an investigation case by claim_id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM investigation_cases WHERE claim_id = ?", (claim_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self.get_case(row["case_id"])

    def update_status(
        self,
        case_id: str,
        new_status: str | CaseStatus,
        actor: str,
        reason: Optional[str] = None,
    ) -> InvestigationCase:
        """
        Updates the status of a case adhering to transition policies,
        logging an audit event.
        """
        target_status = (
            new_status.value if isinstance(new_status, CaseStatus) else str(new_status).upper()
        )
        if target_status not in CaseStatus.__members__:
            raise ValueError(
                f"Invalid status '{target_status}'. Must be one of {[s.value for s in CaseStatus]}"
            )

        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case '{case_id}' not found")

        current_status = case.status
        if not is_valid_transition(current_status, target_status):
            raise ValueError(
                f"Invalid transition from {current_status} to {target_status} for case {case_id}"
            )

        now = _utc_now()
        details_text = f"Status transition from {current_status} to {target_status}"
        if reason:
            details_text += f". Reason: {reason}"

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE investigation_cases
                SET status = ?, updated_at = ?
                WHERE case_id = ?
                """,
                (target_status, now, case_id),
            )
            cur.execute(
                """
                INSERT INTO case_events (
                    case_id, event_type, actor, old_value, new_value, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    CaseEventType.STATUS_CHANGED.value,
                    actor,
                    current_status,
                    target_status,
                    details_text,
                    now,
                ),
            )

        logger.info("Case %s status updated: %s -> %s by %s", case_id, current_status, target_status, actor)
        updated = self.get_case(case_id)
        assert updated is not None
        return updated

    def assign_investigator(
        self,
        case_id: str,
        investigator: str,
        actor: str,
    ) -> InvestigationCase:
        """
        Assigns an investigator to a case. If the case is currently NEW,
        it automatically moves to UNDER_REVIEW.
        """
        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case '{case_id}' not found")

        old_assignee = case.assigned_to
        now = _utc_now()
        target_status = case.status

        # If NEW, transition to UNDER_REVIEW upon assignment
        if case.status == CaseStatus.NEW.value:
            target_status = CaseStatus.UNDER_REVIEW.value

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE investigation_cases
                SET assigned_to = ?, status = ?, updated_at = ?
                WHERE case_id = ?
                """,
                (investigator, target_status, now, case_id),
            )
            cur.execute(
                """
                INSERT INTO case_events (
                    case_id, event_type, actor, old_value, new_value, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    CaseEventType.INVESTIGATOR_ASSIGNED.value,
                    actor,
                    old_assignee,
                    investigator,
                    f"Assigned to {investigator} (status: {target_status})",
                    now,
                ),
            )
            if target_status != case.status:
                cur.execute(
                    """
                    INSERT INTO case_events (
                        case_id, event_type, actor, old_value, new_value, details, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case_id,
                        CaseEventType.STATUS_CHANGED.value,
                        actor,
                        case.status,
                        target_status,
                        "Auto-transition to UNDER_REVIEW upon investigator assignment",
                        now,
                    ),
                )

        logger.info("Case %s assigned to %s by %s", case_id, investigator, actor)
        updated = self.get_case(case_id)
        assert updated is not None
        return updated

    def add_note(
        self,
        case_id: str,
        author: str,
        note_text: str,
    ) -> CaseNote:
        """Appends a timestamped note and creates an audit event."""
        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case '{case_id}' not found")

        text = note_text.strip()
        if not text:
            raise ValueError("Note text cannot be empty")

        now = _utc_now()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO case_notes (case_id, author, note_text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (case_id, author, text, now),
            )
            note_id = cur.lastrowid

            # Update latest notes summary on the case record
            cur.execute(
                """
                UPDATE investigation_cases
                SET notes = ?, updated_at = ?
                WHERE case_id = ?
                """,
                (text, now, case_id),
            )

            # Audit event
            cur.execute(
                """
                INSERT INTO case_events (
                    case_id, event_type, actor, old_value, new_value, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    CaseEventType.NOTE_ADDED.value,
                    author,
                    None,
                    f"Note #{note_id}",
                    text[:120] + ("..." if len(text) > 120 else ""),
                    now,
                ),
            )

        logger.info("Added note #%s to case %s by %s", note_id, case_id, author)
        return CaseNote(
            note_id=note_id,
            case_id=case_id,
            author=author,
            note_text=text,
            created_at=now,
        )

    def resolve_case(
        self,
        case_id: str,
        resolution_status: str | CaseStatus,
        resolution_notes: str,
        actor: str,
    ) -> InvestigationCase:
        """
        Resolves a case with investigator conclusion and documented justification.

        CRITICAL POLICY: Does NOT alter synthetic dataset labels. All investigator
        findings are preserved in the case management audit record.
        """
        target = (
            resolution_status.value
            if isinstance(resolution_status, CaseStatus)
            else str(resolution_status).upper()
        )
        if target not in (CaseStatus.RESOLVED.value, CaseStatus.FALSE_POSITIVE.value):
            raise ValueError(
                f"Resolution status must be RESOLVED or FALSE_POSITIVE, got '{target}'"
            )

        res_text = resolution_notes.strip()
        if not res_text:
            raise ValueError("Resolution notes/findings must be documented")

        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case '{case_id}' not found")

        current_status = case.status
        now = _utc_now()

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE investigation_cases
                SET status = ?, resolution = ?, updated_at = ?
                WHERE case_id = ?
                """,
                (target, res_text, now, case_id),
            )
            cur.execute(
                """
                INSERT INTO case_events (
                    case_id, event_type, actor, old_value, new_value, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    CaseEventType.CASE_RESOLVED.value,
                    actor,
                    current_status,
                    target,
                    f"Resolved with outcome: {target}. Findings: {res_text}",
                    now,
                ),
            )

        logger.info("Case %s resolved as %s by %s", case_id, target, actor)
        resolved = self.get_case(case_id)
        assert resolved is not None
        return resolved

    def get_case_history(self, case_id: str) -> Dict[str, Any]:
        """
        Returns chronological timeline of all events and notes for a case.
        """
        case = self.get_case(case_id)
        if not case:
            raise KeyError(f"Case '{case_id}' not found")

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM case_events
                WHERE case_id = ?
                ORDER BY timestamp ASC, event_id ASC
                """,
                (case_id,),
            )
            events = [
                CaseEvent(
                    event_id=r["event_id"],
                    case_id=r["case_id"],
                    event_type=r["event_type"],
                    actor=r["actor"],
                    old_value=r["old_value"],
                    new_value=r["new_value"],
                    details=r["details"],
                    timestamp=r["timestamp"],
                ).to_dict()
                for r in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT * FROM case_notes
                WHERE case_id = ?
                ORDER BY created_at ASC, note_id ASC
                """,
                (case_id,),
            )
            notes = [
                CaseNote(
                    note_id=r["note_id"],
                    case_id=r["case_id"],
                    author=r["author"],
                    note_text=r["note_text"],
                    created_at=r["created_at"],
                ).to_dict()
                for r in cur.fetchall()
            ]

        return {
            "case": case.to_dict(),
            "events": events,
            "notes": notes,
        }

    def list_cases(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        min_risk: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InvestigationCase]:
        """Queries and filters the investigation cases queue."""
        query = "SELECT * FROM investigation_cases WHERE 1=1"
        params: List[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if priority:
            query += " AND priority = ?"
            params.append(priority.upper())
        if assigned_to:
            query += " AND assigned_to = ?"
            params.append(assigned_to)
        if min_risk is not None:
            query += " AND risk_score >= ?"
            params.append(float(min_risk))

        query += " ORDER BY risk_score DESC, created_at ASC LIMIT ? OFFSET ?"
        params.extend([int(limit), int(offset)])

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            cases = [
                InvestigationCase(
                    case_id=r["case_id"],
                    claim_id=r["claim_id"],
                    risk_score=float(r["risk_score"]),
                    risk_band=r["risk_band"],
                    priority=r["priority"],
                    status=r["status"],
                    assigned_to=r["assigned_to"],
                    reason=r["reason"],
                    notes=r["notes"],
                    resolution=r["resolution"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                for r in cur.fetchall()
            ]
        return cases

    def get_case_statistics(self) -> Dict[str, Any]:
        """Provides aggregate operational metrics of the case queue."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM investigation_cases")
            total = cur.fetchone()[0]

            cur.execute("SELECT status, COUNT(*) FROM investigation_cases GROUP BY status")
            by_status = dict(cur.fetchall())

            cur.execute("SELECT priority, COUNT(*) FROM investigation_cases GROUP BY priority")
            by_priority = dict(cur.fetchall())

            cur.execute("SELECT COUNT(*) FROM investigation_cases WHERE assigned_to IS NOT NULL")
            assigned = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM case_notes")
            total_notes = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM case_events")
            total_events = cur.fetchone()[0]

        return {
            "total_cases": total,
            "status_distribution": by_status,
            "priority_distribution": by_priority,
            "assigned_cases": assigned,
            "unassigned_cases": total - assigned,
            "total_notes": total_notes,
            "total_events": total_events,
        }
