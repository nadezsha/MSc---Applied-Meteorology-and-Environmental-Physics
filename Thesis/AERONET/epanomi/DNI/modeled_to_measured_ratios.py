"""
This script compares **spectral DNI** from libRadtran model outputs
(AERONET–driven Epanomi uvspec runs) with **measured spectral DNI**
from the EKO MS-711 spectroradiometer.

What the script does:
---------------------

1. Reads the measured 1-minute spectral data from:
       sza_calculation_with_integrated_dni.csv
   This file contains:
       - Datetime
       - SZA (solar zenith angle)
       - One column per wavelength (e.g., 300, 301, 302 …)

2. Reads the model spectral DNI from libRadtran OUT files:
       epanomi_YYYY-MM-DD_sza_XXXpX.out
   (Each OUT file corresponds to a specific date + SZA.)

3. For each day:
    • Matches each minute-measurement to its corresponding model OUT file  
      using the date + SZA  
    • Converts model direct_horizontal → spectral DNI  
      using DNI = dir_horiz / cos(SZA)
    • Converts model units to W/m²/nm (if needed)
    • Interpolates the model spectrum onto the instrument wavelengths  
      (typically 400–1100 nm)
    • Computes the ratio:
           DNImodel / DNImeasured
      at each wavelength
    • Averages all measurements of that day to produce a smooth ratio curve

4. Produces one figure per day with:
       x-axis: wavelength (400–1100 nm)
       y-axis: DNImodel / DNImeasured  (dimensionless)

5. Saves all plots to:
       figures_spectral_ratio/
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === USER SETTINGS ===

# Measured EKO data (with Datetime, SZA, and spectral columns, in W/m²/nm)
MEAS_FILE = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\epanomi\eko-ms711-dni-epanomi\2025\sza_calculation\sza_calculation_with_integrated_dni.csv"
)

# Base directory of libRadtran model OUT files (AERONET Epanomi runs)
MODEL_BASE_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\DNI\uvspec_runs"
)

# Output folder for figures (next to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR / "figures_spectral_ratio"
FIG_DIR.mkdir(exist_ok=True)

# Wavelength range for ratio plots (in nm)
WL_MIN = 400.0
WL_MAX = 1100.0

# Name candidates for SZA column in measured data
MEAS_SZA_COLS = ["sza_deg", "SZA", "sza", "solar_zenith"]

# Column name candidates for integrated DNI (for sanity check only)
MEAS_DNI_INT_COLS = ["DNI_integrated_Wm2", "dni_integrated", "dni_int"]

# Units of libRadtran spectral output BEFORE conversion:
#   "W_m2_nm"  -> already W/m²/nm
#   "mW_m2_nm" -> mW/m²/nm, will be divided by 1000
#   "W_m2_um"  -> W/m²/µm, will be divided by 1000 to get per nm
MODEL_UNITS = "mW_m2_nm"   # <-- set this if needed


# === helper functions ===

def choose(colnames, options):
    """Pick first existing column name from 'options' list (case-sensitive)."""
    for name in options:
        if name in colnames:
            return name
    return None


def format_sza_tag(sza_deg: float) -> str:
    """
    Format SZA to match libRadtran OUT file naming:
        83.0  -> '083p0'
        49.7  -> '049p7'
    """
    sza_tenths = int(round(sza_deg * 10.0))
    deg = sza_tenths // 10
    tenth = sza_tenths % 10
    return f"{deg:03d}p{tenth:d}"


# libRadtran OUT reader (4-column version: wl, direct_horiz, diff_dn, diff_up)
COLS_MODEL = [
    "wavelength",
    "direct_horiz",
    "diffuse_down_horiz",
    "diffuse_up_horiz",
]


def read_model_out(fp: Path, skiprows: int = 9) -> pd.DataFrame:
    """
    Read a libRadtran OUT file:
      col0: wavelength (nm)
      col1: direct horizontal
      col2: diffuse down
      col3: diffuse up
    """
    rows = []
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i < skiprows:
                continue
            s = line.strip()
            if not s or s[0] in "#!;":
                continue

            parts = s.split()
            if len(parts) < 4:
                continue
            parts = parts[:4]

            try:
                vals = [float(x) for x in parts]
            except ValueError:
                vals = []
                for x in parts:
                    try:
                        vals.append(float(x))
                    except ValueError:
                        break
                if len(vals) != 4:
                    continue

            rows.append(vals)

    df = pd.DataFrame(rows, columns=COLS_MODEL)
    if not df.empty:
        df = df.sort_values("wavelength").drop_duplicates(
            subset="wavelength", keep="first"
        )
    return df.reset_index(drop=True)


def get_model_spectrum(date_str: str, sza_deg: float) -> pd.DataFrame | None:
    """
    Find and read the model OUT file for a given date (YYYY-MM-DD) and SZA.
    Returns a DataFrame with wavelength + direct_horiz, or None if not found.
    """
    sza_tag = format_sza_tag(sza_deg)
    fname = f"epanomi_{date_str}_sza_{sza_tag}.out"
    fp = MODEL_BASE_DIR / date_str / fname
    if not fp.exists():
        fp_alt = fp.with_suffix(".OUT")
        if fp_alt.exists():
            fp = fp_alt
        else:
            return None

    return read_model_out(fp)


def model_unit_factor_to_W_m2_nm() -> float:
    """
    Conversion factor to bring libRadtran output into W/m²/nm.
    """
    if MODEL_UNITS == "W_m2_nm":
        return 1.0
    elif MODEL_UNITS == "mW_m2_nm":
        return 1e-3  # mW -> W
    elif MODEL_UNITS == "W_m2_um":
        return 1e-3  # per µm -> per nm
    else:
        raise ValueError(f"Unknown MODEL_UNITS: {MODEL_UNITS}")


# === read measured data ===

meas = pd.read_csv(MEAS_FILE)

# Parse datetime and date
if "Datetime" not in meas.columns:
    raise ValueError("Expected a 'Datetime' column in the measured CSV.")

meas["Datetime"] = pd.to_datetime(meas["Datetime"], errors="coerce")
meas["date"] = meas["Datetime"].dt.date.astype("string")

# Find SZA column
meas_sza_col = choose(meas.columns, MEAS_SZA_COLS)
if meas_sza_col is None:
    raise ValueError(
        f"Could not find SZA column. Tried: {MEAS_SZA_COLS}. Found columns: {list(meas.columns)}"
    )

# Identify spectral wavelength columns (numeric names)
wl_cols = []
for col in meas.columns:
    try:
        _ = float(col)
        wl_cols.append(col)
    except ValueError:
        continue

if not wl_cols:
    raise ValueError("No numeric wavelength columns found in measured CSV.")

# Convert to numeric wavelengths and filter by range 400–1100 nm
wl_vals = np.array([float(c) for c in wl_cols])
mask_range = (wl_vals >= WL_MIN) & (wl_vals <= WL_MAX)
wl_vals = wl_vals[mask_range]
wl_cols = [str(int(w)) for w in wl_vals]

print(f"Using {len(wl_cols)} wavelength channels from {wl_vals.min()} to {wl_vals.max()} nm.")

# === UNIT SANITY CHECK (informational only) ===

dni_int_col = choose(meas.columns, MEAS_DNI_INT_COLS)
if dni_int_col is not None:
    step = max(1, len(meas) // 200)
    subset = meas.iloc[::step]
    spec = subset[wl_cols].to_numpy(float)
    spec_int = np.trapezoid(spec, wl_vals, axis=1)  # EKO spectra in W/m²/nm -> W/m²

    dni_raw = subset[dni_int_col].to_numpy(float)
    med_dni = np.nanmedian(dni_raw)
    if med_dni < 5:
        dni_wm2 = dni_raw * 1000.0
        print(f"{dni_int_col} looks like kW/m² (median {med_dni:.3f}); converting to W/m² for check.")
    else:
        dni_wm2 = dni_raw
        print(f"{dni_int_col} looks like W/m² (median {med_dni:.3f}).")

    m = np.isfinite(spec_int) & np.isfinite(dni_wm2) & (spec_int > 0) & (dni_wm2 > 0)
    if m.any():
        ratio = spec_int[m] / dni_wm2[m]
        print(f"Median (∫EKO_spectral dλ) / {dni_int_col}_[W/m²] ≈ {np.nanmedian(ratio):.3f}")
    else:
        print("Not enough valid rows for unit sanity check.")
else:
    print("No integrated DNI column found in measured data; skipping unit sanity check.")

# === group by day and compute DNImodel/DNImeasured ratio vs wavelength ===

model_factor = model_unit_factor_to_W_m2_nm()  # mW → W etc.

all_dates = sorted(meas["date"].unique())

for date_str in all_dates:
    day_df = meas[meas["date"] == date_str].copy()
    if day_df.empty:
        continue

    print(f"\nProcessing date {date_str} with {len(day_df)} rows...")

    ratio_sum = np.zeros_like(wl_vals, dtype=float)
    ratio_count = np.zeros_like(wl_vals, dtype=int)

    for _, row in day_df.iterrows():
        sza_deg = float(row[meas_sza_col])
        if not np.isfinite(sza_deg):
            continue

        model_df = get_model_spectrum(date_str, sza_deg)
        if model_df is None or model_df.empty:
            continue

        theta = math.radians(sza_deg)
        mu0 = math.cos(theta)
        if mu0 <= 1e-6:
            continue

        wl_model = model_df["wavelength"].to_numpy(float)
        direct_horiz = model_df["direct_horiz"].to_numpy(float)

        direct_horiz_W = direct_horiz * model_factor
        dni_model = direct_horiz_W / mu0  # W/m²/nm

        model_interp = np.interp(wl_vals, wl_model, dni_model, left=np.nan, right=np.nan)

        meas_spec = row[wl_cols].to_numpy(dtype=float)  # W/m²/nm

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = model_interp / meas_spec

        m = np.isfinite(ratio)
        ratio_sum[m] += ratio[m]
        ratio_count[m] += 1

    valid = ratio_count > 0
    if not np.any(valid):
        print(f"No valid model/measurement overlap for {date_str}; skipping figure.")
        continue

    ratio_mean = np.full_like(wl_vals, np.nan)
    ratio_mean[valid] = ratio_sum[valid] / ratio_count[valid]

    print(
        f"  {date_str}: median ratio = {np.nanmedian(ratio_mean[valid]):.3f}, "
        f"10th–90th pct = {np.nanpercentile(ratio_mean[valid], [10, 90])}"
    )

    # === PLOT FOR THIS DAY ===
    plt.figure()
    plt.plot(wl_vals[valid], ratio_mean[valid], label=f"{date_str}")
    plt.axhline(1.0, linestyle="--", linewidth=1, label="Perfect agreement")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("DNI_model / DNI_measured")
    plt.title(f"Spectral DNI Ratio (model/measurement) – {date_str} (Epanomi)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    fig_path = FIG_DIR / f"dni_ratio_{date_str}.png"
    plt.savefig(fig_path, dpi=300)
    print(f"Saved figure: {fig_path}")
    plt.close()

print("\nDone. One PNG per day written to:", FIG_DIR)
