"""
dashboard/components/empty_states.py
------------------------------------
Standardized empty states for empty tables, queues, or search misses.
"""

from __future__ import annotations

from typing import Optional
import streamlit as st


def render_empty_state(
    title: str = "No Records Found",
    description: str = "No claims or events match your current filter criteria.",
    icon: str = "🔍",
) -> None:
    """
    Renders an elegant empty state placeholder.
    """
    html = f"""
    <div class="saas-empty-state">
        <div class="saas-empty-icon">{icon}</div>
        <div class="saas-empty-title">{title}</div>
        <div class="saas-empty-desc">{description}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
