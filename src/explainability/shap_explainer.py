"""
src/explainability/shap_explainer.py
-----------------------------------
Supervised model explainability using SHAP (SHapley Additive exPlanations).
Computes exact local Shapley values using TreeExplainer on the trained XGBoost pipeline,
categorizing features into risk_increasing and risk_decreasing factors.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_PATH = ROOT / "models" / "fraud_model" / "model.joblib"
DEFAULT_FEATURES_PATH = ROOT / "data" / "features" / "final_claim_features.csv"

# Pretty name mapping for human-readable reports
FEATURE_NAME_MAP = {
    "claim_amount": "Claim Amount ($)",
    "claim_age_days": "Claim Age (Days)",
    "days_since_policy_start": "Days Since Policy Inception",
    "amount_to_premium_ratio": "Claim Amount to Annual Premium Ratio",
    "invoice_to_claim_ratio": "Invoice to Claim Amount Ratio",
    "claimant_claim_frequency": "Claimant Prior Claim Frequency",
    "provider_claim_volume": "Provider Total Claim Volume",
    "vehicle_age": "Vehicle Age (Years)",
    "claimant_age": "Claimant Age (Years)",
    "provider_rating": "Provider Quality Rating (1-5)",
    "duplicate_similarity_score": "Pairwise Duplicate Similarity Score",
    "duplicate_flag": "Duplicate / Resubmission Flag",
    "claim_type": "Claim Incident Type",
    "policy_type": "Insurance Policy Type",
    "vehicle_type": "Vehicle Classification",
    "vehicle_make": "Vehicle Manufacturer",
    "provider_type": "Service Provider Category",
    "claimant_city": "Claimant City / Territory",
}


def _format_feature_label(raw_feature: str, raw_value: Any = None) -> str:
    """Formats raw column names or one-hot encoded dummy names into clean human-readable text."""
    clean_name = raw_feature
    if clean_name.startswith("num__"):
        col = clean_name.replace("num__", "")
        pretty = FEATURE_NAME_MAP.get(col, col.replace("_", " ").title())
        if raw_value is not None and not (isinstance(raw_value, float) and np.isnan(raw_value)):
            if "amount" in col or "premium" in col:
                return f"{pretty} (${raw_value:,.2f})"
            elif "ratio" in col or "score" in col or "rating" in col:
                return f"{pretty} ({raw_value:.2f})"
            else:
                return f"{pretty} ({raw_value})"
        return pretty
    elif clean_name.startswith("cat__"):
        clean = clean_name.replace("cat__", "")
        cat_cols = ["claim_type", "policy_type", "vehicle_type", "vehicle_make", "provider_type", "claimant_city"]
        for c in sorted(cat_cols, key=len, reverse=True):
            if clean.startswith(f"{c}_"):
                cat_val = clean[len(c) + 1:]
                pretty_col = FEATURE_NAME_MAP.get(c, c.replace("_", " ").title())
                return f"{pretty_col}: {cat_val}"
        return clean.replace("_", " ").title()
    return FEATURE_NAME_MAP.get(clean_name, clean_name.replace("_", " ").title())


class ShapExplainer:
    """
    SHAP-based local and global explainer for the supervised fraud detection model.
    """

    def __init__(self, model_path: Optional[str | Path] = None):
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self.pipeline = joblib.load(self.model_path)
        self.preprocessor = self.pipeline.named_steps["preprocessor"]
        self.classifier = self.pipeline.named_steps["classifier"]
        self.feature_names_in = list(self.pipeline.feature_names_in_)
        self.transformed_names = list(self.preprocessor.get_feature_names_out())

        # Initialize TreeExplainer on preprocessed features
        self.explainer = shap.TreeExplainer(self.classifier)

    def explain_instance(
        self,
        claim_features: pd.Series | Dict[str, Any],
        top_k: int = 5,
        claim_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Computes SHAP explanations for a single claim record.
        Returns top risk-increasing and top risk-decreasing factors.
        """
        # Convert to DataFrame
        if isinstance(claim_features, dict):
            row_df = pd.DataFrame([claim_features])
        else:
            row_df = pd.DataFrame([claim_features.to_dict()])

        cid = claim_id or str(row_df.get("claim_id", ["UNKNOWN"]).iloc[0] if "claim_id" in row_df.columns else "UNKNOWN")

        # Subset to expected feature columns
        available_cols = [c for c in self.feature_names_in if c in row_df.columns]
        X = row_df[available_cols].copy()

        # Fill missing features with default NaN so preprocessor imputer handles them
        for col in self.feature_names_in:
            if col not in X.columns:
                X[col] = np.nan
        X = X[self.feature_names_in]

        # Compute probability
        if hasattr(self.pipeline, "predict_proba"):
            probs = self.pipeline.predict_proba(X)[0]
            fraud_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            fraud_prob = 0.5

        # Transform features
        X_trans = self.preprocessor.transform(X)

        # Compute Shapley values
        shap_explanation = self.explainer(X_trans)
        shap_vals = np.array(shap_explanation.values)[0]

        # Assemble individual factor contributions
        all_factors: List[Dict[str, Any]] = []
        for i, (fname, s_val) in enumerate(zip(self.transformed_names, shap_vals)):
            # Find raw value if available
            raw_val = None
            if fname.startswith("num__"):
                orig_col = fname.replace("num__", "")
                raw_val = X[orig_col].iloc[0] if orig_col in X.columns else None

            pretty_name = _format_feature_label(fname, raw_val)
            impact = float(round(s_val, 4))
            direction = "risk_increasing" if impact > 0 else "risk_decreasing"

            all_factors.append({
                "feature": pretty_name,
                "raw_feature": fname,
                "impact": impact,
                "abs_impact": abs(impact),
                "direction": direction,
            })

        # Sort factors by absolute impact
        all_factors.sort(key=lambda x: x["abs_impact"], reverse=True)

        # Partition into positive and negative
        positive_factors = [f for f in all_factors if f["direction"] == "risk_increasing"]
        negative_factors = [f for f in all_factors if f["direction"] == "risk_decreasing"]

        # Top overall factors
        top_factors = [
            {
                "feature": f["feature"],
                "impact": f["impact"],
                "direction": f["direction"],
            }
            for f in all_factors[:top_k]
        ]

        top_positive = [
            {
                "feature": f["feature"],
                "impact": f["impact"],
                "direction": f["direction"],
            }
            for f in positive_factors[:top_k]
        ]

        top_negative = [
            {
                "feature": f["feature"],
                "impact": f["impact"],
                "direction": f["direction"],
            }
            for f in negative_factors[:top_k]
        ]

        return {
            "claim_id": cid,
            "fraud_probability": round(fraud_prob, 4),
            "base_value": float(round(shap_explanation.base_values[0], 4)) if hasattr(shap_explanation, "base_values") else 0.0,
            "top_factors": top_factors,
            "top_positive_factors": top_positive,
            "top_negative_factors": top_negative,
            "all_factors_count": len(all_factors),
        }

    def explain_dataset(self, df: pd.DataFrame, top_k: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Batch-explains an entire DataFrame of claims.
        Returns a dictionary mapping claim_id -> explanation dictionary.
        """
        results = {}
        for _, row in df.iterrows():
            cid = str(row.get("claim_id", f"CLM_{_}"))
            exp = self.explain_instance(row, top_k=top_k, claim_id=cid)
            results[cid] = exp
        return results
