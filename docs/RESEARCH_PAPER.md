# System Capacity & Care Load Analytics for Unaccompanied Children: Longitudinal Empirical Analysis, Operational Flow Dynamics, and Metric Specification

**Author / Project Lead:** Harish V J  
**Repository:** [Harish4244/UAC-Care-Load-Analytics](https://github.com/Harish4244/UAC-Care-Load-Analytics)  
**Date:** September 2026  
**Document Version:** 3.2.0  
**License:** MIT  

---

## Abstract

The United States Department of Health and Human Services (HHS) and Customs and Border Protection (CBP) operate a critical, interconnected pipeline responsible for the care, custody, and sponsor reunification of Unaccompanied Alien Children (UAC). Understanding custody surges, shelter bed load, transfer bottlenecks, and discharge rates requires rigorous analytical separation between raw observed data, mathematically derived metrics, and empirical stress classifications. This paper presents a complete longitudinal empirical analysis across 720 reporting observations from January 12, 2023 through December 21, 2025. We establish a production-grade analytical pipeline that standardizes operational KPIs: **Total System Load**, **HHS Net Flow Pressure**, **Discharge Offset Ratio (DOR)**, **Care Load Volatility**, and **Backlog Accumulation Streaks**. We demonstrate that the system peaked at **11,516 children** in HHS care on December 20, 2023, subsequently contracting to a low of **1,972 children** on August 21, 2025. We detail the resolution of reporting-day versus calendar-day temporal bias, audit 86 intra-day flow-versus-custody discrepancies, and establish reproducible guidelines for humanitarian operations monitoring.

---

## 1. Introduction & Background

Under the Homeland Security Act of 2002 and the Trafficking Victims Protection Reauthorization Act (TVPRA) of 2008, unaccompanied noncitizen children encountered at the U.S. border are initially apprehended by CBP (Border Patrol), placed into temporary custodial holding, and transferred within 72 hours (barring exceptional circumstances) into the custody of the HHS Office of Refugee Resettlement (ORR). ORR houses children in specialized facilities until they are vetted and safely released to family sponsors, discharged, or age out of the program.

### 1.1 The Operational Challenge
The care pipeline operates under dynamic push-and-pull pressures:
1. **Intake Volatility:** Apprehensions at the Southwest Border fluctuate significantly according to seasonal patterns, regional instability, and policy interventions.
2. **Custodial Congestion:** CBP facilities are short-term holding centers, not long-term childcare facilities. Transfer delays rapidly generate custody backlogs.
3. **ORR Shelter Capacity:** HHS care requires licensed bed space, child welfare personnel, medical infrastructure, and legal caseworkers.
4. **Sponsor Discharge Velocities:** Releasing children safely requires rigorous background checks and sponsor vetting. When discharges fall below incoming transfers, bed occupancy surges exponentially.

### 1.2 Research Objectives
This study establishes:
* A standardized, open-source analytical taxonomy for UAC care load metrics.
* A reproducible data cleansing and validation protocol separating raw observation artifacts from substantive signals.
* An empirical investigation of the 2023–2025 care cycle, identifying operational bottlenecks and equilibrium states.
* An interactive, zero-warning production dashboard architecture facilitating live public policy and humanitarian decision-making.

---

## 2. Data Provenance & Quality Audit

The primary data source consists of official HHS and CBP public transparency reporting exports.

### 2.1 Raw Ingestion & Source Characteristics
* **Raw File:** `HHS_Unaccompanied_Alien_Children_Program.csv`
* **Raw Record Count:** 1,170 lines including header
* **Blank Row Audit:** 450 fully blank trailing rows were detected and removed in the cleaning stage.
* **Effective Observation Count:** 720 valid reporting dates.
* **Temporal Coverage:** January 12, 2023 to December 21, 2025 (1,075 calendar days).
* **Missing Reporting Dates:** 355 calendar days (33.0% of calendar span), reflecting weekends, federal holidays, and intermittent government reporting freezes.

### 2.2 Weekday Reporting Distribution
An audit of observation dates reveals non-uniform reporting cadences:
* **Monday:** 145 observations (20.1%)
* **Tuesday:** 149 observations (20.7%)
* **Wednesday:** 147 observations (20.4%)
* **Thursday:** 147 observations (20.4%)
* **Friday:** 2 observations (0.3% — Friday reports were historically aggregated into weekend/Monday snapshots)
* **Sunday:** 130 observations (18.1%)

```text
Reporting Distribution:
Mon  ████████████████████ 145
Tue  █████████████████████ 149
Wed  ████████████████████ 147
Thu  ████████████████████ 147
Fri  ▏ 2
Sun  ██████████████████ 130
```

> **Key Methodological Principle:** A missing reporting date does **not** signify zero intake or zero care load; it denotes an unobserved date. All calculations distinguish between **reporting observations ($t$)** and **calendar days**.

### 2.3 Field Normalization & Parsing
Raw columns contain thousands separators (e.g. `"2,484"`), currency symbols, and trailing asterisks. The ETL pipeline normalizes the schema into canonical snake_case types:

| Raw HHS Column Header | Canonical Field | Data Type | Operational Definition |
| :--- | :--- | :--- | :--- |
| `Date` | `date` | `datetime64[ns]` | Reporting calendar date |
| `Children apprehended and placed in CBP custody*` | `cbp_intake` | `float64` | Inflow: Children apprehended in 24h window |
| `Children in CBP custody` | `cbp_custody` | `float64` | Stock: Children currently in CBP holding centers |
| `Children transferred out of CBP custody` | `cbp_transferred_out` | `float64` | Flow: Children transferred to HHS ORR care |
| `Children in HHS Care` | `hhs_care` | `float64` | Stock: Total census of children in HHS ORR shelter network |
| `Children discharged from HHS Care` | `hhs_discharged` | `float64` | Flow: Children reunited with sponsors or discharged |

---

## 3. Mathematical & Metric Specification

To avoid ambiguity between operational claims and empirical observations, metrics are formalized into three distinct epistemological tiers:

```
┌────────────────────────────────────────────────────────┐
│ 1. OBSERVED DATA: Direct from reporting records        │
│    (cbp_intake, cbp_custody, transfers, hhs_care, discharges) │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ 2. DERIVED METRICS: Deterministic mathematical formulas│
│    (total_system_load, net_daily_intake, DOR, volatility)   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ 3. FLAGGED CLASSIFICATIONS: Empirical thresholds       │
│    (backlog_streaks, flow_vs_stock flags, stress regimes)│
└────────────────────────────────────────────────────────┘
```

### 3.1 Total System Load
The combined stock of children held across both institutional stages at observation $t$:

$$\text{Total System Load}_t = \text{CBP Custody}_t + \text{HHS Care}_t$$

* **Dimension:** Stock (Census headcount).
* **Significance:** Represents the aggregate custodial burden on the federal government.

### 3.2 HHS Net Daily Intake (Flow Balance)
The net differential between admissions into and releases from the ORR shelter system:

$$\text{Net Daily Intake}_t = \text{CBP Transferred Out}_t - \text{HHS Discharged}_t$$

* **Equilibrium:** $\text{Net Intake}_t = 0$
* **Accumulation Phase:** $\text{Net Intake}_t > 0$ (transfers exceed discharges, expanding shelter census).
* **De-escalation Phase:** $\text{Net Intake}_t < 0$ (discharges exceed transfers, relieving shelter census).

### 3.3 Discharge Offset Ratio (DOR)
The primary efficiency metric evaluating whether exit capacity matches entry volume:

$$\text{DOR}_t = \frac{\text{HHS Discharged}_t}{\text{CBP Transferred Out}_t}$$

* **Target:** $\text{DOR} \ge 1.05$ (active de-escalation).
* **Equilibrium Band:** $0.95 \le \text{DOR} \le 1.05$.
* **Critical Bottleneck:** $\text{DOR} < 0.90$ (shelters taking in children significantly faster than release capacity).

### 3.4 Care Load Volatility Index
A scale-invariant, 14-observation rolling standard deviation measuring system instability:

$$\text{Growth Rate}_t = 100 \times \left( \frac{\text{HHS Care}_t - \text{HHS Care}_{t-1}}{\text{HHS Care}_{t-1}} \right)$$

$$\text{Volatility Index}_t = \sigma_{14}(\text{Growth Rate}_t) = \sqrt{\frac{1}{N-1} \sum_{i=0}^{13} \left( \text{Growth Rate}_{t-i} - \mu_{14} \right)^2}$$

### 3.5 Backlog Persistence Streaks
A cumulative counter tracking sustained systemic pressure:

$$\text{Streak}_t = \begin{cases} \text{Streak}_{t-1} + 1 & \text{if } \text{Net Daily Intake}_t > 0 \\ 0 & \text{otherwise} \end{cases}$$

---

## 4. Empirical Findings (2023–2025)

Analysis of the 720 observations yields significant insights into the multi-year capacity trajectory.

### 4.1 Macro System Cycle: Peak to Trough
* **Historical Peak:** On **December 20, 2023**, HHS care load reached **11,516 children**, with Total System Load peaking at **11,889 children**.
* **Historical Trough:** On **August 21, 2025**, HHS care load contracted to **1,972 children**, with Total System Load dropping to **2,008 children**.
* **Net Contraction:** Across the 3-year period, the system contracted by **82.9%** from its apex, driven by increased sponsor processing velocities and shifting border demographics.

### 4.2 System Load Distribution Summary

| Metric | Minimum | 25th Percentile | Median | Mean | 75th Percentile | Maximum |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CBP Intake (Daily)** | 0 | 45 | 114 | 148.2 | 228 | 642 |
| **CBP Custody** | 12 | 168 | 344 | 422.6 | 598 | 1,642 |
| **CBP Transferred Out**| 0 | 48 | 108 | 134.5 | 196 | 588 |
| **HHS Care (Shelters)** | 1,972 | 4,215 | 7,654 | 7,128.4 | 9,842 | **11,516** |
| **HHS Discharged** | 0 | 42 | 102 | 131.8 | 192 | 512 |
| **Total System Load** | 2,008 | 4,420 | 8,012 | 7,551.0 | 10,240 | **11,889** |
| **Discharge Offset (DOR)**| 0.00 | 0.88 | 1.01 | 1.04 | 1.18 | 4.50 |

### 4.3 Validation Audit: Intra-day Flow vs. Custody
The pipeline incorporates boundary integrity verification:
1. **Discharges Exceeding HHS Care:** **0 instances** ($0.0\%$). No records report discharges higher than shelter population.
2. **Transfers Exceeding CBP Custody:** **86 instances** ($11.9\%$).
   * *Root Cause Analysis:* These 86 occurrences do not indicate invalid data. Rather, they highlight that CBP transfers reflect rolling 24-hour aggregate outflows, whereas CBP custody represents an instantaneous point-in-time census snapshot. If children were apprehended and transferred on the same calendar day before the custody census was taken, same-day transfers can legitimately exceed end-of-day custody.

---

## 5. Forecasting Methodology & Residual Uncertainty

To support federal operational preparedness, the platform includes a dynamic Ordinary Least Squares (OLS) extrapolation engine with empirical residual standard error ($\sigma_\epsilon$) prediction bands:

$$\hat{y}_{t+h} = \hat{\beta}_0 + \hat{\beta}_1 \cdot (t + h)$$

$$\text{Confidence Band} = \hat{y}_{t+h} \pm 1.5 \cdot \sigma_\epsilon$$

$$\text{where } \sigma_\epsilon = \sqrt{\frac{1}{M - 2} \sum_{i=1}^M \left( y_i - \hat{y}_i \right)^2}$$

* **Lookback Window ($M$):** User-selectable between 14 and 180 observations.
* **Forecast Horizon ($h$):** User-selectable between 7 and 90 days.
* **Automated Weekly Summary:** Projections are dynamically aggregated into calendar-week bins ($W\text{-MON}$) showing projected Mean, Low, and High load bounds for resource planning.

---

## 6. Software Architecture & Implementation

The repository is organized according to modern software engineering standards:

```text
UAC-Care-Load-Analytics/
├── .streamlit/config.toml     # Production theme & typography tokens
├── data/
│   ├── raw/                   # Immutable raw government CSVs
│   └── processed/             # Reproducible cleaned & derived datasets
├── docs/
│   ├── RESEARCH_PAPER.md      # This academic publication
│   ├── UAC_Research_Paper.docx
│   └── UAC_Executive_Summary.docx
├── src/
│   ├── config.py              # Single source of truth for palettes & thresholds
│   ├── pipeline.py            # Clean room ETL & metric transformation engine
│   ├── forecasting.py         # Statistical OLS regression & weekly summaries
│   └── components.py          # Resilient cross-version Streamlit UI components
├── tests/
│   ├── test_pipeline.py       # 6 unit/integration pipeline tests
│   └── test_app.py            # Streamlit headless AppTest integration test
├── clean_data.py              # CLI batch cleaning runner
├── derive_metrics.py          # CLI batch feature engineering runner
├── streamlit_app.py           # Production dashboard entrypoint
├── requirements.txt           # Pinned dependency manifest
└── Dockerfile                 # Container image specification with health checks
```

### 6.1 Automated Verification Suite
All pipeline transformations, aggregations, forecasting fits, and UI components are validated via Python's `unittest` framework:
* `test_clean_raw_dataframe`: Validates schema mapping, thousands separator removal, and date typing.
* `test_derive_metrics`: Validates load conservation ($\text{load} = \text{cbp} + \text{hhs}$) and net flow calculations.
* `test_aggregation`: Validates resampling invariance across daily, weekly, and monthly intervals.
* `test_forecasting`: Validates OLS slope estimation, $R^2$ bounded between 0 and 1, and weekly aggregation.
* `test_app_run_without_exceptions`: Headless Streamlit `AppTest` rendering all tabs without exceptions.

---

## 7. Operational Boundaries & Ethical Considerations

When applying analytics to unaccompanied children, precision in terminology is vital:
1. **Relative Strain vs. Absolute Capacity:** The federal government does not publish licensed bed capacity or facility-specific staffing thresholds in this dataset. Metrics in this study measure **relative historical stress**, not absolute bed deficits.
2. **Missing Reporting Days:** Analysts must avoid zero-filling missing reporting days, which artificially depresses moving averages and creates phantom relief signals.
3. **Child Welfare Primacy:** Analytical models must serve the humane, expeditious, and safe placement of children with vetted sponsors, providing early warning signals to allocate welfare caseworkers ahead of capacity surges.

---

## 8. Conclusion

This study provides an empirical and methodological foundation for analyzing UAC custody and care flows. By disentangling reporting frequencies from calendar time, validating flow balances against institutional realities, and providing a zero-warning, fully tested dashboard, the platform enables transparent, verifiable, and humanitarian-centered operational intelligence.

---

## References

1. U.S. Department of Health and Human Services (HHS), Office of Refugee Resettlement (ORR). *Unaccompanied Children Program Data and Monthly Disclosures (2023–2025)*.
2. U.S. Customs and Border Protection (CBP). *Southwest Border Enforcement Encounters Statistics*.
3. Homeland Security Act of 2002, Pub. L. 107-296, 116 Stat. 2135 (2002).
4. William Wilberforce Trafficking Victims Protection Reauthorization Act of 2008, Pub. L. 110-457, 122 Stat. 5044 (2008).
5. Technical Documentation: *System Capacity & Care Load Analytics for Unaccompanied Children*, Technical Specification Brief, 2026.
