"""
src/explainability/graph_explainer.py
------------------------------------
Topological graph evidence extraction for fraud explainability.
Extracts verifiable, evidence-based graph signals:
- Suspicious connections
- High-degree entities
- Repeated relationships
- Neighboring flagged claims
Directly grounded in network tables and engineered graph features. Zero hallucinated claims.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "database" / "fraud_detection.db"
GRAPH_FEATURES_PATH = ROOT / "data" / "features" / "graph_features.csv"
RISK_SCORES_PATH = ROOT / "data" / "features" / "final_risk_scores.csv"


class GraphExplainer:
    """
    Evidence-based graph explainer for insurance claim networks.
    """

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        graph_features_path: Optional[str | Path] = None,
        risk_scores_path: Optional[str | Path] = None,
    ):
        self.db_path = Path(db_path or DB_PATH)
        self.features_path = Path(graph_features_path or GRAPH_FEATURES_PATH)
        self.risk_path = Path(risk_scores_path or RISK_SCORES_PATH)

        self.graph_features: pd.DataFrame = pd.DataFrame()
        if self.features_path.exists():
            self.graph_features = pd.read_csv(self.features_path, keep_default_na=False)

        self.risk_scores: pd.DataFrame = pd.DataFrame()
        if self.risk_path.exists():
            self.risk_scores = pd.read_csv(self.risk_path, keep_default_na=False)

    def explain_claim_graph(self, claim_id: str) -> Dict[str, Any]:
        """
        Extracts verified graph signals for a specific claim.
        Returns:
          - suspicious_connections
          - high_degree_entities
          - repeated_relationships
          - neighboring_flagged_claims
        """
        cid = claim_id.strip()

        suspicious_connections: List[Dict[str, Any]] = []
        high_degree_entities: List[Dict[str, Any]] = []
        repeated_relationships: List[Dict[str, Any]] = []
        neighboring_flagged_claims: List[Dict[str, Any]] = []

        # 1. Fetch graph features for this claim if available
        gf_row = {}
        if not self.graph_features.empty:
            match = self.graph_features[self.graph_features["claim_id"] == cid]
            if not match.empty:
                gf_row = match.iloc[0].to_dict()

        # 2. Fetch relational entities from SQLite
        claim_data = {}
        related_claims = []
        if self.db_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT c.*,
                           cl.name AS claimant_name, cl.city AS claimant_city,
                           p.policy_type, p.premium,
                           pr.provider_name, pr.city AS provider_city, pr.rating AS provider_rating,
                           v.make AS vehicle_make, v.vehicle_type
                    FROM claims c
                    LEFT JOIN claimants cl ON c.claimant_id = cl.claimant_id
                    LEFT JOIN policies p ON c.policy_id = p.policy_id
                    LEFT JOIN providers pr ON c.provider_id = pr.provider_id
                    LEFT JOIN vehicles v ON c.vehicle_id = v.vehicle_id
                    WHERE c.claim_id = ?
                    """,
                    (cid,),
                )
                r = cur.fetchone()
                if r:
                    claim_data = dict(r)

                # Fetch neighbor claims sharing claimant, provider, or vehicle
                if claim_data:
                    clt_id = claim_data.get("claimant_id")
                    prv_id = claim_data.get("provider_id")
                    veh_id = claim_data.get("vehicle_id")

                    cur.execute(
                        """
                        SELECT c.claim_id, c.claim_amount, c.claim_date, c.claim_type, c.status, c.fraud_label,
                               c.claimant_id, c.provider_id, c.vehicle_id
                        FROM claims c
                        WHERE (c.claimant_id = ? OR c.provider_id = ? OR c.vehicle_id = ?) AND c.claim_id != ?
                        """,
                        (clt_id, prv_id, veh_id, cid),
                    )
                    related_claims = [dict(row) for row in cur.fetchall()]

        # ── A. Suspicious Connections ────────────────────────────────────────
        susp_count = int(gf_row.get("suspicious_neighbor_count", 0)) if gf_row else 0
        if susp_count > 0:
            suspicious_connections.append({
                "type": "ELEVATED_SUSPICIOUS_NEIGHBOR_COUNT",
                "description": f"Ego-network contains {susp_count} neighboring node(s) with flagged anomalous behavior",
                "evidence_value": susp_count,
            })

        claim_betweenness = float(gf_row.get("claim_betweenness", 0.0)) if gf_row else 0.0
        if claim_betweenness > 0.005:
            suspicious_connections.append({
                "type": "HIGH_BETWEENNESS_BRIDGE",
                "description": f"Claim acts as an informational bridge between distinct network clusters (betweenness: {claim_betweenness:.4f})",
                "evidence_value": round(claim_betweenness, 4),
            })

        # Location mismatch between claimant and provider
        if claim_data:
            c_city = claim_data.get("claimant_city")
            p_city = claim_data.get("provider_city")
            if c_city and p_city and c_city != p_city:
                suspicious_connections.append({
                    "type": "CROSS_TERRITORY_PROVIDER_SERVICE",
                    "description": f"Claimant registered in '{c_city}' serviced by provider in distant territory '{p_city}'",
                    "evidence_value": f"{c_city} -> {p_city}",
                })

        # ── B. High-Degree Entities ──────────────────────────────────────────
        if gf_row:
            prv_deg = int(gf_row.get("provider_degree", 0))
            prv_claim_count = int(gf_row.get("provider_claim_count", 0))
            if prv_deg >= 15 or prv_claim_count >= 8:
                high_degree_entities.append({
                    "entity_type": "Provider",
                    "entity_id": claim_data.get("provider_id", "Unknown"),
                    "name": claim_data.get("provider_name", "Provider"),
                    "degree": prv_deg,
                    "claim_count": prv_claim_count,
                    "description": f"High-volume service provider '{claim_data.get('provider_name')}' connected to {prv_deg} edges and {prv_claim_count} claims",
                })

            clt_deg = int(gf_row.get("claimant_degree", 0))
            clt_claim_count = int(gf_row.get("claimant_claim_count", 0))
            if clt_deg >= 6 or clt_claim_count >= 3:
                high_degree_entities.append({
                    "entity_type": "Claimant",
                    "entity_id": claim_data.get("claimant_id", "Unknown"),
                    "name": claim_data.get("claimant_name", "Claimant"),
                    "degree": clt_deg,
                    "claim_count": clt_claim_count,
                    "description": f"Repeat claimant '{claim_data.get('claimant_name')}' filed {clt_claim_count} separate claims in the network",
                })

            veh_deg = int(gf_row.get("vehicle_degree", 0))
            if veh_deg >= 5:
                high_degree_entities.append({
                    "entity_type": "Vehicle",
                    "entity_id": claim_data.get("vehicle_id", "Unknown"),
                    "name": f"{claim_data.get('vehicle_make', '')} {claim_data.get('vehicle_type', '')}".strip(),
                    "degree": veh_deg,
                    "claim_count": veh_deg // 2,
                    "description": f"Vehicle '{claim_data.get('vehicle_id')}' involved in multiple policy incidents (degree: {veh_deg})",
                })

        # ── C. Repeated Relationships ────────────────────────────────────────
        rep_cp = int(gf_row.get("repeated_claimant_provider", 0)) if gf_row else 0
        if rep_cp > 0:
            repeated_relationships.append({
                "relationship_type": "REPEATED_CLAIMANT_PROVIDER",
                "entity_pair": f"{claim_data.get('claimant_id')} <-> {claim_data.get('provider_id')}",
                "count": rep_cp,
                "description": f"Claimant and provider share {rep_cp} previous claim interaction(s), suggesting preferred collusion or steering",
            })

        # Check vehicle repetition
        if claim_data:
            veh_id = claim_data.get("vehicle_id")
            veh_claims = [rc for rc in related_claims if rc.get("vehicle_id") == veh_id]
            if len(veh_claims) > 1:
                repeated_relationships.append({
                    "relationship_type": "REPEATED_VEHICLE_CLAIMS",
                    "entity_pair": f"Vehicle: {veh_id}",
                    "count": len(veh_claims),
                    "description": f"Vehicle was claimed across {len(veh_claims)} separate incidents",
                })

        # ── D. Neighboring Flagged Claims ────────────────────────────────────
        # Map risk scores to neighbor claims if available
        risk_map = {}
        if not self.risk_scores.empty:
            for _, r in self.risk_scores.iterrows():
                risk_map[str(r["claim_id"])] = {
                    "final_risk_score": float(r.get("final_risk_score", 0.0)),
                    "risk_band": str(r.get("risk_band", "LOW")),
                }

        for rc in related_claims:
            rc_id = rc["claim_id"]
            is_fraud = rc.get("fraud_label") == 1
            r_info = risk_map.get(rc_id, {})
            r_score = r_info.get("final_risk_score", 0.0)
            is_high_risk = r_score >= 0.50

            if is_fraud or is_high_risk:
                # Determine linking entity
                shared = []
                if rc.get("claimant_id") == claim_data.get("claimant_id"):
                    shared.append("SHARED_CLAIMANT")
                if rc.get("provider_id") == claim_data.get("provider_id"):
                    shared.append("SHARED_PROVIDER")
                if rc.get("vehicle_id") == claim_data.get("vehicle_id"):
                    shared.append("SHARED_VEHICLE")

                neighboring_flagged_claims.append({
                    "claim_id": rc_id,
                    "shared_relationship": " & ".join(shared) or "CONNECTED_NEIGHBOR",
                    "claim_amount": float(rc.get("claim_amount", 0.0)),
                    "claim_type": rc.get("claim_type", "N/A"),
                    "confirmed_fraud": is_fraud,
                    "final_risk_score": round(r_score, 4),
                    "risk_band": r_info.get("risk_band", "HIGH" if is_high_risk else "LOW"),
                    "description": (
                        f"Neighbor claim '{rc_id}' (${rc.get('claim_amount', 0):,.2f}) "
                        f"via {' & '.join(shared)} is {'CONFIRMED FRAUD' if is_fraud else 'HIGH RISK'} "
                        f"(Score: {r_score:.4f})"
                    ),
                })

        return {
            "claim_id": cid,
            "suspicious_connections": suspicious_connections,
            "high_degree_entities": high_degree_entities,
            "repeated_relationships": repeated_relationships,
            "neighboring_flagged_claims": neighboring_flagged_claims,
            "fraud_neighbor_count": int(gf_row.get("fraud_neighbor_count", len(neighboring_flagged_claims))),
            "fraud_neighbor_ratio": float(round(gf_row.get("fraud_neighbor_ratio", 0.0), 4)),
        }
