# Production Deployment Guide — UAC System Capacity & Care Load Analytics

**HHS Unaccompanied Alien Children Program — Executive Analytics Dashboard v3.2**

---

## 1. Overview & Architecture

This repository contains the complete production-ready source code, data pipelines, automated tests, container configurations, and documentation for the **UAC System Capacity & Care Load Analytics** platform.

### Tech Stack
- **Dashboard Framework:** Streamlit (>=1.35, <2.0)
- **Data Engine:** Pandas (>=2.0, <3.0), NumPy (>=1.24, <3.0)
- **Visualization Engine:** Plotly (>=5.20, <6.0)
- **Runtime:** Python 3.11 (`runtime.txt`)
- **Containers:** Docker (`Dockerfile` + `.dockerignore`) with built-in health checks
- **PaaS Deployments:** Heroku / Railway / Render (`Procfile`)
- **Design System:** Custom Enterprise Glassmorphism CSS, Inter Typography, Dark Navy Brand Palette (`.streamlit/config.toml`)
- **Automated Tests:** Unit & integration test suite (`tests/`)

---

## 2. Local Setup & Execution

### Prerequisites
- Python 3.11 installed
- Git installed

### Quick Start
```bash
# 1. Clone repository & enter workspace
git clone https://github.com/Harish4244/UAC-Care-Load-Analytics.git
cd UAC-Care-Load-Analytics

# 2. Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
# source .venv/bin/activate

# 3. Install production dependencies (lightweight: only 4 core packages)
pip install -r requirements.txt

# 4. Run dashboard
streamlit run streamlit_app.py
```
App will launch at `http://localhost:8501`.

### Data Ingestion & Pipeline Regeneration
To clean new raw HHS data exports and derive updated operational metrics:
```bash
# Step 1: Clean raw data (auto-detects from data/raw/ or root)
python clean_data.py

# Step 2: Derive rolling metrics, streaks, volatility & quality flags
python derive_metrics.py

# Step 3: Run full automated test suite
python -m unittest discover tests
```

---

## 3. Deployment Option 1: Streamlit Community Cloud (Recommended Free Host)

Streamlit Community Cloud provides 1-click continuous deployment directly from your GitHub repository.

1. **Commit and Push to GitHub**:
   ```bash
   git add .
   git commit -m "feat: complete production release v3.2 with modular architecture"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**.
4. Select your repository (`Harish4244/UAC-Care-Load-Analytics`), branch (`main`), and set **Main file path** to `streamlit_app.py`.
5. Under **Advanced settings**, confirm Python version is set to **3.11** (matching `runtime.txt`).
6. Click **Deploy**. Your app will be live with an SSL-secured URL (`https://<app-name>.streamlit.app`).

---

## 4. Deployment Option 2: Docker Container (Cloud Run / AWS ECS / Self-Hosted)

The included `Dockerfile` utilizes a minimal `python:3.11-slim` base, non-root best practices, built-in health checks (`/_stcore/health` via native Python standard library), and port binding for container orchestrators.

### Build and Run Locally
```bash
# Build image
docker build -t uac-analytics:v3.2 .

# Run container
docker run -p 8501:8501 --name uac-dashboard uac-analytics:v3.2
```
Test health check:
```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8501/_stcore/health').read().decode())"
```

### Deploy to Google Cloud Run
```bash
gcloud run deploy uac-analytics \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```

### Deploy to AWS App Runner / ECS
Push the Docker image to Amazon ECR, then launch via AWS App Runner or ECS Fargate pointing to port 8501.

---

## 5. Deployment Option 3: Heroku / Railway / Render (PaaS)

The repository includes a validated `Procfile` and `runtime.txt` configured with `$PORT` binding for dynamic cloud environments.

### Procfile Specification
```procfile
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

### Deployment Steps (Railway / Render):
1. Connect your GitHub repository at [railway.app](https://railway.app) or [render.com](https://render.com).
2. The platform will automatically detect Python 3.11 via `runtime.txt` and execute the `Procfile`.
3. Set environment variable `PORT` if required (most platforms inject this automatically).
4. Deploy completes in under 2 minutes.

---

## 6. Pre-Flight Verification Checklist

Before final sign-off, verify the following:
- [x] `streamlit run streamlit_app.py` boots clean with zero warnings.
- [x] All 5 interactive tabs render smoothly:
  - Tab 1: System Load & YoY Day-of-Year trajectory
  - Tab 2: CBP ↔ HHS Intake/Discharge Pipeline Flow
  - Tab 3: Deep Dive (Caseload Volatility, OLS Regression, Streak Histograms)
  - Tab 4: 7-90 Day Dynamic Forecast with $\pm 1.5\sigma$ residual confidence intervals
  - Tab 5: Data Quality Auditor, Gap Distribution, & CSV exporter
- [x] Dynamic metric cards update across date range filters.
- [x] In-memory file uploader accepts raw HHS CSV files and instantly re-derives all metrics on the fly.
- [x] Automated test suite in `tests/` passes 100% of test assertions.
- [x] `requirements.txt` is strictly trimmed to 4 packages (no bloat).
- [x] Dockerfile builds with healthcheck enabled.
- [x] Clean `.dockerignore` and `.gitignore` preventing build pollution.

---

## 7. Metrics & KPI Dictionary

| Metric Name | Formula / Logic | Operational Interpretation |
|---|---|---|
| **Total System Load** | `cbp_custody + hhs_care` | Total unaccompanied minors under federal custody across both agencies |
| **Net Daily Intake** | `cbp_transferred_out - hhs_discharged` | Positive indicates growing HHS shelter backlog; negative indicates de-escalation |
| **Discharge Offset Ratio (DOR)** | `hhs_discharged / cbp_transferred_out` | $>1.0$ indicates care discharges exceed intake (safe); $<1.0$ indicates bottleneck |
| **Backlog Streak** | Cumulative consecutive days where `net_daily_intake > 0` | Measures sustained pressure duration before system relief |
| **Care Volatility Index** | 14-observation rolling $\sigma$ of `% \Delta hhs_care` | Quantifies turbulence and predictability of shelter capacity |
| **OLS Trend Forecast** | Ordinary Least Squares linear regression ($y = mx + b$) | Baseline trajectory projection with residual confidence bands |
