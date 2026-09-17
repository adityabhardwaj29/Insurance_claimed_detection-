"""
src/explainability/claim_explainer.py
------------------------------------
Unified claim explainability orchestrator.
Synthesizes:
1. Supervised ML SHAP Shapley values (top positive and negative factors)
2. Graph topological evidence (suspicious connections, high-degree entities, repeated links, flagged neighbors)
3. Plain-language investigator narrative summary
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.explainability.graph_explainer import GraphExplainer
from src.explainability.shap_explainer import ShapExplainer

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
FEATURES_CSV = ROOT / "data" / "features" / "final_claim_features.csv"


class ClaimExplainer:
    """
    Unified multimodal claim explainer integrating SHAP and Knowledge Graph evidence.
    """

    def __init__(
        self,
        shap_explainer: Optional[ShapExplainer] = None,
        graph_explainer: Optional[GraphExplainer] = None,
        features_path: Optional[str | Path] = None,
    ):
        self.shap = shap_explainer or ShapExplainer()
        self.graph = graph_explainer or GraphExplainer()
        self.features_path = Path(features_path or FEATURES_CSV)

        self._claims_cache: pd.DataFrame = pd.DataFrame()
        if self.features_path.exists():
            self._claims_cache = pd.read_csv(self.features_path, keep_default_na=False)

    def explain_claim(self, claim_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Generates comprehensive, multi-angle explainability report for a claim.
        """
        cid = claim_id.strip()

        # 1. Fetch feature row for this claim
        row_dict = {}
        if not self._claims_cache.empty:
            match = self._claims_cache[self._claims_cache["claim_id"] == cid]
            if not match.empty:
                row_dict = match.iloc[0].to_dict()

        if not row_dict:
            row_dict = {"claim_id": cid}

        # 2. Compute SHAP explanations
        shap_res = self.shap.explain_instance(row_dict, top_k=top_k, claim_id=cid)

        # 3. Compute Graph evidence explanations
        graph_res = self.graph.explain_claim_graph(cid)

        # 4. Synthesize Plain-English narrative summary
        summary = self._build_narrative_summary(shap_res, graph_res)

        # 5. Assemble exact requested schema
        return {
            "claim_id": cid,
            "fraud_probability": shap_res["fraud_probability"],
            "base_value": shap_res.get("base_value", 0.0),
            "top_factors": shap_res["top_factors"],
            "top_positive_factors": shap_res["top_positive_factors"],
            "top_negative_factors": shap_res["top_negative_factors"],
            "graph_explanation": {
                "suspicious_connections": graph_res["suspicious_connections"],
                "high_degree_entities": graph_res["high_degree_entities"],
                "repeated_relationships": graph_res["repeated_relationships"],
                "neighboring_flagged_claims": graph_res["neighboring_flagged_claims"],
                "fraud_neighbor_count": graph_res["fraud_neighbor_count"],
                "fraud_neighbor_ratio": graph_res["fraud_neighbor_ratio"],
            },
            "summary_text": summary,
        }

    def _build_narrative_summary(
        self,
        shap_res: Dict[str, Any],
        graph_res: Dict[str, Any],
    ) -> str:
        """Constructs an explainable, plain-English summary for human investigators."""
        prob = shap_res["fraud_probability"]
        pos_factors = shap_res.get("top_positive_factors", [])
        neg_factors = shap_res.get("top_negative_factors", [])
        graph_flagged = graph_res.get("neighboring_flagged_claims", [])
        rep_rel = graph_res.get("repeated_relationships", [])
        high_deg = graph_res.get("high_degree_entities", [])

        narrative_parts = []

        # Risk level overview
        if prob >= 0.70:
            narrative_parts.append(
                f"Claim exhibits CRITICAL fraud probability of {prob*100:.1f}%, driven by strong supervised and behavioral signals."
            )
        elif prob >= 0.40:
            narrative_parts.append(
                f"Claim exhibits ELEVATED fraud risk of {prob*100:.1f}%, warranting human investigator review."
            )
        else:
            narrative_parts.append(
                f"Claim exhibits LOW fraud probability of {prob*100:.1f}%, consistent with typical legitimate claim patterns."
            )

        # Key ML drivers
        if pos_factors:
            top_pos_names = [f"'{f['feature']}' (+{f['impact']:.2f})" for f in pos_factors[:3]]
            narrative_parts.append(
                f"Top risk-increasing factors identified by model: {', '.join(top_pos_names)}."
            )

        if neg_factors and prob < 0.70:
            top_neg_names = [f"'{f['feature']}' ({f['impact']:.2f})" for f in neg_factors[:2]]
            narrative_parts.append(
                f"Mitigating legitimacy factors: {', '.join(top_neg_names)}."
            )

        # Key Graph drivers
        if graph_flagged:
            narrative_parts.append(
                f"Network topology reveals {len(graph_flagged)} connected claim(s) with confirmed fraud or high risk in the immediate ego-network."
            )

        if rep_rel:
            narrative_parts.append(
                f"Found {len(rep_rel)} repeated entity relationship(s) across separate claims (e.g. repeated claimant-provider interaction)."
            )

        if high_deg:
            hub_names = [f"{h['entity_type']} {h.get('name', '')} (degree {h['degree']})" for h in high_deg[:2]]
            narrative_parts.append(
                f"Entities with high network connectivity involved: {', '.join(hub_names)}."
            )

        return " ".join(narrative_parts)


def explain_claim(claim_id: str) -> Dict[str, Any]:
    """Convenience helper to explain any claim."""
    explainer = ClaimExplainer()
    return explainer.explain_claim(claim_id)
