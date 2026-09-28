import pandas as pd
import numpy as np

df = pd.read_csv('cleaned_uac_data.csv', parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

# --- Validation flags ---
df['flag_transfer_exceeds_custody'] = df['cbp_transferred_out'] > df['cbp_custody']
df['flag_discharge_exceeds_care'] = df['hhs_discharged'] > df['hhs_care']
df['gap_days'] = df['date'].diff().dt.days

# --- Derived capacity metrics ---
df['total_system_load'] = df['cbp_custody'] + df['hhs_care']
df['net_daily_intake'] = df['cbp_transferred_out'] - df['hhs_discharged']
df['care_load_growth_pct'] = df['hhs_care'].pct_change() * 100
df['total_load_growth_pct'] = df['total_system_load'].pct_change() * 100

# Backlog indicator: sustained positive net intake (rolling sign persistence)
df['net_intake_positive'] = df['net_daily_intake'] > 0
# rolling 7-obs count of positive net intake days (backlog pressure streak)
df['backlog_streak'] = df['net_intake_positive'].groupby((~df['net_intake_positive']).cumsum()).cumcount() + 1
df.loc[~df['net_intake_positive'], 'backlog_streak'] = 0

# Rolling averages (by observation, since reporting isn't strictly daily)
df['hhs_care_roll7'] = df['hhs_care'].rolling(7, min_periods=3).mean()
df['hhs_care_roll14'] = df['hhs_care'].rolling(14, min_periods=5).mean()
df['total_load_roll7'] = df['total_system_load'].rolling(7, min_periods=3).mean()
df['net_intake_roll7'] = df['net_daily_intake'].rolling(7, min_periods=3).mean()

# Volatility: rolling std of hhs_care pct change
df['care_volatility_roll14'] = df['care_load_growth_pct'].rolling(14, min_periods=5).std()

# Discharge offset ratio: discharges / transfers-in (ability to relieve load)
df['discharge_offset_ratio'] = df['hhs_discharged'] / df['cbp_transferred_out'].replace(0, np.nan)

df.to_csv('uac_metrics.csv', index=False)

print("Validation issues:")
print("Transfer > custody:", df['flag_transfer_exceeds_custody'].sum())
print("Discharge > care:", df['flag_discharge_exceeds_care'].sum())
print()
print("Summary stats:")
print(df[['cbp_intake','cbp_custody','cbp_transferred_out','hhs_care','hhs_discharged','total_system_load','net_daily_intake']].describe())
print()
print("Max backlog streak:", df['backlog_streak'].max())
print("Date of max HHS care:", df.loc[df['hhs_care'].idxmax(),'date'], df['hhs_care'].max())
print("Date of min HHS care:", df.loc[df['hhs_care'].idxmin(),'date'], df['hhs_care'].min())
