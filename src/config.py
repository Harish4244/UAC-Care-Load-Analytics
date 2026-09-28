"""
Configuration, design tokens, color palette, and column mappings
for the UAC Analytics platform.
"""

from __future__ import annotations
import os

# ── Color Palette ─────────────────────────────────────────────────────────────
NAVY       = "#0b2545"
NAVY_MID   = "#13315c"
BLUE       = "#1d4ed8"
BLUE_LT    = "#3b82f6"
BLUE_PALE  = "#93c5fd"
AMBER      = "#b45309"
AMBER_LT   = "#f59e0b"
AMBER_PALE = "#fde68a"
GREEN      = "#166534"
GREEN_LT   = "#22c55e"
RED        = "#b91c1c"
RED_LT     = "#ef4444"
PURPLE     = "#6d28d9"
PURPLE_LT  = "#a78bfa"
TEAL       = "#0f766e"
TEAL_LT    = "#14b8a6"
GRAY       = "#94a3b8"
GRAY_LT    = "#e2e8f0"
GRAY_XLT   = "#f1f5f9"
SLATE      = "#64748b"
DARK       = "#1e293b"
WHITE      = "#ffffff"

# ── Plotly Base Layout ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, Segoe UI, sans-serif", size=12, color=DARK),
    xaxis=dict(gridcolor=GRAY_LT, linecolor=GRAY_LT, zeroline=False),
    yaxis=dict(gridcolor=GRAY_LT, linecolor=GRAY_LT, zeroline=False),
    legend=dict(orientation="h", y=1.14, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)", font_size=12, bordercolor=GRAY_LT),
)

# ── Column Mappings ───────────────────────────────────────────────────────────
RAW_COLUMN_MAP = {
    "Date": "date",
    "Children apprehended and placed in CBP custody*": "cbp_intake",
    "Children apprehended and placed in CBP custody": "cbp_intake",
    "Children in CBP custody": "cbp_custody",
    "Children transferred out of CBP custody": "cbp_transferred_out",
    "Children in HHS Care": "hhs_care",
    "Children discharged from HHS Care": "hhs_discharged",
}

NUMERIC_COLS = [
    "cbp_intake",
    "cbp_custody",
    "cbp_transferred_out",
    "hhs_care",
    "hhs_discharged",
]

# ── Operational Thresholds ───────────────────────────────────────────────────
DOR_TARGET = 1.05          # Discharge offset ratio >= 1.05 implies backlog de-escalation
EQUILIBRIUM_LOWER = 0.95   # 0.95 to 1.05 implies near equilibrium
VOLATILITY_THRESHOLD = 5.0 # Care volatility index threshold in %
