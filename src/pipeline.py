"""
ETL Data Pipeline: cleaning, metric derivation, aggregation, and data loading
for the UAC Analytics platform.
"""

from __future__ import annotations

import os
from typing import Tuple
import numpy as np
import pandas as pd

from src.config import NUMERIC_COLS, RAW_COLUMN_MAP


def clean_raw_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw HHS export DataFrame.

    Renames columns, converts dates, strips thousand separators, casts numeric
    columns to floats, drops empty rows, and sorts by date ascending.
    """
    df = raw.dropna(how="all").copy()

    # Map column names
    rename_dict = {}
    for col in df.columns:
        clean_name = RAW_COLUMN_MAP.get(str(col).strip(), None)
        if clean_name:
            rename_dict[col] = clean_name
    if rename_dict:
        df = df.rename(columns=rename_dict)
    elif df.shape[1] >= 6:
        # Fallback to positional mapping if names don't match
        df.columns = ["date", "cbp_intake", "cbp_custody", "cbp_transferred_out",
                      "hhs_care", "hhs_discharged"] + list(df.columns[6:])

    # Parse date
    df["date"] = pd.to_datetime(df["date"], format="%B %d, %Y", errors="coerce")
    if df["date"].isna().all():
        df["date"] = pd.to_datetime(raw.iloc[:, 0], errors="coerce")

    # Clean numeric fields
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Derive operational capacity metrics, streaks, volatility, and validation flags."""
    df = df.sort_values("date").reset_index(drop=True).copy()

    # Validation flags
    df["flag_transfer_exceeds_custody"] = df["cbp_transferred_out"] > df["cbp_custody"]
    df["flag_discharge_exceeds_care"] = df["hhs_discharged"] > df["hhs_care"]
    df["gap_days"] = df["date"].diff().dt.days

    # Derived capacity metrics
    df["total_system_load"] = df["cbp_custody"] + df["hhs_care"]
    df["net_daily_intake"] = df["cbp_transferred_out"] - df["hhs_discharged"]
    df["care_load_growth_pct"] = df["hhs_care"].pct_change() * 100.0
    df["total_load_growth_pct"] = df["total_system_load"].pct_change() * 100.0

    # Backlog streak: consecutive observations where transfers > discharges
    df["net_intake_positive"] = df["net_daily_intake"] > 0
    df["backlog_streak"] = (
        df["net_intake_positive"]
        .groupby((~df["net_intake_positive"]).cumsum())
        .cumcount()
        + 1
    )
    df.loc[~df["net_intake_positive"], "backlog_streak"] = 0

    # Rolling averages (observation-based)
    df["hhs_care_roll7"] = df["hhs_care"].rolling(7, min_periods=3).mean()
    df["hhs_care_roll14"] = df["hhs_care"].rolling(14, min_periods=5).mean()
    df["total_load_roll7"] = df["total_system_load"].rolling(7, min_periods=3).mean()
    df["net_intake_roll7"] = df["net_daily_intake"].rolling(7, min_periods=3).mean()

    # Volatility: 14-observation rolling standard deviation of HHS Care growth %
    df["care_volatility_roll14"] = df["care_load_growth_pct"].rolling(14, min_periods=5).std()

    # Discharge offset ratio: discharges / transfers-in
    df["discharge_offset_ratio"] = df["hhs_discharged"] / df["cbp_transferred_out"].replace(0, np.nan)

    return df


def aggregate_data(df: pd.DataFrame, granularity: str) -> pd.DataFrame:
    """Aggregate daily observation data to Weekly or Monthly cadence safely."""
    if granularity == "Daily":
        return df.copy()

    freq = "W-MON" if granularity == "Weekly" else "MS"
    indexed = df.set_index("date")

    # Resample numeric metrics using mean
    numeric = indexed.resample(freq).mean(numeric_only=True).reset_index()

    # Aggregate boolean flags and streaks using max
    for col in ["backlog_streak", "flag_transfer_exceeds_custody", "flag_discharge_exceeds_care"]:
        if col in indexed.columns:
            resampled = indexed[col].resample(freq).max()
            numeric = numeric.set_index("date")
            numeric[col] = resampled
            numeric = numeric.reset_index()

    return numeric.dropna(subset=["total_system_load"]).reset_index(drop=True)


def resolve_and_load_data() -> Tuple[pd.DataFrame, str]:
    """Find and load UAC dataset from the filesystem in priority order.

    Returns:
        (DataFrame, source_label_str)
    """
    candidate_paths = [
        ("data/processed/uac_metrics.csv", True),
        ("uac_metrics.csv", True),
        ("data/processed/cleaned_uac_data.csv", False),
        ("cleaned_uac_data.csv", False),
    ]

    for path, is_derived in candidate_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["date"])
            if not is_derived:
                df = derive_metrics(df)
            return df, f"Loaded from `{path}`"

    # If no processed data found, look for raw file to clean
    raw_candidates = [
        "data/raw/HHS_Unaccompanied_Alien_Children_Program.csv",
        "HHS_Unaccompanied_Alien_Children_Program.csv",
    ]
    for rpath in raw_candidates:
        if os.path.exists(rpath):
            raw = pd.read_csv(rpath)
            cleaned = clean_raw_dataframe(raw)
            derived = derive_metrics(cleaned)
            return derived, f"Derived live from raw `{rpath}`"

    raise FileNotFoundError(
        "No UAC data found. Please run `python clean_data.py && python derive_metrics.py` "
        "or upload a CSV via the dashboard."
    )
