"""
dashboard/components/charts.py
------------------------------
Standardized Plotly theme applicator for enterprise SaaS consistency.
"""

from __future__ import annotations

from typing import Optional
import plotly.graph_objects as go


def apply_chart_theme(
    fig: go.Figure,
    height: int = 400,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Applies the centralized enterprise dark SaaS styling to any Plotly chart.
    """
    layout_update = dict(
        font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#94a3b8"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        height=height,
        margin=dict(l=40, r=20, t=50 if title else 20, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#f8fafc", size=11),
        ),
        xaxis=dict(
            gridcolor="#1e293b",
            zerolinecolor="#1e293b",
            tickfont=dict(color="#64748b", size=11),
            title_font=dict(color="#94a3b8", size=12),
        ),
        yaxis=dict(
            gridcolor="#1e293b",
            zerolinecolor="#1e293b",
            tickfont=dict(color="#64748b", size=11),
            title_font=dict(color="#94a3b8", size=12),
        ),
    )

    if title:
        layout_update["title"] = dict(
            text=title,
            font=dict(size=14, color="#f8fafc", family="Inter, sans-serif"),
            x=0.0,
            xanchor="left",
        )

    fig.update_layout(**layout_update)
    return fig
