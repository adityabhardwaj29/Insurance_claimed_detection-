"""
api/services/graph_service.py
-----------------------------
Service layer for network topology queries, ego-subnetwork extraction,
and real-time graph risk calculations.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils.config import settings

logger = logging.getLogger(__name__)


class GraphService:
    """Provides network graph lookups and topological analysis."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.nodes_path = settings.GRAPH_NODES_PATH
        self.edges_path = settings.GRAPH_EDGES_PATH
        self.graph_features_path = settings.ROOT / "data" / "features" / "graph_features.csv"

    def get_claim_subnetwork(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Extracts the ego subnetwork around a claim: claimant, provider,
        connected claims, and edges.
        """
        cid = claim_id.strip()

        # 1. Lookup claim relational details
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM claims WHERE claim_id = ?", (cid,))
            c_row = cur.fetchone()
            if not c_row:
                return None
            claim_data = dict(c_row)

        claimant_id = claim_data["claimant_id"]
        provider_id = claim_data["provider_id"]
        policy_id = claim_data["policy_id"]
        vehicle_id = claim_data["vehicle_id"]

        # 2. Lookup graph topological features for this claim
        clt_deg = 1
        prv_count = 1
        fnr = 0.0
        susp_count = 0
        repeated = 0
        graph_risk = 0.40

        if self.graph_features_path.exists():
            try:
                gf = pd.read_csv(self.graph_features_path, keep_default_na=False)
                match = gf[gf["claim_id"] == cid]
                if not match.empty:
                    r = match.iloc[0]
                    clt_deg = int(r.get("claimant_degree", 1))
                    prv_count = int(r.get("provider_claim_count", 1))
                    fnr = float(r.get("fraud_neighbor_ratio", 0.0))
                    susp_count = int(r.get("suspicious_neighbor_count", 0))
                    repeated = int(r.get("repeated_claimant_provider", 0))
            except Exception as e:
                logger.warning("Could not read graph features for %s: %s", cid, e)

        # 3. Assemble subnetwork nodes
        nodes: List[Dict[str, Any]] = [
            {"id": cid, "label": f"Claim: {cid}", "type": "Claim", "fraud": int(claim_data.get("fraud_label", 0))},
            {"id": claimant_id, "label": f"Claimant: {claimant_id}", "type": "Claimant"},
            {"id": provider_id, "label": f"Provider: {provider_id}", "type": "Provider"},
            {"id": policy_id, "label": f"Policy: {policy_id}", "type": "Policy"},
            {"id": vehicle_id, "label": f"Vehicle: {vehicle_id}", "type": "Vehicle"},
        ]

        # 4. Find other claims sharing claimant or provider
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT claim_id, fraud_label FROM claims
                WHERE (claimant_id = ? OR provider_id = ?) AND claim_id != ?
                LIMIT 10
                """,
                (claimant_id, provider_id, cid),
            )
            sibling_rows = cur.fetchall()

        edges: List[Dict[str, Any]] = [
            {"source": claimant_id, "target": cid, "relationship": "FILED_BY"},
            {"source": cid, "target": provider_id, "relationship": "SERVICED_BY"},
            {"source": cid, "target": policy_id, "relationship": "UNDER_POLICY"},
            {"source": cid, "target": vehicle_id, "relationship": "INVOLVES_VEHICLE"},
        ]

        for s in sibling_rows:
            s_id = s["claim_id"]
            s_fraud = int(s["fraud_label"])
            nodes.append({
                "id": s_id,
                "label": f"Claim: {s_id}",
                "type": "ConnectedClaim",
                "fraud": s_fraud,
            })
            edges.append({
                "source": provider_id,
                "target": s_id,
                "relationship": "SHARED_PROVIDER",
            })

        return {
            "claim_id": cid,
            "claimant_id": claimant_id,
            "provider_id": provider_id,
            "claimant_degree": clt_deg,
            "provider_claim_count": prv_count,
            "fraud_neighbor_ratio": round(fnr, 4),
            "suspicious_neighbor_count": susp_count,
            "nodes": nodes,
            "edges": edges,
        }

    def analyze_graph(
        self,
        claim_id: Optional[str] = None,
        claimant_id: Optional[str] = None,
        provider_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Computes topological analysis for input entity parameters."""
        if claim_id:
            sub = self.get_claim_subnetwork(claim_id)
            if sub:
                conn_claims = len(sub["nodes"]) - 5
                # Composite graph risk formula
                fnr = sub["fraud_neighbor_ratio"]
                clt_deg = sub["claimant_degree"]
                prv_cnt = sub["provider_claim_count"]
                susp = sub["suspicious_neighbor_count"]
                risk = min(1.0, 0.35 * fnr + 0.20 * (clt_deg / 10.0) + 0.20 * (prv_cnt / 25.0) + 0.10 * (susp / 5.0))
                return {
                    "claim_id": claim_id,
                    "graph_risk_score": round(risk, 4),
                    "claimant_degree": clt_deg,
                    "provider_claim_count": prv_cnt,
                    "fraud_neighbor_ratio": fnr,
                    "suspicious_neighbor_count": susp,
                    "repeated_claimant_provider": 1 if prv_cnt > 1 else 0,
                    "connected_claim_count": conn_claims,
                    "network_summary": f"Claim {claim_id} has {clt_deg} claimant connections and {prv_cnt} provider claims with fraud neighbor ratio {fnr:.2f}.",
                }

        # Fallback if arbitrary claimant/provider queried
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            clt_cnt = 1
            prv_cnt = 1
            if claimant_id:
                cur.execute("SELECT COUNT(*) FROM claims WHERE claimant_id = ?", (claimant_id,))
                clt_cnt = cur.fetchone()[0] or 1
            if provider_id:
                cur.execute("SELECT COUNT(*) FROM claims WHERE provider_id = ?", (provider_id,))
                prv_cnt = cur.fetchone()[0] or 1

        risk = min(1.0, 0.20 * (clt_cnt / 10.0) + 0.20 * (prv_cnt / 25.0))
        return {
            "claim_id": claim_id,
            "graph_risk_score": round(risk, 4),
            "claimant_degree": clt_cnt,
            "provider_claim_count": prv_cnt,
            "fraud_neighbor_ratio": 0.0,
            "suspicious_neighbor_count": 0,
            "repeated_claimant_provider": 1 if (clt_cnt > 1 and prv_cnt > 1) else 0,
            "connected_claim_count": clt_cnt + prv_cnt,
            "network_summary": f"Entity analysis: claimant count={clt_cnt}, provider claim volume={prv_cnt}.",
        }


# Convenience module-level
def get_network(claim_id: str) -> Dict[str, Any]:
    svc = GraphService()
    res = svc.get_claim_subnetwork(claim_id)
    return res if res else {"claim_id": claim_id, "nodes": [], "edges": []}
