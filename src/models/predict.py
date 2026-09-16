"""
src/models/predict.py
---------------------
Model inference module for insurance claim fraud detection.

Outputs:
  - fraud_probability (calibrated continuous probability in [0.0, 1.0])
  - binary predicted label based on customizable threshold (default 0.5)

Note: As per project rules, fraud_probability is NOT converted into a final risk score here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models" / "fraud_model"


def load_model(model_dir: str | Path | None = None) -> tuple[Any, dict[str, Any]]:
    """
    Loads the persisted model artifact and its metadata.
    """
    m_dir = Path(model_dir or DEFAULT_MODEL_DIR)
    model_file = m_dir / "model.joblib"
    meta_file = m_dir / "metadata.json"

    if not model_file.exists():
        raise FileNotFoundError(
            f"Trained model not found at {model_file}. Run `python -m src.models.train` first."
        )

    model = joblib.load(model_file)
    metadata = {}
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return model, metadata


def predict_probability(model: Any, X: pd.DataFrame | np.ndarray) -> np.ndarray:
    """
    Generates fraud probability in [0.0, 1.0] for each claim.
    """
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[:, 1]
    elif hasattr(model, "decision_function"):
        df_vals = model.decision_function(X)
        probs = 1.0 / (1.0 + np.exp(-df_vals))
    else:
        probs = model.predict(X).astype(float)
    return np.clip(probs, 0.0, 1.0)


def predict(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    threshold: float = 0.5,
) -> np.ndarray:
    """
    Generates binary classification (0 = legitimate, 1 = fraudulent) based on threshold.
    """
    probs = predict_probability(model, X)
    return (probs >= threshold).astype(int)


def score_claims_dataframe(
    model: Any,
    df: pd.DataFrame,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """
    Attaches `fraud_probability` and `predicted_label` to the input DataFrame.
    """
    out = df.copy()
    probs = predict_probability(model, out)
    out["fraud_probability"] = np.round(probs, 4)
    out["predicted_fraud"] = (probs >= threshold).astype(int)
    return out
