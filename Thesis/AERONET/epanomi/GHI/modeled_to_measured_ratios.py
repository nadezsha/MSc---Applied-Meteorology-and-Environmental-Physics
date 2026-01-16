"""
Compare spectral GHI from libRadtran (AERONET inversion GHI run)
with measured spectral GHI from the EKO MS-711.

For each day:
  - read 1-min EKO spectra (GHI, assumed in mW/m²/nm -> W/m²/nm)
  - read the matching libRadtran OUT file (epanomi_GHI_YYYY-MM-DD_sza_XXXpX.out)
  - compute model spectral GHI = edir*cos(SZA) + edn
  - compute ratio = model / measurement
  - average over all minutes of that day

Outputs:
  - one PNG per day in: figures_spectral_ratio_GHI/
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------------
# USER SETTINGS
# ------------------------------------------------------------------

# Measured EKO GHI data (Datetime, SZA, spectral columns, mW/m²/nm)
MEAS_FILE = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\epanomi\eko-ms711-epanomi\2025\sza_calculation\sza_calculation_with_integrated_ghi.csv"
)

# libRadtran OUT directory (Epanomi)
MODEL_BASE_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\GHI\uvspec_runs_GHI"
)

# Output figures
SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR / "figures_spectral_ratio_GHI"
FIG_DIR.mkdir(exist_ok=True)

# Long-format output (optional)
OUTPUT_SPECTRAL_CSV = SCRIPT_DIR / "epanomi_spectral_meas_model_long.csv"

# Wavelength range
WL_MIN = 400.0
WL_MAX = 1100.0

MEAS_SZA_COLS = ["sza_deg", "SZA", "sza", "solar_zenith"]
MEAS_GHI_INT_COLS = ["GHI_integrated_Wm2", "ghi_integrated", "ghi_int"]

MODEL_UNITS = "mW_m2_nm"
MEAS_UNITS = "mW_m2_nm"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def choose(colnames, options):
    for name in options:
        if name in colnames:
            return name
    return None


def format_sza_tag(sza_deg: float) -> str:
    sza_tenths = int(round(sza_deg * 10.0))
    deg = sza_tenths // 10
    tenth = sza_tenths % 10
    return f"{deg:03d}p{tenth:d}"


COLS_MODEL = ["wavelength", "edir", "edn", "eup"]

def read_model_out(fp: Path, skiprows: int = 9) -> pd.DataFrame:
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
            try:
                rows.append([float(x) for x in parts[:4]])
            except ValueError:
                continue
    df = pd.DataFrame(rows, columns=COLS_MODEL)
    if not df.empty:
        df = df.sort_values("wavelength").drop_duplicates(subset="wavelength")
    return df.reset_index(drop=True)


def get_model_spectrum(date_str: str, sza_deg: float):
    sza_tag = format_sza_tag(sza_deg)
    fname = f"epanomi_GHI_{date_str}_sza_{sza_tag}.out"
    fp = MODEL_BASE_DIR / date_str / fname
    if fp.exists():
        return read_model_out(fp)
    fp_alt = fp.with_suffix(".OUT")
    if fp_alt.exists():
        return read_model_out(fp_alt)
    return None


def unit_factor(units):
    if units == "W_m2_nm":
        return 1.0
    elif units == "mW_m2_nm":
        return 1e-3
    elif units == "W_m2_um":
        return 1e-3
    raise ValueError(f"Unknown unit {units}")


# ------------------------------------------------------------------
# Read measured EKO data
# ------------------------------------------------------------------

meas = pd.read_csv(MEAS_FILE)
meas["Datetime"] = pd.to_datetime(meas["Datetime"], errors="coerce")
meas["date"] = meas["Datetime"].dt.date.astype(str)

meas_sza_col = choose(meas.columns, MEAS_SZA_COLS)
if meas_sza_col is None:
    raise ValueError("No SZA column found in measured file.")

# Detect wavelength columns
wl_cols = []
for col in meas.columns:
    try:
        float(col)
        wl_cols.append(col)
    except:
        pass

if not wl_cols:
    raise ValueError("No numeric wavelength columns found in measured file.")

wl_vals = np.array([float(c) for c in wl_cols])
mask = (wl_vals >= WL_MIN) & (wl_vals <= WL_MAX)
wl_vals = wl_vals[mask]
wl_cols = [str(int(w)) for w in wl_vals]

print(f"Using wavelengths {wl_vals.min()}–{wl_vals.max()} nm")

meas_factor = unit_factor(MEAS_UNITS)
model_factor = unit_factor(MODEL_UNITS)

all_dates = sorted(meas["date"].unique())
spectral_rows = []

# ------------------------------------------------------------------
# MAIN LOOP: day-by-day spectral GHI ratio
# ------------------------------------------------------------------

for date_str in all_dates:
    day_df = meas[meas["date"] == date_str]
    if day_df.empty:
        continue

    print(f"\nProcessing {date_str} with {len(day_df)} rows")

    ratio_sum = np.zeros_like(wl_vals)
    ratio_count = np.zeros_like(wl_vals, int)

    n_matched = 0

    for _, row in day_df.iterrows():
        sza_deg = float(row[meas_sza_col])

        model_df = get_model_spectrum(date_str, sza_deg)
        if model_df is None or model_df.empty:
            continue

        mu0 = math.cos(math.radians(sza_deg))
        if mu0 < 1e-6:
            continue

        wl_model = model_df["wavelength"].to_numpy(float)
        edir = model_df["edir"].to_numpy(float) * model_factor
        edn  = model_df["edn"].to_numpy(float) * model_factor

        ghi_model = edir * mu0 + edn
        ghi_model_interp = np.interp(wl_vals, wl_model, ghi_model, left=np.nan, right=np.nan)

        meas_spec = row[wl_cols].to_numpy(float) * meas_factor

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = ghi_model_interp / meas_spec

        m = np.isfinite(ratio)
        ratio_sum[m] += ratio[m]
        ratio_count[m] += 1
        n_matched += 1

        if m.any():
            dt = row["Datetime"]
            for lam, e_meas, e_mod, r in zip(
                wl_vals[m], meas_spec[m], ghi_model_interp[m], ratio[m]
            ):
                spectral_rows.append(
                    dict(
                        Datetime=dt,
                        date=date_str,
                        SZA_deg=sza_deg,
                        wavelength_nm=lam,
                        E_meas_W_m2_nm=e_meas,
                        E_model_W_m2_nm=e_mod,
                        ratio_model_over_meas=r,
                    )
                )

    print(f"  Matched model spectra: {n_matched}")

    valid = ratio_count > 0
    if not np.any(valid):
        print("  No valid spectral overlaps — skipping figure")
        continue

    ratio_mean = np.full_like(wl_vals, np.nan)
    ratio_mean[valid] = ratio_sum[valid] / ratio_count[valid]

    plt.figure(figsize=(8, 4))
    plt.plot(wl_vals[valid], ratio_mean[valid], label=date_str)
    plt.axhline(1.0, linestyle="--", linewidth=1)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("GHI_model / GHI_measured")
    plt.title(f"Epanomi – spectral GHI ratio ({date_str})")
    plt.grid()
    plt.tight_layout()

    out_fig = FIG_DIR / f"epanomi_GHI_ratio_{date_str}.png"
    plt.savefig(out_fig, dpi=300)
    plt.close()

    print(f"  Saved figure: {out_fig}")


# ------------------------------------------------------------------
# Save long-format file
# ------------------------------------------------------------------

if spectral_rows:
    df_long = pd.DataFrame(spectral_rows)
    df_long.to_csv(OUTPUT_SPECTRAL_CSV, index=False)
    print(f"\nSaved long-format spectral file:\n  {OUTPUT_SPECTRAL_CSV}")
else:
    print("\nNo spectral rows collected.")


print("\nDone. Figures written to:", FIG_DIR)
