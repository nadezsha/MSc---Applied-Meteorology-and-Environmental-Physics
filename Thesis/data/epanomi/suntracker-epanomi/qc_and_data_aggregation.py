import math
import numpy as np
import pandas as pd

# Parameters
INPUT_FILE = "merged_timeseries_epanomi.csv"
OUTPUT_FILE = "merged_timeseries_epanomi_1min.csv"
DISCARDED_FILE = "discarded_minutes.txt"
TIMESTAMP_COL = "Datetime_UTC"   
BASE_SECONDS = 10                 # 10-sec data
REQUIRED_FRACTION = 0.70          # 70%

# --- Load data ---
df = pd.read_csv(INPUT_FILE)

# Parse datetime
df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL], errors="coerce")
df = df.dropna(subset=[TIMESTAMP_COL])
df = df.sort_values(TIMESTAMP_COL).set_index(TIMESTAMP_COL)

# Numeric columns only
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Expected samples per minute
expected_per_min = 60 // BASE_SECONDS
required_count = math.ceil(REQUIRED_FRACTION * expected_per_min)

# Resample to minute (mean and std)
counts_per_min = df[numeric_cols].resample("1T").count()
means_per_min = df[numeric_cols].resample("1T").mean()
stds_per_min = df[numeric_cols].resample("1T").std()

# Apply QC mask
qc_mask = counts_per_min >= required_count
means_qc = means_per_min.where(qc_mask, other=np.nan)
stds_qc = stds_per_min.where(qc_mask, other=np.nan)

# Rename std columns to avoid collisions
stds_qc = stds_qc.add_suffix("_std")

# Combine mean and std dataframes
result_combined = pd.concat([means_qc, stds_qc], axis=1)

# Identify discarded minutes (all numeric NaN after QC)
discarded_minutes = means_qc[numeric_cols].isna().all(axis=1)
discarded_idx = means_qc.index[discarded_minutes]

# Drop discarded minutes
result = result_combined[~discarded_minutes]

# Save aggregated file
result.to_csv(OUTPUT_FILE)

# Save discarded minutes to txt file
with open(DISCARDED_FILE, "w") as f:
    f.write(f"Total discarded minutes: {len(discarded_idx)}\n")
    for ts in discarded_idx:
        f.write(ts.strftime("%Y-%m-%d %H:%M") + "\n")

# Print summary
print(f"Done. Aggregated data saved to {OUTPUT_FILE}")
print(f"Discarded minutes saved to {DISCARDED_FILE}")
print(f"Kept {len(result)} minutes, discarded {discarded_minutes.sum()} minutes.")