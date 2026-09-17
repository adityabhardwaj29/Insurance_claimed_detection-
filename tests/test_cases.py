"""
tests/test_cases.py
-------------------
Comprehensive test suite for Phase 9: Fraud Investigation Case Management.
Verifies database integrity, state transitions, investigator assignments,
notes, audit events, human-review resolution, API services, and routes.
"""

from __future__ import annotations

import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from src.cases.models import (
    CaseEvent,
    CaseEventType,
    CaseNote,
    CasePriority,
    CaseStatus,
    InvestigationCase,
    is_valid_transition,
)
from src.cases.case_manager import CaseManager
from src.cases.investigation import build_investigation_dossier, investigation_summary
from api.services.case_service import CaseService
from api.main import app

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def temp_db(tmp_path):
    """Creates a temporary sqlite database with base claims schema."""
    db_file = tmp_path / "test_fraud.db"
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Minimal schema for claims dependencies
    conn.executescript("""
        CREATE TABLE claimants (
            claimant_id TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            city TEXT,
            gender TEXT,
            marital_status TEXT
        );
        CREATE TABLE providers (
            provider_id TEXT NOT NULL PRIMARY KEY,
            provider_name TEXT NOT NULL,
            city TEXT,
            provider_type TEXT,
            rating REAL
        );
        CREATE TABLE policies (
            policy_id TEXT NOT NULL PRIMARY KEY,
            claimant_id TEXT NOT NULL REFERENCES claimants(claimant_id),
            start_date TEXT,
            end_date TEXT,
            policy_type TEXT,
            premium REAL,
            date_order_invalid INTEGER DEFAULT 0
        );
        CREATE TABLE vehicles (
            vehicle_id TEXT NOT NULL PRIMARY KEY,
            claimant_id TEXT NOT NULL REFERENCES claimants(claimant_id),
            make TEXT,
            vehicle_type TEXT,
            registration_no TEXT,
            model_year INTEGER
        );
        CREATE TABLE invoices (
            invoice_id TEXT NOT NULL PRIMARY KEY,
            provider_id TEXT NOT NULL REFERENCES providers(provider_id),
            invoice_amount REAL,
            invoice_date TEXT,
            description TEXT
        );
        CREATE TABLE claims (
            claim_id TEXT NOT NULL PRIMARY KEY,
            claimant_id TEXT NOT NULL REFERENCES claimants(claimant_id),
            policy_id TEXT NOT NULL REFERENCES policies(policy_id),
            vehicle_id TEXT NOT NULL REFERENCES vehicles(vehicle_id),
            provider_id TEXT NOT NULL REFERENCES providers(provider_id),
            invoice_id TEXT NOT NULL REFERENCES invoices(invoice_id),
            claim_date TEXT,
            claim_amount REAL,
            claim_type TEXT,
            status TEXT,
            fraud_label INTEGER,
            description TEXT
        );

        INSERT INTO claimants VALUES ('CLT0001', 'John Doe', 35, 'Mumbai', 'M', 'Married');
        INSERT INTO providers VALUES ('PRV001', 'Auto Care', 'Mumbai', 'Garage', 4.5);
        INSERT INTO policies VALUES ('POL0001', 'CLT0001', '2023-01-01', '2024-01-01', 'Comprehensive', 15000, 0);
        INSERT INTO vehicles VALUES ('VEH0001', 'CLT0001', 'Tata', 'SUV', 'MH01AB1234', 2020);
        INSERT INTO invoices VALUES ('INV00001', 'PRV001', 55000, '2023-06-01', 'Repair invoice');
        INSERT INTO claims VALUES ('CLM00001', 'CLT0001', 'POL0001', 'VEH0001', 'PRV001', 'INV00001', '2023-06-02', 55000, 'Accident', 'Open', 1, 'Collision damage');
        INSERT INTO claims VALUES ('CLM00002', 'CLT0001', 'POL0001', 'VEH0001', 'PRV001', 'INV00001', '2023-06-03', 12000, 'Glass Damage', 'Approved', 0, 'Windshield crack');
    """)
    conn.commit()
    conn.close()
    return db_file


# ── 1. Model & Transition Rules ──────────────────────────────────────────────


def test_models_enums_and_transitions():
    assert is_valid_transition("NEW", "UNDER_REVIEW")
    assert is_valid_transition("NEW", "FALSE_POSITIVE")
    assert not is_valid_transition("NEW", "RESOLVED")  # cannot resolve without review

    assert is_valid_transition("UNDER_REVIEW", "ESCALATED")
    assert is_valid_transition("UNDER_REVIEW", "RESOLVED")
    assert is_valid_transition("UNDER_REVIEW", "FALSE_POSITIVE")
    assert is_valid_transition("UNDER_REVIEW", "NEW")

    assert is_valid_transition("ESCALATED", "RESOLVED")
    assert is_valid_transition("ESCALATED", "UNDER_REVIEW")

    assert is_valid_transition("RESOLVED", "UNDER_REVIEW")  # reopen
    assert is_valid_transition("FALSE_POSITIVE", "UNDER_REVIEW")

    # Invalid enum inputs
    assert not is_valid_transition("UNKNOWN", "RESOLVED")
    assert not is_valid_transition("NEW", "INVALID")


# ── 2. Case Creation & Persistence ───────────────────────────────────────────


def test_create_case_manual(temp_db):
    manager = CaseManager(db_path=temp_db)
    case = manager.create_case(
        claim_id="CLM00001",
        risk_score=0.85,
        risk_band="CRITICAL",
        priority="CRITICAL",
        reason="HIGH_FRAUD_PROBABILITY | HIGH_CLAIM_AMOUNT",
        notes="Initial alert triggered by XGBoost model",
        actor="RULE_ENGINE",
    )

    assert case.case_id == "CASE-CLM00001"
    assert case.claim_id == "CLM00001"
    assert case.status == CaseStatus.NEW.value
    assert case.risk_score == 0.85
    assert case.risk_band == "CRITICAL"
    assert case.priority == "CRITICAL"

    # Verify retrieval
    retrieved = manager.get_case("CASE-CLM00001")
    assert retrieved is not None
    assert retrieved.case_id == case.case_id
    assert retrieved.notes == "Initial alert triggered by XGBoost model"

    # Verify audit event
    history = manager.get_case_history("CASE-CLM00001")
    assert len(history["events"]) >= 1
    assert history["events"][0]["event_type"] == CaseEventType.CASE_CREATED.value
    assert history["events"][0]["actor"] == "RULE_ENGINE"
    assert len(history["notes"]) == 1
    assert history["notes"][0]["note_text"] == "Initial alert triggered by XGBoost model"


def test_create_duplicate_case_raises(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="CASE-001")
    with pytest.raises(ValueError, match="already exists"):
        manager.create_case(claim_id="CLM00001", case_id="CASE-001")


def test_create_cases_from_risk_scores(temp_db):
    manager = CaseManager(db_path=temp_db)
    created = manager.create_cases_from_risk_scores(min_risk_score=0.50)

    # In actual final_risk_scores.csv, there are 27 claims in HIGH and CRITICAL bands
    # Since only CLM00001 and CLM00002 exist in temp_db, create_cases should process matching claims
    assert isinstance(created, list)

    # Calling again should not create duplicates
    repeat = manager.create_cases_from_risk_scores(min_risk_score=0.50)
    assert len(repeat) == 0


# ── 3. Status Transitions & Investigator Assignment ──────────────────────────


def test_update_status_valid_and_invalid(temp_db):
    manager = CaseManager(db_path=temp_db)
    case = manager.create_case(claim_id="CLM00001", case_id="CASE-T1")

    # Invalid: NEW -> RESOLVED
    with pytest.raises(ValueError, match="Invalid transition"):
        manager.update_status("CASE-T1", "RESOLVED", actor="ADJUSTER")

    # Valid: NEW -> UNDER_REVIEW
    updated = manager.update_status("CASE-T1", "UNDER_REVIEW", actor="ADJUSTER", reason="Assigned for inquiry")
    assert updated.status == "UNDER_REVIEW"

    # Valid: UNDER_REVIEW -> ESCALATED
    escalated = manager.update_status("CASE-T1", "ESCALATED", actor="SR_INVESTIGATOR")
    assert escalated.status == "ESCALATED"

    # Check history
    history = manager.get_case_history("CASE-T1")
    status_events = [e for e in history["events"] if e["event_type"] == CaseEventType.STATUS_CHANGED.value]
    assert len(status_events) == 2
    assert status_events[0]["old_value"] == "NEW"
    assert status_events[0]["new_value"] == "UNDER_REVIEW"


def test_assign_investigator(temp_db):
    manager = CaseManager(db_path=temp_db)
    case = manager.create_case(claim_id="CLM00001", case_id="CASE-ASSIGN")
    assert case.status == "NEW"

    # Assigning to investigator auto-moves NEW to UNDER_REVIEW
    assigned = manager.assign_investigator("CASE-ASSIGN", investigator="Inv. Sharma", actor="SUPERVISOR")
    assert assigned.assigned_to == "Inv. Sharma"
    assert assigned.status == "UNDER_REVIEW"

    history = manager.get_case_history("CASE-ASSIGN")
    assign_events = [e for e in history["events"] if e["event_type"] == CaseEventType.INVESTIGATOR_ASSIGNED.value]
    assert len(assign_events) == 1
    assert assign_events[0]["new_value"] == "Inv. Sharma"


# ── 4. Case Notes & History ──────────────────────────────────────────────────


def test_add_notes_and_ordering(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="CASE-NOTE")

    n1 = manager.add_note("CASE-NOTE", author="Inv. Sharma", note_text="Interviewed provider regarding invoice.")
    n2 = manager.add_note("CASE-NOTE", author="Inv. Sharma", note_text="Damage photos inconsistent with repair cost.")

    assert n1.note_id is not None
    assert n2.note_id is not None
    assert n2.note_id > n1.note_id

    # Case record notes summary should reflect latest note
    updated_case = manager.get_case("CASE-NOTE")
    assert "Damage photos inconsistent" in updated_case.notes

    # Verify history
    hist = manager.get_case_history("CASE-NOTE")
    assert len(hist["notes"]) == 2
    assert hist["notes"][0]["note_text"] == "Interviewed provider regarding invoice."
    assert hist["notes"][1]["note_text"] == "Damage photos inconsistent with repair cost."


def test_empty_note_raises(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="CASE-EMPTY")
    with pytest.raises(ValueError, match="cannot be empty"):
        manager.add_note("CASE-EMPTY", author="Inv. Sharma", note_text="   ")


# ── 5. Case Resolution & Human-in-the-Loop Rule ─────────────────────────────


def test_resolve_case_human_review(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="CASE-RES")
    manager.assign_investigator("CASE-RES", "Inv. Sharma", actor="SUPERVISOR")

    # Invalid resolution status
    with pytest.raises(ValueError, match="must be RESOLVED or FALSE_POSITIVE"):
        manager.resolve_case("CASE-RES", "REJECTED", "Findings text", actor="Inv. Sharma")

    # Valid resolution
    resolved = manager.resolve_case(
        case_id="CASE-RES",
        resolution_status="RESOLVED",
        resolution_notes="Confirmed inflated billing and parts mismatch with surveyor.",
        actor="Inv. Sharma",
    )
    assert resolved.status == "RESOLVED"
    assert "Confirmed inflated billing" in resolved.resolution

    # CRITICAL GLOBAL RULE CHECK: The claim table in the database must NOT have its
    # original ground truth or fraud_label mutated automatically!
    with sqlite3.connect(temp_db) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT fraud_label, status FROM claims WHERE claim_id = 'CLM00001'")
        claim_row = cur.fetchone()
        assert claim_row["fraud_label"] == 1  # unchanged synthetic ground truth


def test_resolve_false_positive(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00002", case_id="CASE-FP")
    manager.assign_investigator("CASE-FP", "Inv. Patel", actor="SUPERVISOR")

    resolved = manager.resolve_case(
        case_id="CASE-FP",
        resolution_status="FALSE_POSITIVE",
        resolution_notes="Legitimate glass damage confirmed by third-party surveyor; alert dismissed.",
        actor="Inv. Patel",
    )
    assert resolved.status == "FALSE_POSITIVE"
    assert "surveyor" in resolved.resolution


# ── 6. Querying & Statistics ─────────────────────────────────────────────────


def test_list_cases_and_filters(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="C1", priority="CRITICAL", risk_score=0.85)
    manager.create_case(claim_id="CLM00002", case_id="C2", priority="LOW", risk_score=0.20)
    manager.assign_investigator("C1", "Inv. Sharma", actor="SUPERVISOR")

    all_cases = manager.list_cases()
    assert len(all_cases) == 2

    # Filter by priority
    crit = manager.list_cases(priority="CRITICAL")
    assert len(crit) == 1
    assert crit[0].case_id == "C1"

    # Filter by assigned_to
    assigned = manager.list_cases(assigned_to="Inv. Sharma")
    assert len(assigned) == 1
    assert assigned[0].case_id == "C1"

    # Filter by min_risk
    high_risk = manager.list_cases(min_risk=0.50)
    assert len(high_risk) == 1
    assert high_risk[0].case_id == "C1"


def test_case_statistics(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(claim_id="CLM00001", case_id="C1", priority="HIGH")
    manager.create_case(claim_id="CLM00002", case_id="C2", priority="LOW")
    manager.assign_investigator("C1", "Inv. Sharma", actor="SUPERVISOR")
    manager.add_note("C1", "Inv. Sharma", "Initial audit note")

    stats = manager.get_case_statistics()
    assert stats["total_cases"] == 2
    assert stats["assigned_cases"] == 1
    assert stats["unassigned_cases"] == 1
    assert stats["total_notes"] == 1
    assert stats["total_events"] >= 3


# ── 7. Investigation Dossier ─────────────────────────────────────────────────


def test_build_investigation_dossier(temp_db):
    manager = CaseManager(db_path=temp_db)
    manager.create_case(
        claim_id="CLM00001",
        case_id="CASE-DOSSIER",
        risk_score=0.76,
        risk_band="CRITICAL",
        reason="HIGH_FRAUD_PROBABILITY | HIGH_CLAIM_AMOUNT",
    )
    manager.add_note("CASE-DOSSIER", "Inv. Sharma", "Inspected invoice details.")

    dossier = build_investigation_dossier("CASE-DOSSIER", db_path=temp_db)
    assert dossier["case"]["case_id"] == "CASE-DOSSIER"
    assert dossier["claim"]["claim_id"] == "CLM00001"
    assert dossier["claimant"]["name"] == "John Doe"
    assert dossier["provider"]["provider_name"] == "Auto Care"
    assert dossier["policy"]["policy_type"] == "Comprehensive"
    assert dossier["vehicle"]["make"] == "Tata"
    assert dossier["invoice"]["invoice_amount"] == 55000
    assert dossier["risk_breakdown"]["final_risk_score"] == 0.76
    assert len(dossier["notes"]) == 1
    assert len(dossier["events"]) >= 2


def test_investigation_summary_helper():
    s = investigation_summary(claim={"id": "CLM00001"}, signals={"fraud_prob": 0.8})
    assert s["review_required"] is True
    assert s["human_decision_pending"] is True


# ── 8. API Service & Routes Integration ──────────────────────────────────────


def test_case_service_facade(temp_db):
    service = CaseService(db_path=temp_db)
    c = service.create_case(claim_id="CLM00001", case_id="CASE-SRV", risk_score=0.65, risk_band="HIGH")
    assert c["case_id"] == "CASE-SRV"

    up = service.update_status("CASE-SRV", "UNDER_REVIEW", actor="TEST")
    assert up["status"] == "UNDER_REVIEW"

    asg = service.assign_investigator("CASE-SRV", "Inv. Khan", actor="ADMIN")
    assert asg["assigned_to"] == "Inv. Khan"

    nt = service.add_note("CASE-SRV", "Inv. Khan", "Service note text")
    assert nt["note_text"] == "Service note text"

    hist = service.get_case_history("CASE-SRV")
    assert len(hist["events"]) >= 3

    res = service.resolve_case("CASE-SRV", "RESOLVED", "Legitimate resolution", actor="Inv. Khan")
    assert res["status"] == "RESOLVED"


def test_fastapi_case_routes():
    client = TestClient(app)

    # 1. Health check
    r = client.get("/health")
    assert r.status_code == 200

    # 2. List cases
    r = client.get("/cases")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # 3. Stats summary
    r = client.get("/cases/stats/summary")
    assert r.status_code == 200
    assert "total_cases" in r.json()

    # 4. Create case via API with unique case_id
    import uuid
    test_case_id = f"CASE-API-{uuid.uuid4().hex[:8]}"
    payload = {
        "claim_id": "CLM00001",
        "case_id": test_case_id,
        "risk_score": 0.72,
        "risk_band": "HIGH",
        "priority": "HIGH",
        "reason": "HIGH_FRAUD_PROBABILITY",
        "notes": "API test creation",
    }
    r = client.post("/cases", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["case_id"] == test_case_id

    # 5. Get case by ID
    r = client.get(f"/cases/{test_case_id}")
    assert r.status_code == 200
    assert r.json()["case_id"] == test_case_id

    # 6. Assign investigator
    r = client.post(f"/cases/{test_case_id}/assign", json={"investigator": "Inv. API"})
    assert r.status_code == 200
    assert r.json()["assigned_to"] == "Inv. API"

    # 7. Add note
    r = client.post(f"/cases/{test_case_id}/notes", json={"author": "Inv. API", "note_text": "Note from API test"})
    assert r.status_code == 201
    assert r.json()["note_text"] == "Note from API test"

    # 8. Get history
    r = client.get(f"/cases/{test_case_id}/history")
    assert r.status_code == 200
    hist = r.json()
    assert len(hist["events"]) >= 2
    assert len(hist["notes"]) >= 2

    # 9. Resolve case
    r = client.post(f"/cases/{test_case_id}/resolve", json={
        "resolution_status": "FALSE_POSITIVE",
        "resolution_notes": "API test resolved as false positive after review",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "FALSE_POSITIVE"

    # 10. Dossier
    r = client.get(f"/cases/{test_case_id}/dossier")
    assert r.status_code == 200
    assert "risk_breakdown" in r.json()

