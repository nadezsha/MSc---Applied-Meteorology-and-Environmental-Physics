import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
INPUT_TXT = "20241105_20241105_Helmos_NTUA.lev15"   # your file
OUTPUT_CSV = "aeronet_aod_400_1100nm_interp.csv"
target_nm = np.arange(400, 1101, 1)   # 400..1100 nm
target_um = target_nm / 1000.0        # µm
MISSING = -999.0

# ---------------------------------------------------------------------
# 1. find the line with the table header
# ---------------------------------------------------------------------
def find_header_line(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.startswith("Date("):
                return i
    raise RuntimeError("Could not find 'Date(' line in file.")

header_line = find_header_line(INPUT_TXT)

# ---------------------------------------------------------------------
# 2. read data
# ---------------------------------------------------------------------
df = pd.read_csv(
    INPUT_TXT,
    skiprows=header_line,
    na_values=[MISSING, -999, -999.000000],
)

df["Datetime_UTC"] = pd.to_datetime(
    df["Date(dd:mm:yyyy)"] + " " + df["Time(hh:mm:ss)"],
    format="%d:%m:%Y %H:%M:%S",
    utc=True,
    errors="coerce",
)

# ---------------------------------------------------------------------
# 3. pick wavelength + AOD columns
# ---------------------------------------------------------------------
# raw exact-wavelength columns
raw_exact_cols = [c for c in df.columns if c.startswith("Exact_Wavelengths_of_AOD(um)_")]

# keep only those that actually end with a number + "nm"
exact_cols = []
for c in raw_exact_cols:
    tail = c.split("_")[-1]  # e.g. "1020nm" or "Empty"
    if tail.endswith("nm"):
        num_part = tail.replace("nm", "")
        if num_part.isdigit():
            exact_cols.append(c)

# AOD columns
aod_cols = [c for c in df.columns if c.startswith("AOD_") and c.endswith("nm")]

def sort_by_wl(cols):
    def get_wl(c):
        return int(c.split("_")[-1].replace("nm", ""))
    return sorted(cols, key=get_wl)

exact_cols = sort_by_wl(exact_cols)
aod_cols = sort_by_wl(aod_cols)

if len(exact_cols) != len(aod_cols):
    raise ValueError(
        f"Mismatch: {len(exact_cols)} exact-wavelength columns vs {len(aod_cols)} AOD columns.\n"
        f"exact: {exact_cols}\nAOD: {aod_cols}"
    )

# ---------------------------------------------------------------------
# 4. interpolate row by row
# ---------------------------------------------------------------------
records = []

for _, row in df.iterrows():
    wl_um = row[exact_cols].to_numpy(dtype=float)
    aod_vals = row[aod_cols].to_numpy(dtype=float)

    # remove NaNs
    mask = (~np.isnan(wl_um)) & (~np.isnan(aod_vals))
    wl_um = wl_um[mask]
    aod_vals = aod_vals[mask]

    if wl_um.size < 2:
        # not enough to interpolate, skip this timestamp
        continue

    # sort by wavelength
    order = np.argsort(wl_um)
    wl_um = wl_um[order]
    aod_vals = aod_vals[order]

    # interpolate to 0.4–1.1 µm
    interp = np.interp(
        x=target_um,
        xp=wl_um,
        fp=aod_vals,
        left=np.nan,
        right=np.nan,
    )

    rec = {"Datetime_UTC": row["Datetime_UTC"]}
    for nm, val in zip(target_nm, interp):
        rec[f"AOD_{nm}nm"] = val
    records.append(rec)

# ---------------------------------------------------------------------
# 5. save
# ---------------------------------------------------------------------
out_df = pd.DataFrame(records)
out_df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved {len(out_df)} rows to {OUTPUT_CSV}")
