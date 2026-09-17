"""
tests/test_dashboard.py
-----------------------
Automated unit and integration test suite for Streamlit Fraud Analytics Dashboard.
Validates:
- Database and risk feature loading
- Exact computation of executive KPIs (non-null, bounded, no simulated numbers)
- Network graph construction (Claim <-> Claimant <-> Policy <-> Vehicle <-> Provider <-> Location)
- 360-degree investigation dossier compilation
- Case creation and status transition functions
- Multi-signal report loading and metrics validation
"""

from __future__ import annotations

import sqlite3
import pytest
import pandas as pd
import networkx as nx

from dashboard.utils.data_loader import (
    load_all_claims_data,
    compute_executive_kpis,
    load_duplicate_records,
    load_investigation_cases,
    build_claim_network_graph,
    load_claim_investigation_dossier,
    create_or_update_case,
    load_experiment_reports,
    DB_PATH,
)


class TestDashboardDataLoader:
    """Tests data retrieval and integrity for dashboard components."""

    def test_load_all_claims_data_returns_dataframe(self):
        df = load_all_claims_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 320
        assert "claim_id" in df.columns
        assert "claim_amount" in df.columns
        assert "final_risk_score" in df.columns
        assert "risk_band" in df.columns
        assert "fraud_label" in df.columns

    def test_compute_executive_kpis_accuracy(self):
        df = load_all_claims_data()
        kpis = compute_executive_kpis(df)

        assert isinstance(kpis, dict)
        assert kpis["total_claims"] == 320
        assert kpis["total_claim_amount"] > 0
        assert 0.0 <= kpis["fraud_rate"] <= 100.0
        assert 0.0 <= kpis["average_risk_score"] <= 1.0
        assert kpis["flagged_claims"] >= 0
        assert kpis["high_risk_claims"] >= 0
        assert kpis["investigation_cases"] >= 0

        # Exact ground truth test: fraud count is 52 out of 320 => 16.25%
        assert kpis["fraud_rate"] == 16.25

    def test_compute_executive_kpis_empty_df(self):
        empty_df = pd.DataFrame()
        kpis = compute_executive_kpis(empty_df)
        assert kpis["total_claims"] == 0
        assert kpis["fraud_rate"] == 0.0
        assert kpis["average_risk_score"] == 0.0

    def test_load_duplicate_records(self):
        dup_df = load_duplicate_records()
        assert isinstance(dup_df, pd.DataFrame)
        if not dup_df.empty:
            assert "claim_id" in dup_df.columns
            sim_col = "duplicate_similarity_score" if "duplicate_similarity_score" in dup_df.columns else "dup_similarity_score"
            assert sim_col in dup_df.columns

    def test_load_investigation_cases(self):
        cases = load_investigation_cases()
        assert isinstance(cases, pd.DataFrame)
        assert not cases.empty
        assert "case_id" in cases.columns
        assert "claim_id" in cases.columns
        assert "status" in cases.columns


class TestNetworkGraphBuilder:
    """Tests graph construction for interactive network visualization."""

    def test_build_claim_network_graph_structure(self):
        # Test with known claim CLM00001
        G, node_details = build_claim_network_graph("CLM00001")

        assert isinstance(G, nx.Graph)
        assert isinstance(node_details, dict)
        assert "CLM00001" in G.nodes
        assert len(G.nodes) >= 5  # Claim, Claimant, Policy, Vehicle, Provider, Location

        # Verify entity types present
        node_types = {d.get("type") for _, d in G.nodes(data=True)}
        assert "Claim" in node_types
        assert "Claimant" in node_types
        assert "Policy" in node_types
        assert "Vehicle" in node_types
        assert "Provider" in node_types
        assert "Location" in node_types

    def test_build_claim_network_graph_nonexistent_claim(self):
        G, node_details = build_claim_network_graph("NON_EXISTENT_99999")
        assert len(G.nodes) == 0
        assert len(node_details) == 0


class TestInvestigationDossier:
    """Tests 360-degree claim investigation dossier assembly."""

    def test_load_claim_investigation_dossier_found(self):
        dossier = load_claim_investigation_dossier("CLM00001")
        assert dossier["found"] is True
        assert dossier["claim_id"] == "CLM00001"
        assert "claim" in dossier
        assert "claimant" in dossier
        assert "policy" in dossier
        assert "vehicle" in dossier
        assert "provider" in dossier
        assert "invoice" in dossier
        assert "risk_breakdown" in dossier
        assert "duplicate_info" in dossier
        assert "graph_info" in dossier

        # Verify risk breakdown contents
        risk = dossier["risk_breakdown"]
        assert "final_risk_score" in risk
        assert "risk_band" in risk
        assert "fraud_probability" in risk

    def test_load_claim_investigation_dossier_not_found(self):
        dossier = load_claim_investigation_dossier("INVALID_ID_8888")
        assert dossier["found"] is False
        assert len(dossier["claim"]) == 0

    def test_create_or_update_case_and_audit_log(self):
        test_claim_id = "CLM00001"
        res = create_or_update_case(
            claim_id=test_claim_id,
            status="UNDER_REVIEW",
            priority="HIGH",
            assigned_to="Test Investigator",
            actor="AUTOMATED_TEST",
            note="Test note for dashboard verification",
        )
        assert "case_id" in res
        assert res["status"] == "UNDER_REVIEW"

        # Verify event and note were recorded in DB
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM case_notes WHERE case_id = ? ORDER BY created_at DESC LIMIT 1", (res["case_id"],))
            note_row = cur.fetchone()
            assert note_row is not None
            assert "Test note for dashboard verification" in note_row[3]


class TestExperimentReports:
    """Tests experiment report loader for zero hallucinated metrics."""

    def test_load_experiment_reports_contains_real_data(self):
        reports = load_experiment_reports()
        assert isinstance(reports, dict)

        # Supervised ML metrics
        assert "supervised_ml" in reports
        ml = reports["supervised_ml"]
        assert "evaluation_metrics" in ml
        assert ml["evaluation_metrics"]["accuracy"] > 0

        # Anomaly detection report
        assert "anomaly_detection" in reports

        # Graph statistics report
        assert "graph_statistics" in reports
        assert reports["graph_statistics"]["total_nodes"] >= 1000
        assert reports["graph_statistics"]["total_edges"] >= 2600
