"""
Compare spectral GHI from libRadtran (AERONET inversion GHI run)
with measured spectral GHI from the EKO MS-711.

For each day:
  - read 1-min EKO spectra (GHI, assumed in mW/m²/nm -> converted to W/m²/nm)
  - read the matching libRadtran OUT file for each Date + SZA
    (helmos_GHI_YYYY-MM-DD_sza_XXXpX.out)
  - compute model spectral GHI = edir * cos(SZA) + edn  (W/m²/nm)
  - compute ratio GHI_model / GHI_measured at each wavelength
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

# Measured EKO GHI data (Datetime, SZA, spectral cols, **mW/m²/nm**)
MEAS_FILE = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\helmos\eko-ms711-helmos\2024\sza_calculation\sza_calculation_with_integrated_ghi.csv"
)

# Base directory of libRadtran GHI OUT files
# structure:  ...\GHI\uvspec_runs_GHI\2024-11-05\helmos_GHI_2024-11-05_sza_083p0.out
MODEL_BASE_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\GHI\uvspec_runs_GHI"
)

# Output folder for figures (next to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR / "figures_spectral_ratio_GHI"
FIG_DIR.mkdir(exist_ok=True)

# Extra output: long-format spectral file (one row per Datetime–wavelength)
OUTPUT_SPECTRAL_CSV = SCRIPT_DIR / "spectral_meas_model_long.csv"

# Wavelength range for ratio plots (in nm)
WL_MIN = 400.0
WL_MAX = 1100.0

# Name candidates for SZA column in measured data
MEAS_SZA_COLS = ["sza_deg", "SZA", "sza", "solar_zenith"]

# Column name candidates for integrated GHI (sanity check only)
MEAS_GHI_INT_COLS = ["GHI_integrated_Wm2", "ghi_integrated", "ghi_int"]

# Units of libRadtran spectral output before conversion:
#   "W_m2_nm"  -> already W/m²/nm
#   "mW_m2_nm" -> mW/m²/nm, will be divided by 1000
#   "W_m2_um"  -> W/m²/µm, will be divided by 1000 to get per nm
MODEL_UNITS = "mW_m2_nm"

# Units of EKO spectra before conversion:
# (from your sanity check, they behave like mW/m²/nm)
MEAS_UNITS = "mW_m2_nm"


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def choose(colnames, options):
    """Pick first existing column name from a list of candidates."""
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


# GHI run OUT reader (lambda edir edn eup)
COLS_MODEL = [
    "wavelength",
    "edir",   # direct normal spectral
    "edn",    # diffuse down
    "eup",    # diffuse up
]


def read_model_out(fp: Path, skiprows: int = 9) -> pd.DataFrame:
    """
    Read a libRadtran OUT file: wl  edir  edn  eup
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
    File name pattern:
        helmos_GHI_YYYY-MM-DD_sza_XXXpX.out
    """
    sza_tag = format_sza_tag(sza_deg)
    fname = f"helmos_GHI_{date_str}_sza_{sza_tag}.out"
    fp = MODEL_BASE_DIR / date_str / fname
    if not fp.exists():
        fp_alt = fp.with_suffix(".OUT")
        if fp_alt.exists():
            fp = fp_alt
        else:
            # debug: uncomment if you want to see missing combinations
            # print(f"Model file not found for {date_str}, SZA={sza_deg:.1f} -> {fname}")
            return None
    return read_model_out(fp)


def model_unit_factor_to_W_m2_nm() -> float:
    """Conversion factor for libRadtran to W/m²/nm."""
    if MODEL_UNITS == "W_m2_nm":
        return 1.0
    elif MODEL_UNITS == "mW_m2_nm":
        return 1e-3
    elif MODEL_UNITS == "W_m2_um":
        return 1e-3
    else:
        raise ValueError(f"Unknown MODEL_UNITS: {MODEL_UNITS}")


def meas_unit_factor_to_W_m2_nm() -> float:
    """Conversion factor for EKO spectra to W/m²/nm."""
    if MEAS_UNITS == "W_m2_nm":
        return 1.0
    elif MEAS_UNITS == "mW_m2_nm":
        return 1e-3
    else:
        raise ValueError(f"Unknown MEAS_UNITS: {MEAS_UNITS}")


# ------------------------------------------------------------------
# Read measured data
# ------------------------------------------------------------------

meas = pd.read_csv(MEAS_FILE)

if "Datetime" not in meas.columns:
    raise ValueError("Expected a 'Datetime' column in the measured CSV.")

meas["Datetime"] = pd.to_datetime(meas["Datetime"], errors="coerce")
meas["date"] = meas["Datetime"].dt.date.astype("string")

meas_sza_col = choose(meas.columns, MEAS_SZA_COLS)
if meas_sza_col is None:
    raise ValueError(
        f"Could not find SZA column. Tried: {MEAS_SZA_COLS}. Found columns: {list(meas.columns)}"
    )

# numeric wavelength columns
wl_cols = []
for col in meas.columns:
    try:
        _ = float(col)
        wl_cols.append(col)
    except ValueError:
        continue

if not wl_cols:
    raise ValueError("No numeric wavelength columns found in measured CSV.")

wl_vals = np.array([float(c) for c in wl_cols])
mask_range = (wl_vals >= WL_MIN) & (wl_vals <= WL_MAX)
wl_vals = wl_vals[mask_range]
wl_cols = [str(int(w)) for w in wl_vals]

print(f"Using {len(wl_cols)} wavelength channels from {wl_vals.min()} to {wl_vals.max()} nm.")

meas_factor = meas_unit_factor_to_W_m2_nm()

# ------------------------------------------------------------------
# Unit sanity check using integrated GHI column
# ------------------------------------------------------------------

ghi_int_col = choose(meas.columns, MEAS_GHI_INT_COLS)
if ghi_int_col is not None:
    step = max(1, len(meas) // 200)
    subset = meas.iloc[::step]
    spec = subset[wl_cols].to_numpy(float) * meas_factor  # -> W/m²/nm
    spec_int = np.trapezoid(spec, wl_vals, axis=1)        # -> W/m²

    ghi_raw = subset[ghi_int_col].to_numpy(float)
    med_ghi = np.nanmedian(ghi_raw)
    if med_ghi < 5:
        ghi_wm2 = ghi_raw * 1000.0
        print(f"{ghi_int_col} looks like kW/m² (median {med_ghi:.3f}); converting to W/m² for check.")
    else:
        ghi_wm2 = ghi_raw
        print(f"{ghi_int_col} looks like W/m² (median {med_ghi:.3f}).")

    m = np.isfinite(spec_int) & np.isfinite(ghi_wm2) & (spec_int > 0) & (ghi_wm2 > 0)
    if m.any():
        ratio_int = spec_int[m] / ghi_wm2[m]
        print(f"Median (∫EKO_spectral dλ) / {ghi_int_col}_[W/m²] ≈ {np.nanmedian(ratio_int):.3f}")
    else:
        print("Not enough valid rows for unit sanity check.")
else:
    print("No integrated GHI column found in measured data; skipping unit sanity check.")

# ------------------------------------------------------------------
# Group by day and compute GHI_model / GHI_measured ratio vs wavelength
# ------------------------------------------------------------------

model_factor = model_unit_factor_to_W_m2_nm()
all_dates = sorted(meas["date"].unique())

# Collect all spectral samples here (one row per Datetime–wavelength)
spectral_rows = []  # type: list[dict]

for date_str in all_dates:
    day_df = meas[meas["date"] == date_str].copy()
    if day_df.empty:
        continue

    print(f"\nProcessing date {date_str} with {len(day_df)} rows...")

    ratio_sum = np.zeros_like(wl_vals, dtype=float)
    ratio_count = np.zeros_like(wl_vals, dtype=int)

    n_matched_rows = 0

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
        edir = model_df["edir"].to_numpy(float)
        edn  = model_df["edn"].to_numpy(float)

        # model: -> W/m²/nm
        edir_W = edir * model_factor
        edn_W  = edn  * model_factor

        # spectral GHI = edir * cos(SZA) + edn
        ghi_model = edir_W * mu0 + edn_W  # W/m²/nm

        # interpolate model onto instrument wavelengths
        model_interp = np.interp(wl_vals, wl_model, ghi_model, left=np.nan, right=np.nan)

        # measured spectra -> W/m²/nm
        meas_spec = row[wl_cols].to_numpy(dtype=float) * meas_factor

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = model_interp / meas_spec  # GHI_model / GHI_measured

        m = np.isfinite(ratio)
        ratio_sum[m] += ratio[m]
        ratio_count[m] += 1
        n_matched_rows += 1

        # ----------------------------------------------------------
        # Store full spectra for this timestamp in long format
        # ----------------------------------------------------------
        if m.any():
            dt = row["Datetime"]
            for lam, e_meas, e_model, r in zip(
                wl_vals[m], meas_spec[m], model_interp[m], ratio[m]
            ):
                spectral_rows.append(
                    {
                        "Datetime": dt,
                        "date": date_str,
                        "SZA_deg": sza_deg,
                        "wavelength_nm": float(lam),
                        "E_meas_W_m2_nm": float(e_meas),
                        "E_model_W_m2_nm": float(e_model),
                        "ratio_model_over_meas": float(r),
                    }
                )

    print(f"  Matched {n_matched_rows} measurement rows to model files.")

    valid = ratio_count > 0
    if not np.any(valid):
        print(f"  No valid model/measurement overlap for {date_str}; skipping figure.")
        continue

    ratio_mean = np.full_like(wl_vals, np.nan)
    ratio_mean[valid] = ratio_sum[valid] / ratio_count[valid]

    print(
        f"  {date_str}: median ratio = {np.nanmedian(ratio_mean[valid]):.3f}, "
        f"10th–90th pct = {np.nanpercentile(ratio_mean[valid], [10, 90])}"
    )

    plt.figure()
    plt.plot(wl_vals[valid], ratio_mean[valid], label=f"{date_str}")
    plt.axhline(1.0, linestyle="--", linewidth=1, label="Perfect agreement")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("GHI_model / GHI_measured")
    plt.title(f"Spectral GHI Ratio (model/measurement) – {date_str}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    fig_path = FIG_DIR / f"ghi_ratio_{date_str}.png"
    plt.savefig(fig_path, dpi=300)
    print(f"  Saved figure: {fig_path}")
    plt.close()

# ------------------------------------------------------------------
# Save long-format spectral file (for per-hour/per-day plots)
# ------------------------------------------------------------------
print(f"\nTotal spectral rows collected: {len(spectral_rows)}")
if spectral_rows:
    df_long = pd.DataFrame(spectral_rows)
    df_long.sort_values(["Datetime", "wavelength_nm"], inplace=True)
    df_long.to_csv(OUTPUT_SPECTRAL_CSV, index=False)
    print("\nSaved long spectral file with model, measurement and ratio:")
    print(" ", OUTPUT_SPECTRAL_CSV)
else:
    print("\nNo spectral rows collected; long spectral CSV not written.")

print("\nDone. One PNG per day written to:", FIG_DIR)
