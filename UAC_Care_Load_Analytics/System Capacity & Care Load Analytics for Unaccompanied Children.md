# System Capacity & Care Load Analytics for Unaccompanied Children

## Project architecture and metric specification

### Executive design decision

The project should be built as a **reproducible analytical pipeline with a separate presentation layer**. The raw CSV must remain immutable. Cleaning, validation, metric calculation, statistical analysis, and dashboard presentation should be separate stages so that every displayed KPI can be traced back to a source record and a documented transformation.

The uploaded technical documentation defines the conceptual pipeline as CBP intake, CBP custody, transfer into HHS care, HHS care, and discharge. It also requires trend analysis, rolling averages, variability analysis, sustained-strain detection, and a Streamlit interface [1].

The source audit identifies three issues that the implementation must handle before analysis:

1. The file contains 1,170 physical records after the header, including 450 fully blank rows.
2. The 720 nonblank observations cover 2023-01-12 through 2025-12-21, but they do not represent every calendar day in that interval.
3. The HHS-care values use comma-formatted thousands separators, such as `2,484`. These values are quoted correctly in the uploaded CSV and must be parsed as integers after removing separators.

These are source-format findings, not invented or imputed dataset values. The dashboard and research paper should report the distinction between **reporting observations** and **calendar days**.

## 1. Conceptual architecture

The system should have five logical layers.

| Layer | Responsibility | Main output |
|---|---|---|
| Raw data | Preserve the uploaded source exactly | Immutable CSV and source metadata |
| Data preparation | Parse, standardize, remove blank records, and create validation flags | Clean observation table |
| Analytical core | Calculate KPIs, rolling features, backlog measures, stress flags, and aggregation tables | Analysis-ready tables |
| Evidence and interpretation | Produce EDA, time-series findings, sensitivity checks, and documented limitations | Figures, tables, research results |
| Presentation | Serve interactive charts and KPI cards in Streamlit | Dashboard |

The dashboard should never contain independent business logic that is absent from the analytical core. It should import prepared tables and functions from `src/`, which prevents the dashboard from silently producing different numbers from the research paper.

A recommended data flow is:

```text
raw CSV + technical documentation
        |
        v
schema mapping and source audit
        |
        v
clean observations + validation flags
        |
        v
canonical time series + derived metrics
        |
        +--> EDA and statistical analysis --> figures and tables --> research paper
        |
        +--> dashboard data layer ------------> Streamlit application
        |
        +--> executive KPI extraction --------> executive summary
```

## 2. Recommended project files

```text
uac-care-load-analytics/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── HHS_Unaccompanied_Alien_Children_Program.csv
│   │   └── TechnicalDocumentation.pdf
│   ├── interim/
│   │   ├── source_audit.csv
│   │   └── validation_flags.csv
│   └── processed/
│       ├── uac_observations_clean.parquet
│       ├── uac_daily_calendar.parquet
│       └── uac_monthly_summary.parquet
├── src/
│   └── uac_analytics/
│       ├── __init__.py
│       ├── config.py
│       ├── schema.py
│       ├── ingest.py
│       ├── clean.py
│       ├── validate.py
│       ├── metrics.py
│       ├── aggregate.py
│       ├── stress.py
│       ├── plots.py
│       └── reporting.py
├── notebooks/
│   ├── 01_source_audit.ipynb
│   ├── 02_data_quality.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_time_series.ipynb
│   └── 05_capacity_stress.ipynb
├── dashboard/
│   ├── app.py
│   ├── components.py
│   └── dashboard_config.toml
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── research_paper.md
│   └── executive_summary.md
├── tests/
│   ├── test_clean.py
│   ├── test_validate.py
│   └── test_metrics.py
└── scripts/
    ├── build_dataset.py
    └── build_reports.py
```

The `data/raw` directory should be treated as read-only. Processed Parquet files are preferable to repeatedly parsing CSV because they preserve types and load efficiently. The notebooks should be used for exploration and interpretation, while reusable transformations belong in `src/`.

## 3. Recommended Python libraries

### Required

- **pandas** for parsing, date handling, reshaping, rolling calculations, and grouped summaries.
- **numpy** for numerical operations and safe division.
- **pyarrow** for typed Parquet storage.
- **pandera** for dataframe schema checks and explicit validation rules.
- **matplotlib** and **seaborn** for publication-oriented static figures.
- **plotly** for interactive dashboard figures.
- **streamlit** for the dashboard.
- **pytest** for formula and data-quality tests.

### Useful, but not mandatory for the first phase

- **statsmodels** for decomposition, autocorrelation, and time-series diagnostics.
- **scipy** for robust statistics and distributional tests.
- **jupyterlab** for exploratory notebooks.
- **ruff** and **black** for linting and consistent formatting.
- **pydantic** if configuration objects and validation settings become complex.

A minimal first implementation can operate with pandas, numpy, pyarrow, pandera, plotly, streamlit, and pytest. Forecasting libraries should not be added until the project explicitly includes forecasting; the current objectives are monitoring, retrospective analysis, and capacity stress identification.

## 4. Workflow from raw data to dashboard

### Stage 1: Ingestion and source audit

Load the source with the Python `csv` reader or pandas while preserving the original file. Record the file name, ingestion timestamp, row count, column names, encoding, and checksum in a source-audit artifact. Remove only fully blank rows in the clean layer and record their count as a validation result; do not delete or overwrite the raw file.

Normalize column names to stable snake-case names, while retaining a mapping to the original labels. Parse comma-formatted numeric strings after removing thousands separators. Parse dates with an explicit format and reject or flag unparseable values rather than coercing them silently.

### Stage 2: Data cleaning and validation

Validate that all six expected fields exist, numeric measures are nonnegative integers, dates are valid, and the date key is unique after blank-row removal. Create a validation table with one row per observation and boolean flags such as `is_blank_record`, `is_invalid_date`, `is_duplicate_date`, `is_negative_value`, `transfers_exceed_cbp_stock`, and `discharges_exceed_hhs_stock`.

The supplied documentation lists `Transfers <= CBP custody` and `Discharges <= HHS care` as checks [1]. These should be treated as **review flags**, not automatic deletion rules, because a same-day flow can exceed an end-of-day stock when the two measures use different timing conventions. Confirm the timing definitions with the data owner if the project will make operational claims.

Create a complete calendar index for time-series display, but do not forward-fill or interpolate custody stocks or flows by default. A missing reporting date means “not observed,” not necessarily zero. Calculations that require consecutive days should either use observed-report intervals explicitly or be restricted to contiguous calendar runs.

### Stage 3: Derived metrics

Calculate metrics in a single tested module. Store both the formula inputs and the resulting metric columns so that the dashboard can explain each KPI.

#### Total System Load

`total_system_load = cbp_custody + hhs_care`

This is a stock measure of children recorded in the two care locations on a reporting date. It should be described as **reported system load**, not as a measure of capacity utilization, because the dataset does not provide facility capacity.

#### Net Daily Intake

`net_daily_intake = transfers_to_hhs - discharges_from_hhs`

Under the requested definition, this is an HHS-care flow balance. Positive values indicate that transfers into HHS exceeded discharges on that reporting date. It is not a complete system-wide net intake measure because it excludes the CBP intake flow and does not model the relationship between beginning and ending stocks.

Use the clearer dashboard label **HHS net flow / care-pressure proxy** alongside the requested technical name.

#### Care Load Growth Rate

`care_load_growth_rate_pct = 100 * (total_system_load_t / total_system_load_(t-1) - 1)`

The first valid observation is missing by definition. If the prior load is zero, return missing rather than infinity. The calculation must be based on the previous valid reporting observation unless the analysis is explicitly restricted to consecutive calendar days. The denominator and the observation interval should be visible in metadata.

#### Rolling averages

Compute 7-observation and 14-observation trailing means for total system load and, separately, for net daily intake. The primary dashboard should use **7-reporting-observation** and **14-reporting-observation** windows because the source is not complete daily data. A calendar-day version may be added only after explicitly handling missing dates.

Use `min_periods` conservatively, such as the full window for headline KPIs, and expose the number of observations in each window. Do not fill missing calendar days with zero.

#### Backlog Indicator

A defensible primary rule is:

`backlog_indicator = 1` when the trailing 7-observation sum of net daily intake is positive **and** at least 4 of the 7 net-intake observations are positive; otherwise `0`.

This combines net accumulation with persistence and avoids classifying one isolated positive day as sustained backlog. The threshold is an analytical convention, not an official operational threshold. Run sensitivity checks using 3-of-5 and 5-of-7 rules and report whether conclusions change.

#### Care Load Volatility Index

Because no official volatility definition is supplied, define the primary index as a rolling, scale-normalized variability measure:

`volatility_index_14 = 100 * std(delta(total_system_load), window=14) / mean(total_system_load, window=14)`

Here, `delta(total_system_load)` is the change from one valid reporting observation to the next. The result is interpretable as typical stock-change variability relative to the average load, expressed as a percentage. Require a full window and return missing when the rolling mean is zero. In the research paper, compare this with the rolling standard deviation of the growth-rate series as a sensitivity measure.

This index measures instability in reported load. It does not measure clinical acuity, staffing risk, or facility performance.

#### Backlog Accumulation Rate

Define the primary measure as the trailing 7-observation mean of net daily intake:

`backlog_accumulation_rate_7 = mean(net_daily_intake over trailing 7 observations)`

The unit is children per reporting observation. Positive values indicate accumulation pressure; negative values indicate net release. As a robustness measure, calculate the slope of cumulative net daily intake over the same window. These two definitions should agree in sign when reporting intervals are regular.

For irregular observation intervals, do not label the result “per day” unless the denominator is adjusted using elapsed calendar days. Use **per reporting observation** or calculate an elapsed-time rate separately.

#### Discharge Offset Ratio

`discharge_offset_ratio = discharges_from_hhs / transfers_to_hhs`

A ratio of 1 means discharges numerically offset transfers during the reporting observation. Values below 1 indicate that discharges were lower than transfers; values above 1 indicate that discharges exceeded transfers. If transfers are zero, return missing when discharges are also zero and flag the case when discharges are positive. This ratio is a flow comparison, not a probability of discharge or an average length of stay.

### Stage 4: Exploratory and time-series analysis

Begin with coverage, missingness, reporting cadence, distributions, and validation flags. Then examine total load, CBP versus HHS composition, transfer and discharge flows, and the relationship between flows and changes in stocks.

Use daily or reporting-observation charts only when the x-axis makes the observation convention clear. Add weekly and monthly summaries, but distinguish calendar aggregation from observation-count aggregation. For monthly totals, sum flows. For monthly custody levels, use an end-of-month value and optionally report the monthly mean. Do not sum stocks across days.

Useful figures include a stacked CBP/HHS load chart, net-flow and discharge/transfer chart, growth-rate chart, rolling-load chart, heatmap of reporting observations by month and weekday, validation-anomaly timeline, and backlog-regime ribbon.

### Stage 5: Capacity stress analysis

The dataset contains no stated CBP or HHS capacity denominators. Therefore, the first version should identify **relative strain**, not claim absolute overcrowding or utilization.

A defensible relative-stress score can combine percentile-based signals:

- total load above its historical 90th percentile;
- positive 7-observation backlog accumulation rate;
- volatility index above its historical 90th percentile;
- discharge offset ratio below 1;
- persistence for at least three consecutive valid observations.

Report each component separately before presenting any composite score. Label the composite **historical relative stress**, and test alternate percentile thresholds. Absolute capacity stress requires external capacity data, such as licensed beds, available beds, staffing levels, or facility-level operating limits.

### Stage 6: Research paper and executive summary

The research paper should include the problem definition, data and limitations, cleaning and validation protocol, metric definitions, EDA, time-series results, relative-stress methodology, sensitivity analysis, findings, and recommendations bounded by the data. It should avoid causal claims because the source is observational and aggregate.

The executive summary should contain the study period, data coverage caveat, current and peak reported load measures, major strain and relief windows, dominant flow-balance patterns, and a short limitations section. All headline numbers should be generated from the same processed table used by the dashboard.

### Stage 7: Streamlit dashboard

The dashboard should contain four pages or tabs:

1. **System load overview:** total load, CBP/HHS composition, rolling averages, and selected date range.
2. **Flow balance and backlog:** transfers, discharges, net daily intake, backlog indicator, accumulation rate, and discharge offset ratio.
3. **Volatility and relative stress:** volatility index, stress components, and flagged windows.
4. **Data quality and methodology:** coverage calendar, missing dates, validation flags, formulas, and limitations.

Provide date-range selection, metric toggles, reporting-observation versus calendar display controls, and a download button for the filtered derived table. Every chart should display a note when the selected period contains missing reporting dates.

## 5. Ambiguities that must be resolved or documented

### What does “daily” mean?

The documentation calls the dataset daily but the uploaded file does not contain every calendar date. The implementation must distinguish a daily reporting measure from a complete daily time series. The initial KPI layer should use reporting observations; calendar-day rates should be a separate, explicitly labeled analysis.

### Are custody values end-of-day stocks?

The column names imply stocks, but the exact observation time is not supplied. Without a common timestamp, flow-versus-stock validation is approximate. This is why transfer and discharge checks should create review flags rather than automatically invalidate records.

### Is net daily intake system-wide or HHS-only?

The requested formula uses HHS transfers and HHS discharges, so it measures HHS flow balance. CBP apprehensions are not included. The project should not call it total-system net intake without adding a separate system-flow model.

### What constitutes “sustained” backlog?

A duration and threshold are not specified. Use the 7-observation, positive-sum, 4-of-7 rule as the primary operationalization and include sensitivity analysis.

### What is the volatility index?

No official formula is supplied. The proposed normalized rolling standard deviation of stock changes is transparent and scale-aware, but it is a project-defined KPI. Publish the formula and compare it with growth-rate volatility.

### What is a capacity threshold?

No capacity denominator or staffing benchmark is present. The project can identify relative historical strain, but it cannot estimate utilization, overcrowding, or absolute capacity breach from this file alone.

### What does “discharge offset” mean?

The natural interpretation is discharges divided by transfers. The direction must be documented because the inverse ratio would answer a different question. Use `discharges / transfers` so values below 1 clearly indicate insufficient offset of incoming HHS flow.

## 6. Testing and reproducibility requirements

Before dashboard development, write unit tests for each metric using small hand-checkable examples. Test zero denominators, first observations, missing dates, blank rows, comma-formatted counts, duplicate dates, negative values, and flow-versus-stock review flags.

The build process should be executable with one command that creates processed data, figures, and report tables from the raw input. Record the software environment and source-file checksum. The dashboard should load a processed artifact rather than run notebooks at startup.

The project should preserve three separate concepts in every output:

- **Observed:** directly present in the source.
- **Derived:** calculated from observed values using a documented formula.
- **Flagged or inferred:** an analytical classification that depends on a project threshold.

This distinction is essential for scientific defensibility and for humanitarian decision-making, where a relative pressure signal must not be presented as a verified capacity breach.

## References

[1]: /home/ubuntu/upload/1790089307374_TechnicalDocumentation.pdf "Technical Documentation: System Capacity & Care Load Analytics for Unaccompanied Children"
