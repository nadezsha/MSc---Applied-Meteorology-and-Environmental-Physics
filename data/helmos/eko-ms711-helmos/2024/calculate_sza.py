import os
import pandas as pd
import pvlib

LAT = 38.000
LON = 22.183
ELEV_M = 1750
INPUT_CSV = "reshaped_data/all_reshaped_combined.csv"
OUTPUT_DIR = "sza_calculation"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "sza_calculation.csv")

# Read CSV and parse the first column as UTC datetimes
df = pd.read_csv(INPUT_CSV)
time_col = df.columns[0]
df[time_col] = pd.to_datetime(df[time_col], errors="coerce", utc=True)

# Optional: sanity check for unparsable timestamps
n_nat = df[time_col].isna().sum()
if n_nat:
    print(f"Warning: {n_nat} rows had invalid timestamps (NaT).")

# Keep a clean, increasing timeline and contiguous integer index
df = df.sort_values(time_col).reset_index(drop=True)

# Compute solar position
solpos = pvlib.solarposition.get_solarposition(
    time=df[time_col],
    latitude=LAT,
    longitude=LON,
    altitude=ELEV_M,
    pressure=None,       # estimate from altitude
    temperature=12       # mild refraction dependency
)

# Assign by position (avoid index alignment)
df["solar_zenith"] = solpos["apparent_zenith"].to_numpy()   # refraction-corrected
# we can also use geometric:
# df["solar_zenith_geom"] = solpos["zenith"].to_numpy()

# Day of year (1..365/366)
df["doy"] = df[time_col].dt.dayofyear

# (Optional) extras
# df["solar_elevation"] = solpos["apparent_elevation"].to_numpy()
# df["solar_azimuth"] = solpos["azimuth"].to_numpy()

# Save to folder
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False)
print("Saved ->", OUTPUT_CSV)
