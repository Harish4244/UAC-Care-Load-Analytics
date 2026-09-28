"""
Step 1 — Parse a raw HHS UAC export, clean it, and save as cleaned_uac_data.csv

Usage:
    python clean_data.py                  # auto-detects the raw CSV in this folder
    python clean_data.py my_export.csv    # or point at a specific file

Why auto-detect instead of a fixed filename: browsers rename repeat
downloads ("file.csv", "file (1).csv", "file (2).csv", ...), so hardcoding
one exact name breaks the moment a new export is downloaded. This script
instead looks for the one CSV in the folder that isn't already one of this
pipeline's own outputs.
"""
import glob
import os
import sys

import pandas as pd

OUTPUT_FILES = {"cleaned_uac_data.csv", "uac_metrics.csv"}


def find_raw_csv() -> str:
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if not os.path.exists(path):
            sys.exit(f"ERROR: '{path}' does not exist.")
        return path

    candidates = [f for f in glob.glob("*.csv") if os.path.basename(f) not in OUTPUT_FILES]
    if not candidates:
        sys.exit(
            "ERROR: no raw HHS CSV found in the working directory.\n"
            "Place the exported CSV here, or run: python clean_data.py <path-to-file.csv>"
        )
    if len(candidates) > 1:
        sys.exit(
            "ERROR: multiple candidate CSV files found: "
            f"{candidates}\nRun this script with the file to use, e.g.:\n"
            f'    python clean_data.py "{candidates[0]}"'
        )
    return candidates[0]


def main() -> None:
    raw_path = find_raw_csv()
    df = pd.read_csv(raw_path)
    df = df.dropna(how="all").copy()
    df.columns = ["date", "cbp_intake", "cbp_custody", "cbp_transferred_out",
                   "hhs_care", "hhs_discharged"]

    df["date"] = pd.to_datetime(df["date"], format="%B %d, %Y")

    for c in ["cbp_intake", "cbp_custody", "cbp_transferred_out",
              "hhs_care", "hhs_discharged"]:
        df[c] = df[c].astype(str).str.replace(",", "", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)

    print(f"Input file:  {raw_path}")
    print(f"Shape:       {df.shape}")
    print(f"Date range:  {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"Duplicate dates: {df['date'].duplicated().sum()}")
    full_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    print(f"Calendar days in range: {len(full_range)} | Reported rows: {len(df)} "
          f"({len(full_range) - len(df)} non-reporting days)")
    print(df["date"].dt.day_name().value_counts().to_string())

    df.to_csv("cleaned_uac_data.csv", index=False)
    print("\n[OK] cleaned_uac_data.csv written successfully.")


if __name__ == "__main__":
    main()
