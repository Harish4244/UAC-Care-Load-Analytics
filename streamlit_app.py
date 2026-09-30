"""
UAC System Capacity & Care Load Analytics — Streamlit Dashboard v3.2
HHS Unaccompanied Alien Children Program

Architecture:
    - Modular architecture powered by src package (config, pipeline, forecasting, components)
    - Fully backwards and forwards compatible across Streamlit versions (zero deprecation warnings)
    - Resilient multi-tier data loading (upload -> data/processed -> root fallbacks)

Run locally:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Deploy:
    Push to GitHub -> connect to Streamlit Community Cloud (entrypoint: streamlit_app.py)
"""

from __future__ import annotations

import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import (
    NAVY,
    NAVY_MID,
    BLUE,
    BLUE_LT,
    BLUE_PALE,
    AMBER,
    AMBER_LT,
    AMBER_PALE,
    GREEN,
    GREEN_LT,
    RED,
    RED_LT,
    PURPLE,
    PURPLE_LT,
    TEAL,
    TEAL_LT,
    GRAY,
    GRAY_LT,
    GRAY_XLT,
    SLATE,
    DARK,
    WHITE,
    PLOTLY_LAYOUT,
    NUMERIC_COLS,
    DOR_TARGET,
    EQUILIBRIUM_LOWER,
)
from src.pipeline import (
    clean_raw_dataframe,
    derive_metrics,
    aggregate_data,
    resolve_and_load_data,
)
from src.forecasting import (
    ols_fit,
    generate_linear_forecast,
    generate_weekly_summary,
)
from src.components import (
    render_plotly_chart,
    render_dataframe,
    safe_int,
    build_status_ribbon_html,
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="UAC System Capacity & Care Load Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.hhs.gov/programs/social-services/unaccompanied-children/",
        "About": "UAC Program live analytics dashboard — HHS / ORR v3.2",
    },
)

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS — glassmorphism, animations, refined typography
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* ── Base typography ─────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .block-container { padding-top: 1rem; max-width: 1300px; }

  /* ── Metric cards — glassmorphic ─────────────────────────── */
  [data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(248,250,252,0.95), rgba(241,245,249,0.85));
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 14px;
    padding: 20px 16px 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  [data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06);
    border-color: rgba(59,130,246,0.3);
  }
  [data-testid="metric-container"] label {
    font-size: 11px !important;
    color: #64748b !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 600 !important;
  }
  [data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #0b2545 !important;
    font-family: 'Inter', monospace !important;
    letter-spacing: -0.02em;
  }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11.5px !important;
    font-weight: 500 !important;
  }

  /* ── Sidebar — deep navy gradient ──────────────────────── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b2545 0%, #0d1b2a 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
  }
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 700 !important;
  }
  section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 16px 0 !important;
  }
  section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04);
    border: 1px dashed rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 10px;
  }

  /* ── Tabs — sleek pill style ────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
    border-bottom: none;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #64748b !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s ease;
  }
  .stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0b2545 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
  }

  /* ── Buttons & Downloads ─────────────────────────────────── */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 2px 8px rgba(29,78,216,0.3) !important;
    transition: all 0.2s ease !important;
  }
  .stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(29,78,216,0.4) !important;
  }

  /* ── DataFrames & Tables ─────────────────────────────────── */
  [data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
  }

  /* ── Tooltips & Help Icons ───────────────────────────────── */
  [data-testid="stTooltipIcon"] {
    color: #94a3b8 !important;
  }
</style>
""", unsafe_allow_html=True)


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color string to rgba()."""
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — DATA SOURCE & CONTROLS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 0 20px'>"
        "<span style='font-size:36px'>🛡️</span>"
        "<div style='font-size:14px;font-weight:700;color:#e2e8f0;margin-top:6px;"
        "letter-spacing:0.02em'>UAC Analytics</div>"
        "<div style='font-size:10px;color:#94a3b8;letter-spacing:0.06em;"
        "text-transform:uppercase;margin-top:2px'>HHS / ORR Program • v3.2</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 📂 Data Source")
    uploaded = st.file_uploader(
        "Upload raw HHS UAC CSV (optional)",
        type=["csv"],
        help="If omitted, the app loads processed data from data/processed/ or root automatically.",
    )

# ── Load data ─────────────────────────────────────────────────────────────────

metrics: pd.DataFrame | None = None
source_label = ""

if uploaded is not None:
    try:
        raw_uploaded = pd.read_csv(io.BytesIO(uploaded.getvalue()))
        cleaned = clean_raw_dataframe(raw_uploaded)
        metrics = derive_metrics(cleaned)
        source_label = f"Uploaded: {uploaded.name}"
    except Exception as err:
        st.sidebar.error(f"Error parsing uploaded file: {err}")

if metrics is None:
    try:
        metrics, source_label = resolve_and_load_data()
    except Exception as err:
        st.error(f"**Data loading error:** {err}")
        st.stop()

if metrics is None or metrics.empty:
    st.error(
        "**No data available.** Upload a raw HHS UAC CSV export in the sidebar, "
        "or run `python clean_data.py && python derive_metrics.py`."
    )
    st.stop()

# ── Sidebar filters ──────────────────────────────────────────────────────────

with st.sidebar:
    st.caption(f"✓ {source_label}  ·  {len(metrics):,} rows")
    st.markdown("---")

    st.markdown("### 🔍 Filters")
    min_d, max_d = metrics["date"].min().date(), metrics["date"].max().date()
    date_range = st.date_input(
        "Date range", (min_d, max_d), min_value=min_d, max_value=max_d
    )

    # Safely unpack date range — handles single-date selection
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_d, max_d

    granularity = st.radio(
        "Time granularity", ["Daily", "Weekly", "Monthly"], horizontal=True
    )
    st.markdown("---")

    st.markdown("### 📊 Display")
    show_raw = st.checkbox("Raw / period series", value=True)
    show_roll = st.checkbox("Rolling averages", value=True)
    metric_choice = st.multiselect(
        "CBP vs HHS metrics",
        ["HHS care", "CBP custody"],
        default=["HHS care", "CBP custody"],
    )
    st.markdown("---")

    st.markdown("### 🔮 Forecast")
    fc_horizon = st.slider("Forecast horizon (days)", 7, 90, 30, 1)
    fc_lookback = st.slider("Trend fit window (trailing obs)", 14, 180, 60, 1)
    st.markdown("---")

    st.caption("Source: HHS UAC Program daily operational reporting.")

# ── Filter & aggregate ────────────────────────────────────────────────────────

mask = (metrics["date"].dt.date >= start_d) & (metrics["date"].dt.date <= end_d)
filtered = metrics.loc[mask].copy().reset_index(drop=True)
if filtered.empty:
    st.warning("No data in the selected date range. Adjust the sidebar filters.")
    st.stop()

agg = aggregate_data(filtered, granularity)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER BANNER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="
  background: linear-gradient(135deg, {NAVY} 0%, {NAVY_MID} 50%, #1d4e89 100%);
  padding: 28px 32px;
  border-radius: 16px;
  border-bottom: 4px solid {AMBER_LT};
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(11,37,69,0.25), 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
">
  <div style="position:absolute;top:0;right:0;width:200px;height:200px;
    background:radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
    border-radius:50%;transform:translate(30%,-30%);"></div>
  <div style="position:absolute;bottom:0;left:50%;width:300px;height:300px;
    background:radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%);
    border-radius:50%;transform:translate(-50%,50%);"></div>
  <div style="position:relative;z-index:1">
    <div style="color:{BLUE_PALE};font-family:monospace;font-size:11px;
      letter-spacing:0.1em;font-weight:500;text-transform:uppercase">
      U.S. DEPT. OF HEALTH &amp; HUMAN SERVICES — OFFICE OF REFUGEE RESETTLEMENT
    </div>
    <div style="color:#fff;font-size:28px;font-weight:800;margin-top:8px;
      letter-spacing:-0.025em;line-height:1.2">
      UAC System Capacity &amp; Care Load Analytics
    </div>
    <div style="color:#bfdbfe;font-size:14px;margin-top:10px;max-width:860px;
      line-height:1.65;font-weight:400">
      Continuous monitoring of the CBP-to-HHS care pipeline for unaccompanied children —
      daily load, intake/discharge balance, capacity stress indicators, and trend forecasts
      across <strong style="color:{AMBER_PALE}">{len(filtered):,} reported observations</strong>
      <span style="opacity:0.7">({start_d} → {end_d})</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════

last = filtered.iloc[-1]
last30 = filtered.tail(30)
prev30 = (filtered.iloc[-60:-30] if len(filtered) >= 60
          else filtered.iloc[:max(1, len(filtered) // 2)])

net_avg = last30["net_daily_intake"].mean()
vol_avg = last30["care_volatility_roll14"].mean()
dor_avg = last30["discharge_offset_ratio"].mean()
load_delta = (last30["total_system_load"].mean() - prev30["total_system_load"].mean()
              if not prev30.empty else 0)

c1, c2, c3, c4, c5, c6 = st.columns(6)

_total_load = safe_int(last["total_system_load"])
_cbp = safe_int(last["cbp_custody"])
_hhs = safe_int(last["hhs_care"])
_last_date = last["date"].strftime("%Y-%m-%d") if pd.notna(last["date"]) else "N/A"

c1.metric(
    "🧒 Total Under Care",
    f"{_total_load:,}",
    delta=f"{load_delta:+,.0f} vs prev 30d",
    help=f"{_cbp:,} CBP + {_hhs:,} HHS as of {_last_date}",
)
c2.metric(
    "🏠 HHS Care (latest)",
    f"{_hhs:,}",
)
c3.metric(
    "📥 Net Intake Pressure",
    f"{net_avg:+.1f}/day" if pd.notna(net_avg) else "—",
    help="30-obs avg (positive = accumulating backlog)",
)
c4.metric(
    "⚖️ Discharge Offset",
    f"{dor_avg:.2f}" if pd.notna(dor_avg) else "—",
    help="Discharges ÷ transfers-in (>1 = load reducing)",
)
c5.metric(
    "🔁 Backlog Streak",
    f"{safe_int(last['backlog_streak'])} days",
    help="Current consecutive run of net-accumulation days",
)
c6.metric(
    "📊 Volatility Index",
    f"{vol_avg:.2f}%" if pd.notna(vol_avg) else "—",
    help="14-obs rolling σ of daily HHS care % change",
)

# ── Dynamic Status Ribbon ───────────────────────────────────────────────────

peak_row = filtered.loc[filtered["total_system_load"].idxmax()]
peak_load = safe_int(peak_row["total_system_load"])
peak_date = peak_row["date"].strftime("%b %d, %Y") if pd.notna(peak_row["date"]) else "N/A"
latest_load = _total_load
pct_of_peak = (latest_load / peak_load) * 100 if peak_load > 0 else 0

if pd.notna(dor_avg) and dor_avg >= DOR_TARGET:
    status_badge = "🟢 STABLE / DE-ESCALATING"
    status_color = "#166534"
    status_bg = "#f0fdf4"
    pct_above = (dor_avg - 1) * 100
    status_desc = f"Discharges outpace transfers by <b>{pct_above:.1f}%</b> over the last 30 observations, reducing shelter pressure."
elif pd.notna(dor_avg) and dor_avg >= EQUILIBRIUM_LOWER:
    status_badge = "🟡 EQUILIBRIUM"
    status_color = "#b45309"
    status_bg = "#fffbeb"
    status_desc = "Transfers and discharges are closely balanced. Caseload remains steady."
else:
    status_badge = "🔴 ACCUMULATING BACKLOG"
    status_color = "#b91c1c"
    status_bg = "#fef2f2"
    _net_display = f"{net_avg:+.1f}" if pd.notna(net_avg) else "N/A"
    status_desc = f"Transfers into HHS exceed discharges. Caseload accumulating at net <b>{_net_display}</b> children/day."

st.markdown(
    build_status_ribbon_html(
        status_badge,
        status_color,
        status_bg,
        status_desc,
        latest_load,
        peak_load,
        peak_date,
        pct_of_peak,
    ),
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 System Load",
    "🔄 CBP ↔ HHS Pipeline",
    "📊 Deep Dive",
    "🔮 Forecast",
    "🧹 Data Quality",
])

# ── TAB 1: System Load ───────────────────────────────────────────────────────

with tab1:
    st.subheader("Total System Load Over Time")
    st.caption("CBP custody + HHS care, with the upper-quartile of the "
               "selected range shaded as a high-load zone.")

    threshold = filtered["total_system_load"].quantile(0.75)
    fig1 = go.Figure()
    fig1.add_hrect(
        y0=threshold, y1=agg["total_system_load"].max() * 1.02,
        fillcolor=hex_to_rgba(RED, 0.06), line_width=0,
        annotation_text=f"Upper-quartile load (≥{threshold:,.0f})",
        annotation_position="top right",
        annotation_font=dict(color=RED, size=10),
    )
    if show_raw:
        fig1.add_trace(go.Scatter(
            x=agg["date"], y=agg["total_system_load"],
            name="Daily total load",
            line=dict(color=GRAY, width=1), opacity=0.6,
        ))
    if show_roll:
        fig1.add_trace(go.Scatter(
            x=agg["date"], y=agg["total_load_roll7"],
            name="7-obs rolling avg",
            line=dict(color=NAVY, width=2.8),
        ))
    fig1.update_layout(**PLOTLY_LAYOUT, height=400,
                       yaxis_title="Children under care")
    render_plotly_chart(fig1)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Year-over-Year Comparison")
        st.caption("Total system load by day-of-year, one line per "
                   "calendar year in the selection.")
        yoy = filtered.copy()
        yoy["year"] = yoy["date"].dt.year
        yoy["doy"] = yoy["date"].dt.dayofyear
        years = sorted(yoy["year"].unique())
        palette_yoy = [BLUE_LT, AMBER_LT, GREEN_LT, PURPLE_LT, RED_LT, TEAL_LT]
        fig_yoy = go.Figure()
        for i, yr in enumerate(years):
            sub = yoy[yoy["year"] == yr].sort_values("doy")
            fig_yoy.add_trace(go.Scatter(
                x=sub["doy"], y=sub["total_system_load"],
                name=str(yr),
                line=dict(color=palette_yoy[i % len(palette_yoy)], width=2.2),
            ))
        fig_yoy.update_layout(**PLOTLY_LAYOUT, height=340,
                              xaxis_title="Day of year",
                              yaxis_title="Total system load")
        render_plotly_chart(fig_yoy)

    with col_b:
        st.subheader("Monthly Average System Load")
        monthly = (filtered.set_index("date")["total_system_load"]
                   .resample("MS").mean().reset_index())
        fig_bar = go.Figure(go.Bar(
            x=monthly["date"], y=monthly["total_system_load"],
            marker_color=NAVY,
            text=monthly["total_system_load"].round(0).astype(int),
            textposition="outside", textfont_size=9,
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                              yaxis_title="Avg total load")
        render_plotly_chart(fig_bar)


# ── TAB 2: CBP ↔ HHS Pipeline ───────────────────────────────────────────────

with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("CBP Custody vs. HHS Care Load")
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        if "HHS care" in metric_choice:
            fig2.add_trace(go.Scatter(
                x=agg["date"], y=agg["hhs_care"],
                name="HHS care", line=dict(color=NAVY, width=2.2),
            ), secondary_y=False)
        if "CBP custody" in metric_choice:
            fig2.add_trace(go.Scatter(
                x=agg["date"], y=agg["cbp_custody"],
                name="CBP custody", line=dict(color=AMBER, width=1.8),
            ), secondary_y=True)
        fig2.update_layout(**PLOTLY_LAYOUT, height=360)
        fig2.update_yaxes(title_text="HHS care", secondary_y=False)
        fig2.update_yaxes(title_text="CBP custody", secondary_y=True)
        render_plotly_chart(fig2)

    with col_r:
        st.subheader("Net Intake & Backlog Trend")
        st.caption("Amber = accumulating backlog · Gray = load reducing · "
                   "Red line = 7-obs rolling avg.")
        fig3 = go.Figure()
        if show_raw:
            colors = [AMBER if v >= 0 else GRAY
                      for v in agg["net_daily_intake"].fillna(0)]
            fig3.add_trace(go.Bar(
                x=agg["date"], y=agg["net_daily_intake"],
                name="Net daily intake", marker_color=colors, opacity=0.80,
            ))
        if show_roll:
            fig3.add_trace(go.Scatter(
                x=agg["date"], y=agg["net_intake_roll7"],
                name="7-obs rolling avg", line=dict(color=RED, width=2.2),
            ))
        fig3.add_hline(y=0, line_dash="dot", line_color=GRAY, line_width=1)
        fig3.update_layout(**PLOTLY_LAYOUT, height=360)
        render_plotly_chart(fig3)

    st.subheader("Transfers-In vs. Discharges (Pipeline Flow)")
    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(
        x=agg["date"], y=agg["cbp_transferred_out"],
        name="CBP → HHS Transfers",
        line=dict(color=AMBER_LT, width=1.8),
        fill="tozeroy", fillcolor=hex_to_rgba(AMBER, 0.06),
    ))
    fig_flow.add_trace(go.Scatter(
        x=agg["date"], y=agg["hhs_discharged"],
        name="HHS Discharges",
        line=dict(color=GREEN_LT, width=1.8),
        fill="tozeroy", fillcolor=hex_to_rgba(GREEN, 0.06),
    ))
    fig_flow.update_layout(**PLOTLY_LAYOUT, height=320,
                           yaxis_title="Children / period")
    render_plotly_chart(fig_flow)

    st.subheader("Discharge Offset Ratio (Discharges ÷ Transfers-In)")
    st.caption("Values > 1.0 = load reducing · Values < 1.0 = backlog accumulation.")
    dor_max = agg["discharge_offset_ratio"].max(skipna=True)
    fig_dor = go.Figure()
    fig_dor.add_hrect(
        y0=1.0, y1=(dor_max * 1.05 if pd.notna(dor_max) else 2),
        fillcolor=hex_to_rgba(GREEN, 0.05), line_width=0,
    )
    fig_dor.add_trace(go.Scatter(
        x=agg["date"], y=agg["discharge_offset_ratio"],
        name="DOR", line=dict(color=TEAL, width=1.8),
    ))
    fig_dor.add_hline(
        y=1.0, line_dash="dash", line_color=GREEN, line_width=1.5,
        annotation_text="Equilibrium (1.0)",
        annotation_position="top left",
        annotation_font_color=GREEN,
    )
    fig_dor.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="Ratio")
    render_plotly_chart(fig_dor)


# ── TAB 3: Deep Dive ─────────────────────────────────────────────────────────

with tab3:
    st.subheader("Care Load Volatility Index")
    st.caption("14-obs rolling σ of day-over-day % change in HHS care load. "
               "Spikes = rapid, unstable caseload shifts.")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=agg["date"], y=agg["care_volatility_roll14"],
        name="Volatility", line=dict(color=PURPLE, width=1.8),
        fill="tozeroy", fillcolor=hex_to_rgba(PURPLE, 0.08),
    ))
    fig4.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="Volatility (%)")
    render_plotly_chart(fig4)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Quarterly Breakdown")
        q = filtered.copy()
        q["quarter"] = q["date"].dt.to_period("Q").astype(str)
        qstats = q.groupby("quarter")["total_system_load"].agg(["mean", "std"]).reset_index()
        fig_q = go.Figure()
        fig_q.add_trace(go.Bar(
            x=qstats["quarter"], y=qstats["mean"],
            name="Avg. total load", marker_color=NAVY,
            error_y=dict(type="data", array=qstats["std"].fillna(0), color=GRAY),
            text=qstats["mean"].round(0).astype(int),
            textposition="outside", textfont_size=9,
        ))
        fig_q.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                            yaxis_title="Avg. total system load")
        render_plotly_chart(fig_q)

        st.subheader("Backlog Streak Distribution")
        streaks = filtered.loc[filtered["backlog_streak"] > 0, "backlog_streak"]
        if streaks.empty:
            st.info("No positive backlog streaks in the selected range.")
        else:
            fig_hist = go.Figure(go.Histogram(
                x=streaks, marker_color=AMBER,
                nbinsx=max(int(streaks.max()), 1),
            ))
            fig_hist.update_layout(
                **PLOTLY_LAYOUT, height=300,
                xaxis_title="Streak length (consecutive days)",
                yaxis_title="Occurrences",
            )
            render_plotly_chart(fig_hist)

    with col_b:
        st.subheader("HHS Care Load vs. Discharge Offset Ratio")
        st.caption("Each point = one reported day · OLS fit line with R² score.")
        scatter_df = filtered[["hhs_care", "discharge_offset_ratio"]].dropna()
        fit = ols_fit(scatter_df["hhs_care"].to_numpy(),
                      scatter_df["discharge_offset_ratio"].to_numpy())
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=scatter_df["hhs_care"],
            y=scatter_df["discharge_offset_ratio"],
            mode="markers",
            marker=dict(color=NAVY, size=5, opacity=0.45,
                        line=dict(width=0.5, color="white")),
            name="Reported days",
        ))
        if fit is not None:
            order = np.argsort(fit["x"])
            fig_sc.add_trace(go.Scatter(
                x=fit["x"][order], y=fit["y_hat"][order], mode="lines",
                line=dict(color=RED, width=2.2),
                name=f"OLS fit (R²={fit['r_squared']:.2f})",
            ))
        fig_sc.update_layout(
            **PLOTLY_LAYOUT, height=340,
            xaxis_title="Children in HHS Care",
            yaxis_title="Discharge Offset Ratio",
        )
        render_plotly_chart(fig_sc)

        if fit is not None:
            direction = "rises" if fit["slope"] > 0 else "falls"
            st.caption(
                f"Fitted slope: {fit['slope']:.6f} — the discharge offset ratio "
                f"{direction} as HHS care load increases "
                f"(R² = {fit['r_squared']:.2f})."
            )

        st.subheader("Quarterly Net Intake & DOR")
        q2 = filtered.copy()
        q2["quarter"] = q2["date"].dt.to_period("Q").astype(str)
        q_metrics = q2.groupby("quarter").agg(
            net_intake=("net_daily_intake", "mean"),
            dor=("discharge_offset_ratio", "mean"),
        ).reset_index()
        fig_q2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_q2.add_trace(go.Bar(
            x=q_metrics["quarter"], y=q_metrics["net_intake"],
            name="Avg net intake",
            marker_color=[AMBER if v >= 0 else GRAY
                          for v in q_metrics["net_intake"].fillna(0)],
        ), secondary_y=False)
        fig_q2.add_trace(go.Scatter(
            x=q_metrics["quarter"], y=q_metrics["dor"],
            name="Avg DOR", mode="lines+markers",
            line=dict(color=TEAL, width=2), marker=dict(size=7),
        ), secondary_y=True)
        fig_q2.add_hline(y=1.0, line_dash="dot", line_color=GREEN,
                         line_width=1, secondary_y=True)
        fig_q2.update_layout(**PLOTLY_LAYOUT, height=320)
        fig_q2.update_yaxes(title_text="Net intake", secondary_y=False)
        fig_q2.update_yaxes(title_text="DOR", secondary_y=True)
        render_plotly_chart(fig_q2)


# ── TAB 4: Forecast ──────────────────────────────────────────────────────────

with tab4:
    st.subheader(f"{fc_horizon}-Day Linear Trend Forecast")
    st.caption(
        f"Trend fit on the trailing {fc_lookback} reported observations, "
        "projected forward with a ±1.5σ residual band. A straight-line "
        "projection is a directional signal, not a policy prediction."
    )

    fc_col1, fc_col2 = st.columns(2)
    targets = [
        ("HHS Care Load", "hhs_care", NAVY),
        ("Total System Load", "total_system_load", TEAL),
    ]

    for col, (label, field, color) in zip([fc_col1, fc_col2], targets):
        with col:
            result = generate_linear_forecast(
                filtered["date"], filtered[field], fc_horizon, fc_lookback
            )
            st.markdown(f"**{label}**")
            if result is None:
                st.info("Not enough observations to fit a trend.")
                continue
            band = 1.5 * result["resid_std"]
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(
                x=result["history_dates"], y=result["history_values"],
                name="Observed", line=dict(color=GRAY, width=1),
            ))
            fig_f.add_trace(go.Scatter(
                x=result["fit_dates"], y=result["fit_values"],
                name="Trend fit", line=dict(color=color, width=2.2),
            ))
            fig_f.add_trace(go.Scatter(
                x=result["future_dates"], y=result["future_values"],
                name="Forecast",
                line=dict(color=color, width=2.2, dash="dash"),
            ))
            fig_f.add_trace(go.Scatter(
                x=list(result["future_dates"]) + list(result["future_dates"])[::-1],
                y=(list(result["future_values"] + band)
                   + list(result["future_values"] - band)[::-1]),
                fill="toself", fillcolor=hex_to_rgba(color, 0.10),
                line=dict(width=0), name="±1.5σ band",
            ))
            fig_f.add_vline(
                x=pd.to_datetime(result["history_dates"].iloc[-1]).timestamp() * 1000,
                line_dash="dot", line_color=GRAY, line_width=1,
                annotation_text="Forecast →",
                annotation_position="top left",
                annotation_font=dict(color=GRAY, size=10),
            )
            fig_f.update_layout(**PLOTLY_LAYOUT, height=340,
                                yaxis_title=label)
            render_plotly_chart(fig_f)

            per_day = result["slope_per_day"]
            forecast_end = result["future_values"][-1]
            st.caption(
                f"Trend: **{per_day:+.2f}** children/day · "
                f"R² = {result['r_squared']:.2f} · "
                f"Projected at horizon end: **{forecast_end:,.0f}** ± {band:,.0f}"
            )

    st.subheader("Weekly Forecast Summary")
    result_total = generate_linear_forecast(
        filtered["date"], filtered["total_system_load"], fc_horizon, fc_lookback
    )
    if result_total is not None:
        weekly = generate_weekly_summary(result_total, confidence_factor=1.5)
        render_dataframe(weekly, hide_index=True)
        st.download_button(
            label="⬇️ Download Weekly Forecast Summary (CSV)",
            data=weekly.to_csv(index=False).encode("utf-8"),
            file_name=f"uac_forecast_{fc_horizon}d_{start_d}_{end_d}.csv",
            mime="text/csv",
        )
    else:
        st.info("Not enough data for a weekly summary in the current selection.")


# ── TAB 5: Data Quality ─────────────────────────────────────────────────────

with tab5:
    st.subheader("Data Quality & Validation Report")
    total = len(filtered)
    fl_tr = int(filtered["flag_transfer_exceeds_custody"].sum())
    fl_dc = int(filtered["flag_discharge_exceeds_care"].sum())
    gap_rows = filtered[filtered["gap_days"].notna() & (filtered["gap_days"] > 1)]

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Total Observations", f"{total:,}")
    q2.metric("Transfer > Custody Flags", f"{fl_tr:,}",
              delta=f"{fl_tr / total * 100:.1f}% of rows" if total > 0 else "0%",
              delta_color="inverse")
    q3.metric("Discharge > Care Flags", f"{fl_dc:,}",
              delta=f"{fl_dc / total * 100:.1f}% of rows" if total > 0 else "0%",
              delta_color="inverse")
    q4.metric("Reporting Gaps (>1 day)", f"{len(gap_rows):,}")

    if total > 0:
        fl_tr_pct = fl_tr / total * 100
        st.info(
            f"**{fl_tr}** of **{total}** days ({fl_tr_pct:.1f}%) show "
            "transfers-out exceeding the same-day CBP custody snapshot — "
            "**flagged, not corrected** — consistent with intra-day "
            "intake/transfer timing, not a data error. "
            f"**{fl_dc}** instance(s) of discharges exceeding HHS care load.",
            icon="ℹ️",
        )

    col_a, col_b = st.columns(2)

    with col_a:
        if not gap_rows.empty:
            st.subheader("Reporting Gap Distribution")
            gaps = filtered["gap_days"].dropna()
            fig_gap = go.Figure(go.Histogram(
                x=gaps, marker_color=PURPLE,
                nbinsx=max(int(gaps.max()) if not gaps.empty else 1, 1),
            ))
            fig_gap.update_layout(
                **PLOTLY_LAYOUT, height=300,
                xaxis_title="Days since previous report",
                yaxis_title="Occurrences",
            )
            render_plotly_chart(fig_gap)

    with col_b:
        st.subheader("Missing / Null Summary")
        nc = filtered[NUMERIC_COLS].isna().sum().reset_index()
        nc.columns = ["Field", "Missing Count"]
        nc["% Missing"] = (nc["Missing Count"] / total * 100).round(2) if total > 0 else 0
        if nc["Missing Count"].sum() == 0:
            st.success("✅ No missing values in the core fields for the selected date range.")
        else:
            render_dataframe(nc, hide_index=True)

    with st.expander("📋 View underlying data table", expanded=False):
        render_dataframe(filtered.reset_index(drop=True), hide_index=True, height=400)

    st.download_button(
        label="⬇️ Download filtered dataset (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"uac_filtered_{start_d}_{end_d}.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px 24px;
  margin-top: 32px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
">
  <strong style="color:#0b2545">Source:</strong> HHS Unaccompanied Alien Children Program
  daily operational reporting (HHS.gov/ORR).
  Figures reflect published aggregate counts; reporting is not on a strict
  calendar-day cadence.
  &nbsp;|&nbsp;
  <strong style="color:#0b2545">Dashboard v3.2</strong>
  &nbsp;|&nbsp;
  <strong style="color:#0b2545">Data window:</strong> {start_d} – {end_d}
  &nbsp;|&nbsp;
  <strong style="color:#0b2545">{total:,}</strong> observations
  &nbsp;|&nbsp;
  Forecasts are a simple linear baseline for situational awareness, not a
  policy prediction.
</div>
""", unsafe_allow_html=True)
