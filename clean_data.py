"""
Step 1 — Parse raw HHS UAC export, clean it, and save as cleaned_uac_data.csv

Usage:
    python clean_data.py                  # auto-detects raw CSV in data/raw/ or root
    python clean_data.py my_export.csv    # or point at a specific file
"""

from __future__ import annotations

import glob
import os
import sys
import pandas as pd

from src.pipeline import clean_raw_dataframe

OUTPUT_FILES = {"cleaned_uac_data.csv", "uac_metrics.csv"}


def find_raw_csv() -> str:
    """Find the raw input CSV file."""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if not os.path.exists(path):
            sys.exit(f"ERROR: '{path}' does not exist.")
        return path

    # Check data/raw/ first
    raw_dir_files = glob.glob("data/raw/*.csv")
    if raw_dir_files:
        return raw_dir_files[0]

    # Check root directory (excluding known output files)
    candidates = [
        f for f in glob.glob("*.csv")
        if os.path.basename(f) not in OUTPUT_FILES
    ]
    if not candidates:
        sys.exit(
            "ERROR: no raw HHS CSV found in data/raw/ or working directory.\n"
            "Place the exported CSV in data/raw/, or run: python clean_data.py <path-to-file.csv>"
        )
    return candidates[0]


def main() -> None:
    raw_path = find_raw_csv()
    raw_df = pd.read_csv(raw_path)
    df = clean_raw_dataframe(raw_df)

    print(f"Input file:       {raw_path}")
    print(f"Shape:            {df.shape}")
    print(f"Date range:       {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"Duplicate dates:  {df['date'].duplicated().sum()}")
    full_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    print(f"Calendar days:    {len(full_range)} | Reported rows: {len(df)} "
          f"({len(full_range) - len(df)} non-reporting days)")

    # Save to data/processed and root (for backward compatibility)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/cleaned_uac_data.csv", index=False)
    df.to_csv("cleaned_uac_data.csv", index=False)
    print("\n[OK] data/processed/cleaned_uac_data.csv and cleaned_uac_data.csv written successfully.")


if __name__ == "__main__":
    main()
