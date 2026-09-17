"""
dashboard/components/loading.py
-------------------------------
Loading and progress indicator components.
"""

from __future__ import annotations

import streamlit as st


def render_loading_state(message: str = "Analyzing claim patterns...") -> None:
    """
    Renders a clean spinner placeholder for long-running graph or ML tasks.
    """
    st.info(f"⏳ {message}")
