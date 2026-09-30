from pathlib import Path
import csv
import pandas as pd

script_dir = Path(__file__).resolve().parent
candidates = [
    script_dir / "HHS_Unaccompanied_Alien_Children_Program.csv",
    script_dir.parent / "data" / "raw" / "HHS_Unaccompanied_Alien_Children_Program.csv",
    Path("HHS_Unaccompanied_Alien_Children_Program.csv"),
]
path = next((p for p in candidates if p.exists()), script_dir / "HHS_Unaccompanied_Alien_Children_Program.csv")
print('file_bytes', path.stat().st_size)
with path.open(newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))
print('raw_csv_rows_including_header', len(rows))
print('raw_header', rows[0])
print('raw_field_counts', sorted({len(r) for r in rows[1:]}))
print('first_raw_row', rows[1])
print('date_samples', [r[0] for r in rows[1:8]])

header = rows[0]
records = []
for i, row in enumerate(rows[1:], start=2):
    if len(row) != len(header):
        raise ValueError(f'Unexpected field count at CSV line {i}: {len(row)}')
    records.append(row)

df = pd.DataFrame(records, columns=header)
df['Date'] = pd.to_datetime(df['Date'], format='%B %d, %Y', errors='coerce')
for c in header[1:]:
    df[c] = (df[c].astype('string').str.replace(',', '', regex=False).str.strip())
    df[c] = pd.to_numeric(df[c], errors='coerce')
print('parsed_rows', len(df))
print('date_min', df['Date'].min())
print('date_max', df['Date'].max())
print('invalid_dates', int(df['Date'].isna().sum()))
print('invalid_date_samples', [r[0] for r in records if pd.isna(pd.to_datetime(r[0], format='%B %d, %Y', errors='coerce'))][:8])
print('duplicate_dates', int(df['Date'].duplicated().sum()))
print('missing_values', df.isna().sum().to_dict())
print('negative_values', {c: int((df[c] < 0).sum()) for c in header[1:]})
print('transfers_gt_cbp_custody', int((df[header[3]] > df[header[2]]).sum()))
print('discharges_gt_hhs_care', int((df[header[5]] > df[header[4]]).sum()))
full = pd.date_range(df['Date'].min(), df['Date'].max(), freq='D')
print('calendar_days', len(full))
print('missing_calendar_dates', len(full.difference(df['Date'])))
print('observed_weekday_counts', df['Date'].dt.day_name().value_counts().sort_index().to_dict())
print('duplicate_header_names', [x for x in set(header) if header.count(x) > 1])
