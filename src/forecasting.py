"""
Statistical modeling and linear projection engine with confidence intervals
for the UAC Analytics platform.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd


def ols_fit(x: np.ndarray, y: np.ndarray) -> Optional[Dict[str, Any]]:
    """Fit ordinary least squares linear regression y = slope * x + intercept.

    Returns dict with slope, intercept, R², fitted values, or None if invalid.
    """
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean, y_clean = x[mask], y[mask]
    if len(x_clean) < 3:
        return None

    try:
        slope, intercept = np.polyfit(x_clean, y_clean, 1)
        y_hat = slope * x_clean + intercept
        ss_res = float(np.sum((y_clean - y_hat) ** 2))
        ss_tot = float(np.sum((y_clean - y_clean.mean()) ** 2))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        return {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r2),
            "x": x_clean,
            "y_hat": y_hat,
        }
    except Exception:
        return None


def generate_linear_forecast(
    dates: pd.Series,
    values: pd.Series,
    horizon_days: int = 30,
    lookback_obs: int = 60,
) -> Optional[Dict[str, Any]]:
    """Compute OLS linear extrapolation with residual standard error bands."""
    tail = pd.DataFrame({"date": dates, "value": values}).dropna().tail(lookback_obs)
    if len(tail) < 5:
        return None

    t0 = tail["date"].min()
    x = (tail["date"] - t0).dt.days.to_numpy(dtype=float)
    y = tail["value"].to_numpy(dtype=float)

    fit = ols_fit(x, y)
    if fit is None:
        return None

    resid_std = float(np.std(y - fit["y_hat"], ddof=1)) if len(y) > 2 else 0.0
    last_date = tail["date"].max()

    future_dates = pd.date_range(
        last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D"
    )
    future_x = (future_dates - t0).days.to_numpy(dtype=float)
    future_y = fit["slope"] * future_x + fit["intercept"]

    return {
        "future_dates": future_dates,
        "future_values": future_y,
        "resid_std": resid_std,
        "slope_per_day": fit["slope"],
        "r_squared": fit["r_squared"],
        "history_dates": tail["date"],
        "history_values": tail["value"],
        "fit_dates": tail["date"],
        "fit_values": fit["y_hat"],
    }


def generate_weekly_summary(
    forecast_result: Dict[str, Any], confidence_factor: float = 1.5
) -> pd.DataFrame:
    """Group daily projections into calendar weekly summary table."""
    band = confidence_factor * forecast_result["resid_std"]
    fdf = pd.DataFrame(
        {
            "Date": forecast_result["future_dates"],
            "Forecast": forecast_result["future_values"],
        }
    )
    fdf["Lower Band"] = fdf["Forecast"] - band
    fdf["Upper Band"] = fdf["Forecast"] + band
    fdf["Week"] = fdf["Date"].dt.to_period("W").astype(str)

    weekly = (
        fdf.groupby("Week")
        .agg(
            Start=("Date", "min"),
            End=("Date", "max"),
            Avg_Forecast=("Forecast", "mean"),
            Low=("Lower Band", "min"),
            High=("Upper Band", "max"),
        )
        .reset_index(drop=True)
    )

    weekly["Start"] = weekly["Start"].dt.strftime("%Y-%m-%d")
    weekly["End"] = weekly["End"].dt.strftime("%Y-%m-%d")
    weekly[["Avg_Forecast", "Low", "High"]] = (
        weekly[["Avg_Forecast", "Low", "High"]].round(0).astype(int)
    )
    return weekly
