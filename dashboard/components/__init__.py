"""
dashboard/components/__init__.py
--------------------------------
Reusable Enterprise UI/UX Component Library for the Fraud Analytics Platform.
"""

from dashboard.components.layout import inject_theme
from dashboard.components.header import render_header
from dashboard.components.metrics import render_kpi_card
from dashboard.components.badges import risk_badge, status_badge
from dashboard.components.cards import card_container, risk_gauge_card
from dashboard.components.charts import apply_chart_theme
from dashboard.components.empty_states import render_empty_state
from dashboard.components.loading import render_loading_state

__all__ = [
    "inject_theme",
    "render_header",
    "render_kpi_card",
    "risk_badge",
    "status_badge",
    "card_container",
    "risk_gauge_card",
    "apply_chart_theme",
    "render_empty_state",
    "render_loading_state",
]
