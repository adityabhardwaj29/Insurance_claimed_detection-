"""
dashboard/components/metrics.py
-------------------------------
Standardized SaaS KPI Metric Cards.
"""

from __future__ import annotations

from typing import Optional
import streamlit as st


def render_kpi_card(
    label: Optional[str] = None,
    value: str | int | float = "",
    subtitle: Optional[str] = None,
    icon: str = "📊",
    variant: str = "default",  # "default", "critical", "high", "medium", "low", "primary", "info", "success"
    title: Optional[str] = None,
    accent_color: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Renders an enterprise styled KPI card with colored accent bar and typography tokens.
    Supports either `title` or `label`, and optional custom `accent_color`.
    """
    display_label = title if title is not None else (label if label is not None else "")
    variant_class = variant.lower() if variant else "default"

    accent_attr = ""
    if accent_color:
        accent_attr = f'style="border-left: 4px solid {accent_color} !important;"'

    subtitle_html = (
        f'<div class="saas-kpi-footer">{subtitle}</div>'
        if subtitle
        else ""
    )

    card_html = (
        f'<div class="saas-kpi-card {variant_class}" {accent_attr}>'
        f'<div class="saas-kpi-header">'
        f'<span class="saas-kpi-label">{display_label}</span>'
        f'<span class="saas-kpi-icon">{icon}</span>'
        f'</div>'
        f'<div class="saas-kpi-value">{value}</div>'
        f'{subtitle_html}'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
