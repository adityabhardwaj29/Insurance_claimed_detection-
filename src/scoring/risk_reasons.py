"""
src/scoring/risk_reasons.py
----------------------------
Evidence-based risk reason generation for the Hybrid Fraud Risk Engine.

PRINCIPLES
----------
1. Every reason must be derivable from actual data values in the claim record.
2. No reason is generated unless the corresponding feature value crosses a
   documented, data-derived threshold (defined in thresholds.py).
3. Reasons are plain English operational labels — NOT legal accusations.
4. The function returns an empty list if no threshold is crossed (valid state).
5. Reason codes are stable identifiers for downstream systems.

REASON CODES AND TRIGGERS
--------------------------
Each reason has:
  - A stable code (e.g. "HIGH_FRAUD_PROBABILITY")
  - A human-readable message
  - The triggering condition (which feature, which threshold)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.scoring.thresholds import ReasonThresholds, DEFAULT_REASON_THRESHOLDS


# Each entry: (reason_code, human_readable_message, triggering_description)
REASON_CATALOG: Dict[str, str] = {
    "HIGH_FRAUD_PROBABILITY": "Supervised model assigns high fraud probability to this claim",
    "HIGH_ANOMALY_SCORE": "Claim exhibits anomalous feature patterns (Isolation Forest + LOF ensemble)",
    "ANOMALY_FLAGGED": "Claim is flagged as a statistical outlier by the anomaly detection system",
    "HIGH_DUPLICATE_SIMILARITY": "Claim has high similarity to another claim in the dataset",
    "POSSIBLE_DUPLICATE_CLAIM": "Claim is categorized as a possible duplicate based on shared entities",
    "HIGH_CLAIM_AMOUNT": "Claim amount exceeds the 90th percentile of the dataset (outlier amount)",
    "HIGH_AMOUNT_TO_PREMIUM_RATIO": "Claim amount is unusually high relative to the policy premium",
    "HIGH_CLAIMANT_DEGREE": "Claimant is connected to an above-average number of entities in the network",
    "HIGH_PROVIDER_VOLUME": "Provider handles an above-median number of claims (high-volume provider)",
    "HIGH_PROVIDER_VOLUME_TABULAR": "Provider has high claim submission volume in the records",
    "FRAUD_NEIGHBOR_PRESENT": "Claimant has filed other claims that were labelled fraudulent",
    "HIGH_FRAUD_NEIGHBOR_RATIO": "Majority of claimant's sibling claims have fraud labels",
    "REPEATED_CLAIMANT_PROVIDER": "Claimant has filed multiple claims with the same provider",
    "SUSPICIOUS_PROVIDER_CONNECTIONS": "Claimant's claim history involves high-volume (suspicious) providers",
    "HIGH_CLAIM_FREQUENCY": "Claimant has filed an above-average number of claims",
}


def generate_reasons(
    row: Dict[str, Any],
    thresholds: ReasonThresholds = DEFAULT_REASON_THRESHOLDS,
) -> List[str]:
    """
    Generates a list of evidence-based risk reason codes for a single claim.
    Only reasons that are supported by actual feature values are returned.

    Parameters
    ----------
    row : dict
        A single claim's feature values. Expected keys correspond to columns
        in final_claim_features.csv and final_risk_scores.csv.
    thresholds : ReasonThresholds
        Configurable threshold configuration. Defaults to data-derived values.

    Returns
    -------
    List[str] of reason codes (from REASON_CATALOG) that apply to this claim.
    """
    reasons: List[str] = []

    # --- Component 1: Supervised fraud probability ---
    fraud_prob = _safe_float(row.get("fraud_probability"))
    if fraud_prob is not None and fraud_prob >= thresholds.HIGH_FRAUD_PROB:
        reasons.append("HIGH_FRAUD_PROBABILITY")

    # --- Component 2: Anomaly detection ---
    anomaly_score = _safe_float(row.get("anomaly_score"))
    if anomaly_score is not None and anomaly_score >= thresholds.HIGH_ANOMALY:
        reasons.append("HIGH_ANOMALY_SCORE")

    anomaly_flag = _safe_int(row.get("anomaly_flag"))
    if anomaly_flag == 1:
        reasons.append("ANOMALY_FLAGGED")

    # --- Component 3: Duplicate detection ---
    dup_score = _safe_float(row.get("dup_similarity_score"))
    if dup_score is None:
        dup_score = _safe_float(row.get("duplicate_similarity_score"))
    if dup_score is not None and dup_score >= thresholds.HIGH_DUPLICATE_SIMILARITY:
        reasons.append("HIGH_DUPLICATE_SIMILARITY")

    dup_type = str(row.get("dup_type", row.get("duplicate_type", ""))).upper()
    if "POSSIBLE_DUPLICATE" in dup_type:
        reasons.append("POSSIBLE_DUPLICATE_CLAIM")

    # --- Component 4: Claim amount outlier ---
    claim_amount = _safe_float(row.get("claim_amount"))
    if claim_amount is not None and claim_amount >= thresholds.HIGH_CLAIM_AMOUNT:
        reasons.append("HIGH_CLAIM_AMOUNT")

    # --- Component 5: Amount-to-premium ratio ---
    apr = _safe_float(row.get("amount_to_premium_ratio"))
    if apr is not None and apr >= thresholds.HIGH_AMOUNT_PREMIUM_RATIO:
        reasons.append("HIGH_AMOUNT_TO_PREMIUM_RATIO")

    # --- Component 6: Graph network signals ---
    claimant_degree = _safe_int(row.get("claimant_degree"))
    if claimant_degree is not None and claimant_degree >= thresholds.HIGH_CLAIMANT_DEGREE:
        reasons.append("HIGH_CLAIMANT_DEGREE")

    provider_claim_count = _safe_int(row.get("provider_claim_count"))
    if provider_claim_count is not None and provider_claim_count > thresholds.HIGH_PROVIDER_VOLUME:
        reasons.append("HIGH_PROVIDER_VOLUME")

    provider_claim_volume = _safe_int(row.get("provider_claim_volume"))
    if provider_claim_volume is not None and provider_claim_volume > thresholds.HIGH_PROVIDER_VOLUME_TABULAR:
        reasons.append("HIGH_PROVIDER_VOLUME_TABULAR")

    fraud_nb_count = _safe_int(row.get("fraud_neighbor_count"))
    if fraud_nb_count is not None and fraud_nb_count > thresholds.NONZERO_FRAUD_NEIGHBOR_RATIO:
        reasons.append("FRAUD_NEIGHBOR_PRESENT")

    fraud_nb_ratio = _safe_float(row.get("fraud_neighbor_ratio"))
    if fraud_nb_ratio is not None and fraud_nb_ratio > 0.5:
        reasons.append("HIGH_FRAUD_NEIGHBOR_RATIO")

    repeated = _safe_int(row.get("repeated_claimant_provider"))
    if repeated == 1:
        reasons.append("REPEATED_CLAIMANT_PROVIDER")

    suspicious_count = _safe_int(row.get("suspicious_neighbor_count"))
    if suspicious_count is not None and suspicious_count >= thresholds.SUSPICIOUS_NEIGHBOR_MIN:
        reasons.append("SUSPICIOUS_PROVIDER_CONNECTIONS")

    claimant_freq = _safe_int(row.get("claimant_claim_frequency"))
    if claimant_freq is None:
        # Fall back to claimant_claim_count from graph features
        claimant_freq = _safe_int(row.get("claimant_claim_count"))
    if claimant_freq is not None and claimant_freq > thresholds.HIGH_CLAIM_FREQUENCY:
        reasons.append("HIGH_CLAIM_FREQUENCY")

    # Deduplicate while preserving order
    seen = set()
    unique_reasons = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    return unique_reasons


def reasons_to_messages(reason_codes: List[str]) -> List[str]:
    """Converts reason codes to human-readable messages from the catalog."""
    return [REASON_CATALOG.get(code, code) for code in reason_codes]


def reasons_to_string(reason_codes: List[str], separator: str = " | ") -> str:
    """Converts reason codes to a pipe-separated string for CSV storage."""
    if not reason_codes:
        return ""
    return separator.join(reasons_to_messages(reason_codes))


def _safe_float(val: Any) -> float | None:
    """Safely converts a value to float, returning None on failure."""
    if val is None:
        return None
    try:
        f = float(val)
        import math
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def _safe_int(val: Any) -> int | None:
    """Safely converts a value to int, returning None on failure."""
    f = _safe_float(val)
    return None if f is None else int(round(f))
