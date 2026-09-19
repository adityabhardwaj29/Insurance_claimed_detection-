"""
api/routes/reports.py
---------------------
Endpoints for comprehensive claim fraud investigation report generation.
Produces an audit-ready, structured report suitable for human review, compliance, and PDF export.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException

from api.services.claim_service import ClaimService
from api.services.graph_service import GraphService
from api.services.document_service import DocumentService
from api.db import db

router = APIRouter(prefix="/api/reports", tags=["reports"])
claim_service = ClaimService()
graph_service = GraphService()


@router.get("/claim/{claim_id}")
def generate_claim_investigation_report(claim_id: str) -> Dict[str, Any]:
    """
    Generates a formal, regulatory-grade investigation report containing:
    - Executive summary & final decision
    - Claim & claimant profile
    - Policy coverage & underwriting verification
    - Vehicle / Asset & Provider details
    - Multi-signal Hybrid Risk Analysis & calibrated sub-scores
    - SHAP explainable AI attribution factors
    - Duplicate claim similarity check results
    - Collusion network & graph topology analysis
    - Forensic investigator notes & submitted evidence
    - Chronological immutable audit event timeline
    """
    cid = claim_id.strip()
    claim_detail = claim_service.get_claim_detail(cid)
    if not claim_detail:
        raise HTTPException(status_code=404, detail=f"Claim '{cid}' not found")

    risk_info = claim_service.get_claim_risk(cid)
    exp_info = claim_service.get_claim_explanation(cid)
    dup_info = claim_service.get_claim_duplicates(cid)
    graph_info = graph_service.get_claim_subnetwork(cid)
    documents = DocumentService.get_documents_by_claim(cid)

    case_id = f"CASE-{cid}"
    case_row = db.query_one("SELECT * FROM investigation_cases WHERE case_id = ? OR claim_id = ?", (case_id, cid))
    notes = db.query_all("SELECT * FROM case_notes WHERE case_id = ? ORDER BY created_at ASC", (case_id,))
    events = db.query_all("SELECT * FROM case_events WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))

    return {
        "report_id": f"REP-{cid}",
        "generated_at": db.query_one("SELECT CURRENT_TIMESTAMP as now")["now"],
        "claim": claim_detail,
        "risk_assessment": risk_info,
        "explainability": exp_info,
        "duplicate_findings": dup_info,
        "network_analysis": graph_info,
        "investigation_case": case_row,
        "investigator_notes": notes,
        "supporting_documents": documents,
        "audit_timeline": events,
    }
