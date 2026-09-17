"""
dashboard/components/header.py
------------------------------
Standardized Enterprise Header Component.
"""

from __future__ import annotations

from typing import Optional
import streamlit as st


def render_header(
    title: str,
    subtitle: Optional[str] = None,
    tag: str = "FRAUD INTELLIGENCE PLATFORM",
    badge_text: Optional[str] = None,
    badge_variant: Optional[str] = None,
    status_variant: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Renders a unified SaaS enterprise header across all dashboard views.
    """
    variant = badge_variant or status_variant or "success"
    badge_content = badge_text if badge_text else "LIVE DATA"
    badge_html = f'<div class="saas-header-badge {variant}">● {badge_content}</div>'

    subtitle_html = (
        f'<div class="saas-header-subtitle">{subtitle}</div>'
        if subtitle
        else ""
    )

    header_html = (
        f'<div class="saas-header">'
        f'<div class="saas-header-text">'
        f'<div class="saas-header-tag">{tag}</div>'
        f'<h1 class="saas-header-title">{title}</h1>'
        f'{subtitle_html}'
        f'</div>'
        f'<div>{badge_html}</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)
