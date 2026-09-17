"""
dashboard/components/cards.py
-----------------------------
Reusable card containers and risk gauge widgets.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Optional
import streamlit as st
from dashboard.components.badges import risk_badge


@contextmanager
def card_container(title: str, subtitle: Optional[str] = None, icon: str = "📌"):
    """
    Context manager that renders an enterprise card container with header.
    Can be used as:
        with card_container("Title"):
            st.write(...)
    """
    sub_html = f'<div class="saas-card-subtitle">{subtitle}</div>' if subtitle else ""
    html = (
        f'<div class="saas-card-header">'
        f'<div><h3 class="saas-card-title">{icon} {title}</h3>{sub_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    with st.container():
        yield


def risk_gauge_card(
    score: float,
    band: str,
    fraud_prob: float,
    anomaly_score: float,
    duplicate_score: float,
    graph_risk: float,
) -> None:
    """
    Renders a unified risk summary block with composite score and 4 sub-signals.
    """
    badge_html = risk_badge(band)
    pct = int(round(score * 100))

    html = (
        f'<div class="saas-card" style="border-left: 4px solid var(--risk-{band.lower()});">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
        f'<span style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);">'
        f'Hybrid Fraud Risk Assessment</span>'
        f'{badge_html}</div>'
        f'<div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 16px;">'
        f'<span style="font-size: 2.75rem; font-weight: 800; color: var(--text-white); line-height: 1;">{score:.4f}</span>'
        f'<span style="font-size: 1.1rem; color: var(--text-muted); font-weight: 600;">/ 1.000 ({pct}%)</span></div>'
        f'<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; padding-top: 12px; border-top: 1px solid var(--border-subtle);">'
        f'<div><div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Supervised ML</div><div style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">{fraud_prob:.3f}</div></div>'
        f'<div><div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Anomaly Score</div><div style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">{anomaly_score:.3f}</div></div>'
        f'<div><div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Duplicate Sim</div><div style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">{duplicate_score:.3f}</div></div>'
        f'<div><div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Graph Risk</div><div style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">{graph_risk:.3f}</div></div>'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
