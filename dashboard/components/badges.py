"""
dashboard/components/badges.py
------------------------------
Standardized semantic badges for risk bands, case statuses, and alerts.
"""

from __future__ import annotations


def risk_badge(band: str) -> str:
    """
    Returns an HTML string for a colored risk band badge.
    """
    b = str(band).upper().strip() if band else "LOW"
    css_class = b.lower()
    return f'<span class="saas-badge {css_class}">● {b}</span>'


def status_badge(status: str) -> str:
    """
    Returns an HTML string for a case or claim status badge.
    """
    s = str(status).upper().strip() if status else "UNKNOWN"
    mapping = {
        "NEW": "info",
        "UNDER_REVIEW": "high",
        "ESCALATED": "critical",
        "RESOLVED": "low",
        "FALSE_POSITIVE": "neutral",
        "OPEN": "info",
        "APPROVED": "low",
        "REJECTED": "critical",
    }
    css_class = mapping.get(s, "neutral")
    return f'<span class="saas-badge {css_class}">{s}</span>'
