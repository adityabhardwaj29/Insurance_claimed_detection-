"""
src/scoring/priority.py
-----------------------
Maps numeric fraud risk scores to operational risk bands.
"""

from __future__ import annotations

from typing import Optional
from src.scoring.thresholds import DEFAULT_RISK_BANDS, RiskBands


def priority(score: float, bands: Optional[RiskBands] = None) -> str:
    """
    Classifies a composite risk score into an operational risk band:
    CRITICAL, HIGH, MEDIUM, or LOW.

    Parameters
    ----------
    score : float
        Composite risk score in [0, 1].
    bands : RiskBands, optional
        Configurable threshold bands. Defaults to DEFAULT_RISK_BANDS.

    Returns
    -------
    str
        One of 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'.
    """
    b = bands or DEFAULT_RISK_BANDS
    return b.classify(score)
