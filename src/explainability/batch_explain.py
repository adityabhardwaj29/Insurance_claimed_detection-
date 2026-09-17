"""
src/explainability/batch_explain.py
----------------------------------
Batch computation script for Phase 12 Explainable Fraud Detection.
Precomputes and persists unified SHAP and Graph explanations for all 320 claims
to data/features/claim_explanations.json for fast API and Dashboard lookups.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from src.explainability.claim_explainer import ClaimExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
FEATURES_CSV = ROOT / "data" / "features" / "final_claim_features.csv"
OUTPUT_JSON = ROOT / "data" / "features" / "claim_explanations.json"


def precompute_all_explanations(
    features_path: Path = FEATURES_CSV,
    output_path: Path = OUTPUT_JSON,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Precomputes explanations for all claims in the dataset and serializes to JSON.
    """
    if not features_path.exists():
        raise FileNotFoundError(f"Features file not found at {features_path}")

    df = pd.read_csv(features_path, keep_default_na=False)
    logger.info("Loaded %d claims from %s for batch explainability", len(df), features_path)

    explainer = ClaimExplainer(features_path=features_path)

    explanations: Dict[str, Any] = {}
    claim_ids = df["claim_id"].tolist()

    for idx, cid in enumerate(claim_ids, 1):
        exp = explainer.explain_claim(cid, top_k=top_k)
        explanations[cid] = exp
        if idx % 50 == 0 or idx == len(claim_ids):
            logger.info("Processed %d / %d claim explanations", idx, len(claim_ids))

    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(explanations, f, indent=2)

    logger.info("Saved %d precomputed explanations to %s", len(explanations), output_path)
    return explanations


if __name__ == "__main__":
    precompute_all_explanations()
