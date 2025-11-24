"""
Plot spectral model-to-measured ratios for each day & hour.

For each (date, hour):
  - all spectra in that hour are plotted together on one figure
  - x-axis: wavelength [nm]
  - y-axis: ratio = E_model / E_meas (or precomputed column)
  - each timestamp in the hour has a different colour/label
  - a horizontal line at ratio = 1 is drawn for reference

Expected input CSV format (long), e.g. from modeled_to_measured_ratios2.py:
    Datetime,date,SZA_deg,wavelength_nm,E_meas_W_m2_nm,E_model_W_m2_nm,ratio_model_over_meas

Where:
    - Datetime: string parseable by pandas.to_datetime
    - wavelength_nm: float or int
    - E_meas_W_m2_nm: measured spectral irradiance (e.g. MS-711)
    - E_model_W_m2_nm: modeled spectral irradiance (e.g. libRadtran)
    - ratio_model_over_meas: E_model / E_meas (if present, used directly)
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
INPUT_CSV = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\GHI\spectral_meas_model_long.csv"
OUTPUT_DIR = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\GHI\spectral_daily_hourly_ratio_plots"

DATETIME_COL = "Datetime"
WVL_COL = "wavelength_nm"

# Column names from spectral_meas_model_long.csv
MEAS_COL = "E_meas_W_m2_nm"          # measured spectrum
MODEL_COL = "E_model_W_m2_nm"        # modeled spectrum
RATIO_COL = "ratio_model_over_meas"  # model / meas

# Minimum number of distinct timestamps required in an hour to make a plot
MIN_TIMES_PER_HOUR = 1

# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------
print(f"Reading: {INPUT_CSV}")
df = pd.read_csv(INPUT_CSV)

# Parse datetime
df[DATETIME_COL] = pd.to_datetime(df[DATETIME_COL])

# Ensure wavelength is numeric
df[WVL_COL] = pd.to_numeric(df[WVL_COL])

# If ratio column not present, compute it from model / meas
if RATIO_COL not in df.columns:
    if MEAS_COL not in df.columns or MODEL_COL not in df.columns:
        raise ValueError(
            f"No '{RATIO_COL}' column and missing '{MEAS_COL}' or '{MODEL_COL}'. "
            "Provide either the ratio column or both measurement and model columns."
        )
    with np.errstate(divide="ignore", invalid="ignore"):
        df[RATIO_COL] = df[MODEL_COL] / df[MEAS_COL]
    print(f"Computed ratio column '{RATIO_COL}' as {MODEL_COL} / {MEAS_COL}.")
else:
    print(f"Using existing ratio column: {RATIO_COL}")

# Add helper columns for grouping
df["date"] = df[DATETIME_COL].dt.date
df["hour"] = df[DATETIME_COL].dt.hour

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Plots will be saved in: {OUTPUT_DIR}")

# ---------------------------------------------------------------------
# GROUP BY (date, hour) AND PLOT
# ---------------------------------------------------------------------
grouped = df.groupby(["date", "hour"])
n_plots = 0

for (the_date, the_hour), df_hour in grouped:
    # Get distinct timestamps within this hour
    times = df_hour[DATETIME_COL].drop_duplicates().sort_values()
    if len(times) < MIN_TIMES_PER_HOUR:
        continue  # skip if not enough scans

    print(f"Plotting {the_date} hour {the_hour:02d}: {len(times)} spectra")

    plt.figure(figsize=(8, 5))

    # Cycle colours via matplotlib's default cycler
    for t in times:
        df_t = df_hour[df_hour[DATETIME_COL] == t].sort_values(WVL_COL)

        wvl = df_t[WVL_COL].values
        ratio = df_t[RATIO_COL].values

        # label with HH:MM
        label = t.strftime("%H:%M")
        plt.plot(wvl, ratio, label=label, linewidth=1.0)

    # Horizontal reference line at ratio = 1
    plt.axhline(1.0, linestyle="--", linewidth=1.0)

    plt.xlabel("Wavelength [nm]")
    plt.ylabel("Model / Measured GHI (spectral ratio)")
    plt.title(f"Spectral GHI ratios - {the_date} - hour {the_hour:02d}")
    plt.grid(True, alpha=0.3)

    # If many lines, legend can get crowded; you can adjust here as needed
    if len(times) <= 12:
        plt.legend(title="Time", fontsize=8)
    else:
        # For many scans, just show a small legend
        plt.legend(title="Time (subset)", fontsize=6, ncol=2)

    plt.tight_layout()

    # Save figure
    out_name = f"spectral_ratios_{the_date}_H{the_hour:02d}.png"
    out_path = Path(OUTPUT_DIR) / out_name
    plt.savefig(out_path, dpi=200)
    plt.close()

    n_plots += 1

print(f"Done. Generated {n_plots} plot(s).")