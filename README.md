# UAC System Capacity & Care Load Analytics — v3.0

**HHS Unaccompanied Alien Children Program** — Live interactive analytics dashboard built with Streamlit, Plotly, Pandas, and NumPy.

## Features

- **6 KPI Cards** — Total children under care, HHS care census, net intake pressure, discharge offset ratio, backlog streak, volatility index
- **5 Interactive Tabs:**
  - 📈 **System Load** — Total load timeline, year-over-year comparison, monthly averages
  - 🔄 **CBP ↔ HHS Pipeline** — CBP vs HHS dual-axis, net intake/backlog, transfers vs discharges, discharge offset ratio
  - 📊 **Deep Dive** — Volatility index, quarterly breakdowns with error bars, streak distribution, OLS scatter with R²
  - 🔮 **Forecast** — Configurable horizon + lookback OLS trend projections with ±1.5σ confidence bands
  - 🧹 **Data Quality** — Validation flags, gap distribution, null summary, raw data viewer, CSV download
- **Date range, granularity, and series toggles** via the sidebar
- **Upload support** — Drop a raw HHS CSV export and the full ETL pipeline runs in-memory
- **Deployment-ready** — Streamlit Cloud, Docker, Heroku, Railway, Render

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`. Reads `uac_metrics.csv` from the working directory by default.

## Reproducing the Pipeline from Scratch

```bash
python clean_data.py          # auto-detects raw CSV → cleaned_uac_data.csv
python derive_metrics.py      # cleaned_uac_data.csv → uac_metrics.csv
streamlit run streamlit_app.py
```

## Deploy

### Streamlit Community Cloud (recommended — free)
1. Push to GitHub
2. [share.streamlit.io](https://share.streamlit.io) → New app → select repo → branch `main` → file `streamlit_app.py`
3. Deploy. First build: 1–3 min.

### Docker
```bash
docker build -t uac-analytics .
docker run -p 8501:8501 uac-analytics
```

### Railway / Render
Connect GitHub repo — both read the `Procfile` automatically.

## Files

| File | Purpose |
|---|---|
| `streamlit_app.py` | Full interactive dashboard (v3.0) |
| `clean_data.py` | Step 1: parse & clean raw HHS export |
| `derive_metrics.py` | Step 2: compute all derived KPIs |
| `uac_metrics.csv` | Pre-computed dataset (720 reported days) |
| `requirements.txt` | Python dependencies (4 packages) |
| `Dockerfile` | Container build with health check |
| `Procfile` | PaaS start command (Heroku/Railway/Render) |
| `runtime.txt` | Python version pin |
| `.streamlit/config.toml` | Theme + server config |
| `UAC_Research_Paper.docx` | Full EDA, methodology, findings |
| `UAC_Executive_Summary.docx` | One-page stakeholder summary |

## Tech Stack

- **Python 3.11**
- **Streamlit** ≥ 1.35
- **Plotly** ≥ 5.20
- **Pandas** ≥ 2.0
- **NumPy** ≥ 1.24

Built for HHS/ORR program operational analytics.
