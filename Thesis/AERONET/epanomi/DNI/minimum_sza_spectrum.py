"""
Compare spectral DNI at minimum mid-morning SZA (≈10–10:30 UTC) between
EKO MS-711 and libRadtran (AERONET inversion DNI runs).

For each day:
- From the EKO file, select rows for that date.
- Restrict to times between 10:00 and 10:30 UTC.
- Within that window, find the row with the smallest SZA.
  (If the window is empty, fall back to the overall minimum SZA of the day.)
- Find the libRadtran OUT file for the same date with the closest SZA.
  Filenames are assumed like: epanomi_YYYY-MM-DD_sza_083p0.out
- Read spectral DNI from both:
    * EKO: spectral DNI in columns (one per wavelength)
    * libRadtran: edir column (direct normal) vs wavelength
- Convert both from mW/m²/nm to W/m²/nm (if needed).
- Interpolate the libRadtran spectrum to EKO wavelengths.
- Plot:
    * Top panel: EKO and libRadtran spectra
    * Bottom panel: ratio = libRadtran / EKO

Outputs
-------
- One PNG per day: dni_minSZA_YYYY-MM-DD.png
- A small CSV summary listing chosen times, SZAs and matched OUT files.

Notes
-----
- This assumes your EKO CSV has:
    * 'Datetime' column parsable with pandas.to_datetime()
    * 'solar_zenith' column with solar zenith angle in degrees
    * Many spectral columns, whose names contain the wavelength in nm
      (e.g. '350', 'nm_350', etc.).
- It also assumes libRadtran OUT files contain at least two numeric columns:
    wavelength_nm, edir_mW_m2_nm (plus optional extras we ignore).
- Units: we treat both as mW/m²/nm and convert to W/m²/nm by dividing by 1000.
"""

import math
import re
from datetime import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple

# ================================================================
# USER SETTINGS
# ================================================================

# Measured EKO DNI data (with Datetime, solar_zenith, spectral columns in mW/m²/nm)
MEAS_FILE = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\epanomi\eko-ms711-dni-epanomi\2025\sza_calculation\sza_calculation_with_integrated_dni.csv"
)

# Directory with libRadtran DNI OUT files for AERONET inversions
MODEL_OUT_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\DNI\uvspec_runs"
)

# Save figures inside: .../DNI/figures_min_sza
OUT_FIG_DIR = MODEL_OUT_DIR.parent / "figures_min_sza"

# Save CSV inside: .../DNI/
SUMMARY_CSV = MODEL_OUT_DIR.parent / "dni_minSZA_daily_summary_epanomi.csv"

# Wavelength range to analyze [nm]
WL_MIN = 350.0
WL_MAX = 1100.0

# Time window around local minimum SZA (assumed UTC in the file)
WINDOW_START = time(10, 0, 0)   # 10:00 UTC
WINDOW_END   = time(10, 30, 0)  # 10:30 UTC

# Whether EKO and libRadtran spectra are in mW/m²/nm (True) or already W/m²/nm (False)
SPECTRA_IN_MW = True

# Site name for figure titles
SITE_NAME = "Thessaloniki" # Epanomi not available


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def parse_wavelength_from_col(col_name: str):
    """
    Try to extract a numeric wavelength (in nm) from a column name.

    Examples:
        '350' -> 350.0
        'nm_400' -> 400.0
        'E_500.5' -> 500.5

    Returns float or None if no number found.
    """
    # Direct float attempt
    try:
        return float(col_name)
    except ValueError:
        pass

    # Find first number in the string
    m = re.search(r"(\d+(\.\d+)?)", col_name)
    if m:
        return float(m.group(1))
    return None


def find_spectral_columns(df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
    """
    From a DataFrame, find columns that look like spectral data (wavelengths in nm),
    restricted to [WL_MIN, WL_MAX].

    Returns:
        spectral_cols_sorted: list of column names sorted by wavelength ascending.
        wavelengths_sorted:   np.array of corresponding wavelengths in nm.
    """
    wl_map = {}
    for col in df.columns:
        wl = parse_wavelength_from_col(col)
        if wl is not None and (WL_MIN <= wl <= WL_MAX):
            wl_map[col] = wl

    if not wl_map:
        raise RuntimeError("No spectral columns detected in MEAS_FILE within the specified wavelength range.")

    # Sort by wavelength
    items = sorted(wl_map.items(), key=lambda x: x[1])
    spectral_cols_sorted = [c for c, _ in items]
    wavelengths_sorted = np.array([w for _, w in items], dtype=float)
    return spectral_cols_sorted, wavelengths_sorted


def read_uvspec_out_edir(path: Path) -> pd.DataFrame:
    """
    Read a libRadtran OUT file and return a DataFrame with columns:
        'wavelength_nm', 'edir_mW_m2_nm'

    Assumes:
    - File contains numeric data in whitespace-separated columns.
    - First column is wavelength [nm].
    - Second column is edir [mW/m²/nm].
    - Lines beginning with '#' are comments.
    """
    df = pd.read_csv(
        path,
        delim_whitespace=True,
        comment="#",
        header=None,
        engine="python"
    )

    if df.shape[1] < 2:
        raise RuntimeError(f"Unexpected format in {path}; expected at least 2 columns.")

    df = df.iloc[:, :2].copy()
    df.columns = ["wavelength_nm", "edir_mW_m2_nm"]
    return df


def scan_model_files(model_dir: Path) -> List[Dict]:
    """
    Scan MODEL_OUT_DIR (recursively) for files like:
        <something>_YYYY-MM-DD_sza_083p0.out

    Returns a list of dicts with keys: 'date', 'sza_deg', 'path'.
    """
    entries = []
    pattern = re.compile(r".*_(\d{4}-\d{2}-\d{2})_sza_(\d{3})p(\d)\.out$", re.IGNORECASE)

    # 🔧 changed glob -> rglob so we also search subfolders like 2025-04-22
    for path in model_dir.rglob("*.out"):
        m = pattern.match(path.name)
        if not m:
            continue
        date_str = m.group(1)
        sza_int = int(m.group(2))  # e.g. 015
        sza_dec = int(m.group(3))  # e.g. 0
        sza_deg = float(sza_int) + 0.1 * float(sza_dec)
        entries.append({
            "date": pd.to_datetime(date_str).date(),
            "sza_deg": sza_deg,
            "path": path,
        })
    return entries


def choose_closest_model_file(model_entries: List[Dict], date, sza_target: float):
    """
    Given all model entries and a date, choose the entry with that date and
    SZA on a 0.5° grid closest to sza_target. Returns dict or None if none for that date.
    """
    same_day = [e for e in model_entries if e["date"] == date]
    if not same_day:
        return None

    # Round measurement SZA to nearest 0.5°
    sza_rounded = round(sza_target * 2) / 2.0

    # Look for an exact match on that rounded grid
    candidates = [e for e in same_day if abs(e["sza_deg"] - sza_rounded) < 1e-6]
    if not candidates:
        print(f"  No model SZA = {sza_rounded:.1f}° available for {date}; skipping this day.")
        return None

    # If multiple (shouldn't happen), just take the first
    return candidates[0]



# ================================================================
# MAIN
# ================================================================

def main():
    OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading EKO measurement file: {MEAS_FILE}")
    df_meas = pd.read_csv(MEAS_FILE)
    if "Datetime" not in df_meas.columns:
        raise RuntimeError("MEAS_FILE must contain a 'Datetime' column.")

    df_meas["Datetime"] = pd.to_datetime(df_meas["Datetime"])
    if "solar_zenith" not in df_meas.columns:
        raise RuntimeError("MEAS_FILE must contain a 'solar_zenith' column (degrees).")

    # Find spectral columns and their wavelengths
    spectral_cols, wl_meas = find_spectral_columns(df_meas)
    print(f"Detected {len(spectral_cols)} spectral columns from {wl_meas[0]:.1f} to {wl_meas[-1]:.1f} nm.")

    # Add date and time columns for grouping/filtering
    df_meas["date"] = df_meas["Datetime"].dt.date
    df_meas["time"] = df_meas["Datetime"].dt.time

    # Scan model files once
    print(f"Scanning libRadtran OUT files in: {MODEL_OUT_DIR}")
    model_entries = scan_model_files(MODEL_OUT_DIR)
    if not model_entries:
        raise RuntimeError(f"No matching .out files found in {MODEL_OUT_DIR}.")

    print(f"Found {len(model_entries)} model OUT files.")

    # Prepare summary storage
    summary_rows = []

    # Loop over days in the measurement file
    for date_val, day_df in df_meas.groupby("date"):
        print(f"\nProcessing date {date_val} ...")

        # Restrict to 10:00–10:30 UTC
        mask_window = day_df["time"].between(WINDOW_START, WINDOW_END)
        window_df = day_df[mask_window]

        if not window_df.empty:
            # Use the minimum SZA within the time window
            idx_min = window_df["solar_zenith"].idxmin()
            chosen = df_meas.loc[idx_min]
            window_used = True
        else:
            # Fallback: minimum SZA over the whole day
            idx_min = day_df["solar_zenith"].idxmin()
            chosen = df_meas.loc[idx_min]
            window_used = False
            print(f"  No data in {WINDOW_START}-{WINDOW_END} UTC; using minimum SZA of the day instead.")

        dt_chosen = chosen["Datetime"]
        sza_meas = float(chosen["solar_zenith"])
        print(f"  Chosen EKO row at {dt_chosen} with SZA = {sza_meas:.2f}°")

        # Select the spectral measurements for that row
        meas_vals = chosen[spectral_cols].astype(float).to_numpy()
        if SPECTRA_IN_MW:
            meas_vals_W = meas_vals / 1000.0
        else:
            meas_vals_W = meas_vals

        # Choose closest model OUT file for this day and SZA
        model_entry = choose_closest_model_file(model_entries, date_val, sza_meas)
        if model_entry is None:
            print(f"  WARNING: No model file found for date {date_val}; skipping this day.")
            continue

        model_path = model_entry["path"]
        sza_model = float(model_entry["sza_deg"])
        print(f"  Matched model file: {model_path.name} (SZA = {sza_model:.2f}°)")

        # Read model spectrum
        df_model = read_uvspec_out_edir(model_path)
        wl_model = df_model["wavelength_nm"].to_numpy(dtype=float)
        edir_model_mW = df_model["edir_mW_m2_nm"].to_numpy(dtype=float)

        # Interpolate model to EKO wavelengths
        edir_interp_mW = np.interp(wl_meas, wl_model, edir_model_mW)
        if SPECTRA_IN_MW:
            edir_interp_W = edir_interp_mW / 1000.0
        else:
            edir_interp_W = edir_interp_W

        # Compute ratio (model / measurement)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(meas_vals_W > 0, edir_interp_W / meas_vals_W, np.nan)

        # ============ Plotting ============

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))

        ax1.plot(wl_meas, meas_vals_W, label="EKO DNI")
        ax1.plot(wl_meas, edir_interp_W, label="libRadtran DNI", linestyle="--")
        ax1.set_ylabel("Spectral DNI [W m⁻² nm⁻¹]")
        title = (
            f"{SITE_NAME} {date_val}  "
            f"EKO SZA = {sza_meas:.1f}°, model SZA = {sza_model:.1f}°\n"
            f"EKO time = {dt_chosen.strftime('%H:%M:%S')} UTC"
        )
        ax1.set_title(title)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(wl_meas, ratio)
        ax2.axhline(1.0, linestyle="--")
        ax2.set_xlabel("Wavelength [nm]")
        ax2.set_ylabel("Model / Measurement")
        ax2.grid(True, alpha=0.3)

        fig.tight_layout()

        out_png = OUT_FIG_DIR / f"dni_minSZA_{date_val}.png"
        fig.savefig(out_png, dpi=200)
        plt.close(fig)

        print(f"  Saved figure: {out_png}")

        # Save summary row
        summary_rows.append({
            "date": date_val,
            "eko_datetime_utc": dt_chosen,
            "eko_sza_deg": sza_meas,
            "window_used_10_1030": window_used,
            "model_file": model_path.name,
            "model_sza_deg": sza_model,
            "n_wavelengths": len(wl_meas),
        })

    # Save summary CSV
    if summary_rows:
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_csv(SUMMARY_CSV, index=False)
        print(f"\nWrote summary CSV: {SUMMARY_CSV}")
    else:
        print("\nNo days processed; no summary CSV written.")


if __name__ == "__main__":
    main()
