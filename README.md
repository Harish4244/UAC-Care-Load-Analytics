# UAC System Capacity & Care Load Analytics — v3.2

**HHS Unaccompanied Alien Children Program** — Production-grade interactive operational analytics dashboard built with Streamlit, Plotly, Pandas, and NumPy.

---

## 🏗️ Project Architecture & Directory Structure

```text
UAC-Care-Load-Analytics/
├── .streamlit/
│   └── config.toml               # Streamlit theme & production server settings
├── data/
│   ├── raw/                      # Raw HHS data exports
│   │   └── HHS_Unaccompanied_Alien_Children_Program.csv
│   └── processed/                # Production pipeline outputs
│       ├── cleaned_uac_data.csv
│       └── uac_metrics.csv
├── docs/                         # Executive & research documentation
│   ├── UAC_Executive_Summary.docx
│   └── UAC_Research_Paper.docx
├── src/                          # Modular core application engine
│   ├── __init__.py
│   ├── config.py                 # Design tokens, color palette, column schemas
│   ├── pipeline.py               # Ingestion, cleaning, metric derivation, aggregation
│   ├── forecasting.py            # OLS regression & residual confidence intervals
│   └── components.py             # Safe rendering adapters (forward/backward compatible)
├── tests/                        # Automated unit and integration test suite
│   ├── test_pipeline.py          # Data transformations & forecasting tests
│   └── test_app.py               # Full Streamlit AppTest execution test
├── clean_data.py                 # CLI runner for data cleaning & normalization
├── derive_metrics.py             # CLI runner for capacity & streak derivation
├── streamlit_app.py              # Main dashboard application entrypoint
├── requirements.txt              # Pinned Python dependencies
├── runtime.txt                   # Target Python runtime version (3.11)
├── Dockerfile                    # Container configuration with native health checks
├── .dockerignore                 # Production build ignore rules
├── .gitignore                    # Git tracking ignore rules
├── Procfile                      # PaaS deployment entrypoint (Heroku/Railway/Render)
├── README.md                     # Architecture & usage documentation
└── DEPLOYMENT_GUIDE.md           # Step-by-step production deployment manual
```

---

## 🚀 Quick Start

### 1. Local Setup
```bash
# Clone the repository
git clone https://github.com/Harish4244/UAC-Care-Load-Analytics.git
cd UAC-Care-Load-Analytics

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # On Windows
# source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run streamlit_app.py
```
Dashboard launches at `http://localhost:8501`.

### 2. Running Data Pipeline & Tests
```bash
# Clean raw HHS data export
python clean_data.py

# Compute derived capacity metrics & streaks
python derive_metrics.py

# Execute full automated test suite
python -m unittest discover tests
```

---

## 📊 Features & Core Analytics

- **6 Executive KPI Cards:**
  - 🧒 **Total Under Care** (CBP custody + HHS care census with 30-day delta)
  - 🏠 **HHS Care Load** (ORR shelter census)
  - 📥 **Net Intake Pressure** (Daily transfer vs. discharge balance)
  - ⚖️ **Discharge Offset Ratio** (DOR > 1.0 indicates de-escalation)
  - 🔁 **Backlog Streak** (Consecutive observations of net backlog accumulation)
  - 📊 **Volatility Index** (14-observation rolling standard deviation)

- **Dynamic Capacity Ribbon:** Real-time situational badge (🟢 Stable, 🟡 Equilibrium, 🔴 Accumulating Backlog) with contextual capacity benchmarks against historical peak.

- **5 Deep-Dive Analytical Tabs:**
  1. 📈 **System Load:** High-water mark quartile bands, Year-over-Year day-of-year comparisons, monthly averages.
  2. 🔄 **CBP ↔ HHS Pipeline:** Dual-axis custody comparison, net intake pressure, transfer vs. discharge flow, DOR equilibrium.
  3. 📊 **Deep Dive:** Caseload volatility timeline, quarterly aggregate loads with standard error bars, backlog streak histograms, OLS scatter regression.
  4. 🔮 **Forecast:** Horizon (7–90 days) and lookback window (14–180 obs) OLS trend extrapolation with ±1.5σ residual confidence bands and downloadable weekly projection tables.
  5. 🧹 **Data Quality:** Automated audit of intra-day snapshot flags, reporting gap histograms, null/missing values audit, and filtered raw data viewer.

---

## 🚢 Deployment

### Streamlit Community Cloud (Recommended Free Host)
1. Push all code to GitHub (`main` branch).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
3. Select your repository, set branch to `main`, and **Main file path** to `streamlit_app.py`.
4. Deploy! Live in ~1–2 minutes.

### Docker Container
```bash
docker build -t uac-analytics .
docker run -p 8501:8501 uac-analytics
```
Includes native health checks at `http://localhost:8501/_stcore/health`.

### Heroku / Railway / Render
All platforms natively detect `Procfile`, `runtime.txt`, and `requirements.txt`.

---

## 🛠️ Tech Stack
- **Python 3.11**
- **Streamlit** (>=1.35, <2.0)
- **Plotly** (>=5.20, <6.0)
- **Pandas** (>=2.0, <3.0)
- **NumPy** (>=1.24, <3.0)
