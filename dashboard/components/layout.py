"""
dashboard/components/layout.py
------------------------------
Page layout helpers and CSS theme injector.
"""

from __future__ import annotations

import logging
from pathlib import Path
import streamlit as st

logger = logging.getLogger(__name__)

THEME_CSS_PATH = Path(__file__).resolve().parent.parent / "styles" / "theme.css"


def inject_theme() -> None:
    """
    Injects the centralized enterprise CSS design tokens and component styling
    into the active Streamlit session.
    """
    if THEME_CSS_PATH.exists():
        try:
            css_content = THEME_CSS_PATH.read_text(encoding="utf-8")
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.warning("Failed to inject theme.css: %s", e)
    else:
        logger.warning("theme.css not found at %s", THEME_CSS_PATH)
