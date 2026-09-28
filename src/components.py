"""
Reusable UI components, safe rendering helpers, and Streamlit version adapters
for the UAC Analytics platform.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_plotly_chart(fig: go.Figure, **kwargs: Any) -> None:
    """Render Plotly figure with forward and backward Streamlit version compatibility.

    Silently adapts between modern `width='stretch'` and legacy `use_container_width=True`
    to prevent terminal deprecation warnings.
    """
    try:
        st.plotly_chart(fig, width="stretch", **kwargs)
    except (TypeError, ValueError):
        st.plotly_chart(fig, use_container_width=True, **kwargs)


def render_dataframe(data: pd.DataFrame, **kwargs: Any) -> None:
    """Render DataFrame with forward and backward Streamlit version compatibility.

    Silently adapts between modern `width='stretch'` and legacy `use_container_width=True`.
    """
    try:
        st.dataframe(data, width="stretch", **kwargs)
    except (TypeError, ValueError):
        st.dataframe(data, use_container_width=True, **kwargs)


def safe_int(val: Any, default: int = 0) -> int:
    """Convert value safely to int, protecting against NaN, None, inf, and strings."""
    if val is None:
        return default
    try:
        if pd.isna(val):
            return default
        return int(float(val))
    except (ValueError, TypeError, OverflowError):
        return default


def build_status_ribbon_html(
    status_badge: str,
    status_color: str,
    status_bg: str,
    status_desc: str,
    latest_load: int,
    peak_load: int,
    peak_date: str,
    pct_of_peak: float,
) -> str:
    """Construct HTML markup for the operational status banner."""
    return f"""
<div style="
    background:{status_bg};
    border-left:5px solid {status_color};
    border-radius:10px;
    padding:16px 20px;
    margin:18px 0 24px 0;
    box-shadow:0 2px 8px rgba(0,0,0,0.03);
">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <span style="
          background:{status_color};
          color:#ffffff;
          padding:3px 10px;
          border-radius:999px;
          font-size:10px;
          font-weight:700;
          letter-spacing:0.06em;
          text-transform:uppercase;
      ">{status_badge}</span>
      <div style="margin-top:6px;font-size:13px;color:#1e293b;line-height:1.5">
        {status_desc}
      </div>
    </div>
    <div style="text-align:right">
      <div style="font-size:10.5px;color:#64748b;text-transform:uppercase;letter-spacing:0.04em">Capacity Context</div>
      <div style="font-size:13px;font-weight:700;color:#0b2545;margin-top:2px">
        {latest_load:,} / {peak_load:,} peak ({pct_of_peak:.1f}%)
      </div>
      <div style="font-size:10.5px;color:#94a3b8">Peak reached on {peak_date}</div>
    </div>
  </div>
</div>
"""
