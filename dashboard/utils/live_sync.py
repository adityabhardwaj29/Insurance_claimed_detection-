"""
dashboard/utils/live_sync.py
----------------------------
Real-time live sync controller connecting the Streamlit Research & Analytics
Console with the active FastAPI Backend (Port 8000) and SQLite Database.
Enables automatic periodic background polling and instant cache purging.
"""

from __future__ import annotations

import logging
import urllib.request
from typing import Optional

import streamlit as st
from streamlit_autorefresh import st_autorefresh

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3)
def check_api_online(endpoint: str = "http://localhost:8000/api/health") -> bool:
    """Probes FastAPI health endpoint with a short timeout."""
    try:
        req = urllib.request.Request(endpoint, headers={"User-Agent": "Streamlit-Sync-Agent"})
        with urllib.request.urlopen(req, timeout=0.8) as res:
            return res.status == 200
    except Exception:
        return False


def render_live_sync_controller(total_records: Optional[int] = None) -> None:
    """
    Renders the Real-Time Live Sync & Data Synchronization widget
    in the Streamlit sidebar.
    """
    st.sidebar.markdown(
        """
        <div style="background: #13469A; border: 1px solid #1E5AB8; border-left: 4px solid #60A5FA; 
                    padding: 10px 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.15);">
            <div style="font-size: 0.86rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 6px;">
                <span>⚡ Real-Time Live Sync</span>
            </div>
            <div style="font-size: 0.74rem; color: #BFDBFE; margin-top: 2px;">
                Direct SQLite & FastAPI Data Engine
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    api_online = check_api_online()
    if api_online:
        st.sidebar.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; border-radius: 6px; padding: 6px 10px; margin-bottom: 10px;">
                <span style="font-size: 0.78rem; font-weight: 600; color: #4ADE80;">🟢 FastAPI API: Online (8000)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            """
            <div style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3B82F6; border-radius: 6px; padding: 6px 10px; margin-bottom: 10px;">
                <span style="font-size: 0.78rem; font-weight: 600; color: #93C5FD;">🔵 SQLite Direct: Connected</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.sidebar.columns([3, 2])
    with col1:
        auto_sync = st.toggle("Live Sync", value=True, help="Automatically refreshes dashboard when new claims are filed in React app")
    with col2:
        if st.button("🔄 Sync", help="Clear cache and re-fetch latest database records", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if auto_sync:
        interval_choice = st.sidebar.select_slider(
            "Sync Interval",
            options=[3, 5, 10, 30],
            value=5,
            format_func=lambda s: f"{s} sec",
            help="Polling frequency for live claim detection updates"
        )
        st_autorefresh(interval=interval_choice * 1000, key="global_live_data_autorefresh")
        st.sidebar.caption(f"⏱️ Auto-refreshing every **{interval_choice}s**")
    else:
        st.sidebar.caption("⏸️ Auto-refresh paused (manual sync only)")

    if total_records is not None:
        st.sidebar.markdown(
            f"<div style='font-size: 0.76rem; color: #64748B; margin-top: 4px; margin-bottom: 10px;'>"
            f"📊 <strong>Active Database Claims:</strong> <span style='color: #0F172A; font-weight: 700;'>{total_records}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)
