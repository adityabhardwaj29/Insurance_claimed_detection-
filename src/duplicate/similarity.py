"""
src/duplicate/similarity.py
---------------------------
Deterministic, reproducible similarity functions for multi-field claim comparison.

Provides:
  - numeric_similarity: Proportional/bounded difference in [0.0, 1.0]
  - date_similarity: Proximity decay over elapsed days in [0.0, 1.0]
  - categorical_similarity: Exact match indicator for categorical fields
  - jaccard_similarity: Set-based token/element overlap
  - composite_similarity: Weighted combination of component similarities
"""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Mapping


def numeric_similarity(a: float | int | None, b: float | int | None, scale: float = 1.0) -> float:
    """
    Computes normalized numeric similarity in [0.0, 1.0].

    Formula:
        max(0.0, 1.0 - abs(a - b) / max(abs(a), abs(b), scale, 1e-9))

    If both values are identical, returns 1.0.
    If either value is None / NaN, returns 0.0.
    """
    if a is None or b is None:
        return 0.0
    try:
        fa, fb = float(a), float(b)
    except (ValueError, TypeError):
        return 0.0
    if math.isnan(fa) or math.isnan(fb):
        return 0.0
    if fa == fb:
        return 1.0
    denom = max(abs(fa), abs(fb), abs(scale), 1e-9)
    diff = abs(fa - fb)
    return max(0.0, 1.0 - diff / denom)


def date_similarity(
    date_a: str | date | datetime | None,
    date_b: str | date | datetime | None,
    max_days: int = 60,
) -> tuple[float, int]:
    """
    Computes date proximity similarity in [0.0, 1.0] and the absolute difference in days.

    Returns:
        (similarity_score, days_diff)
        - 1.0 if identical day (0 days diff).
        - Linear decay to 0.0 at max_days difference.
        - 0.0 if days_diff > max_days or if dates cannot be parsed.
    """
    if date_a is None or date_b is None:
        return (0.0, 9999)

    def _parse(val: Any) -> datetime | None:
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime(val.year, val.month, val.day)
        try:
            # Supports ISO YYYY-MM-DD
            s = str(val).strip()[:10]
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None

    dt_a = _parse(date_a)
    dt_b = _parse(date_b)
    if dt_a is None or dt_b is None:
        return (0.0, 9999)

    days_diff = abs((dt_a - dt_b).days)
    if days_diff == 0:
        return (1.0, 0)
    sim = max(0.0, 1.0 - (days_diff / float(max_days)))
    return (round(sim, 4), days_diff)


def categorical_similarity(val_a: Any, val_b: Any) -> float:
    """
    Exact equality for categorical fields.
    Returns 1.0 if both non-null and equal (case-insensitive string match if strings),
    0.0 otherwise.
    """
    if val_a is None or val_b is None:
        return 0.0
    sa = str(val_a).strip()
    sb = str(val_b).strip()
    if not sa or not sb or sa.lower() == "nan" or sb.lower() == "nan":
        return 0.0
    return 1.0 if sa.lower() == sb.lower() else 0.0


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Standard Jaccard similarity: |A ∩ B| / |A ∪ B|.
    Returns 1.0 if both empty, 0.0 if one empty.
    """
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return float(intersection / union) if union > 0 else 0.0


def composite_similarity(
    components: Mapping[str, float],
    weights: Mapping[str, float],
) -> float:
    """
    Computes weighted sum of component scores.
    Weights are normalized so they sum to 1.0.
    """
    if not components or not weights:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0
    for key, weight in weights.items():
        if key in components:
            score = max(0.0, min(1.0, float(components[key])))
            weighted_sum += score * weight
            total_weight += weight

    if total_weight <= 0:
        return 0.0
    return round(weighted_sum / total_weight, 4)
