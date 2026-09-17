"""
src/explainability package
--------------------------
Explainable AI (XAI) and Knowledge Graph Evidence Engine for insurance fraud detection.
Provides local and global SHAP Shapley value decomposition and graph topological evidence.
"""

from src.explainability.claim_explainer import ClaimExplainer, explain_claim
from src.explainability.graph_explainer import GraphExplainer
from src.explainability.shap_explainer import ShapExplainer

__all__ = [
    "ShapExplainer",
    "GraphExplainer",
    "ClaimExplainer",
    "explain_claim",
]
