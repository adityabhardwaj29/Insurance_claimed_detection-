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


def render_sidebar_officer_session() -> None:
    """
    Renders an authenticated officer status widget in the Streamlit sidebar.
    """
    if "officer_name" not in st.session_state:
        st.session_state.officer_name = "Rahul Varma, CFE"
        st.session_state.officer_role = "Senior SIU Investigator"
        st.session_state.officer_badge = "SIU-INV-709"
        st.session_state.officer_dept = "Special Investigation Unit"

    st.sidebar.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F3B82 0%, #1A4C9C 100%); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px; margin-bottom: 15px; color: white;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; color: #93C5FD; font-weight: 700;">🛡️ Active Officer Session</span>
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 6px #10B981;" title="Officer Session Online"></span>
            </div>
            <div style="font-size: 0.88rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">
                {st.session_state.officer_name}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
                <span style="font-size: 0.72rem; color: #BFDBFE;">{st.session_state.officer_role}</span>
                <span style="font-family: monospace; font-size: 0.70rem; background: rgba(0,0,0,0.25); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2);">{st.session_state.officer_badge}</span>
            </div>
            <div style="font-size: 0.68rem; color: #93C5FD; margin-top: 3px;">
                🏢 {st.session_state.officer_dept}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

