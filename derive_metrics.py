"""
Step 2 — Compute derived capacity metrics, streaks, volatility, and validation flags

Usage:
    python derive_metrics.py
"""

from __future__ import annotations

import os
import pandas as pd

from src.pipeline import derive_metrics


def main() -> None:
    # Resolve input path
    candidates = ["data/processed/cleaned_uac_data.csv", "cleaned_uac_data.csv"]
    input_path = None
    for p in candidates:
        if os.path.exists(p):
            input_path = p
            break

    if not input_path:
        raise FileNotFoundError(
            "cleaned_uac_data.csv not found. Please run `python clean_data.py` first."
        )

    df = pd.read_csv(input_path, parse_dates=["date"])
    df = derive_metrics(df)

    # Save to data/processed and root
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/uac_metrics.csv", index=False)
    df.to_csv("uac_metrics.csv", index=False)

    print("Validation checks:")
    print("Transfer > custody flags:", int(df["flag_transfer_exceeds_custody"].sum()))
    print("Discharge > care flags:   ", int(df["flag_discharge_exceeds_care"].sum()))
    print()
    print("Capacity Summary:")
    print(f"Max backlog streak:    {int(df['backlog_streak'].max())} observations")
    max_hhs = df.loc[df["hhs_care"].idxmax()]
    min_hhs = df.loc[df["hhs_care"].idxmin()]
    print(f"Peak HHS care:         {int(max_hhs['hhs_care']):,} on {max_hhs['date'].strftime('%Y-%m-%d')}")
    print(f"Trough HHS care:       {int(min_hhs['hhs_care']):,} on {min_hhs['date'].strftime('%Y-%m-%d')}")
    print("\n[OK] data/processed/uac_metrics.csv and uac_metrics.csv written successfully.")


if __name__ == "__main__":
    main()
