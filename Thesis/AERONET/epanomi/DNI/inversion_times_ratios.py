"""
Compare spectral Direct Normal Irradiance (DNI) from libRadtran
(AERONET inversion–based uvspec runs)
with measured spectral DNI from the EKO MS-711 spectroradiometer.

This script **only evaluates times when AERONET inversions exist**.
For each AERONET inversion timestamp, it selects:
  (1) the **closest EKO measurement** (within MAX_TIME_DIFF_MIN minutes),
  (2) the **closest libRadtran model file** based on SZA
      (within MAX_SZA_DIFF_DEG degrees).

Processing steps
----------------
For each date:
  • Load the minute-resolution EKO spectral DNI file
    (spectral columns in mW/m²/nm → converted to W/m²/nm).
  • Load the corresponding AERONET inversion file (.lev15) and extract all
    inversion timestamps.
  • For each inversion timestamp:
       - find the closest EKO measurement
       - find the libRadtran OUT file with the closest SZA
       - interpolate the model spectrum to the EKO wavelength grid
       - compute ratio = DNI_model / DNI_measured
       - save a figure for this single inversion time
  • If multiple inversion times exist for the day:
       - save a second figure overlaying **all inversion curves**
         (semi-transparent)
       - compute the **daily mean** of all ratios
       - save a daily-mean figure

Wavelengths
-----------
Numeric EKO spectral columns are automatically detected.  
Only wavelengths ≥350 nm are used (e.g. 350–1100 nm).

Inputs
------
MEAS_FILE:
    Spectral DNI measurements (EKO MS-711), including:
      - Datetime column (UTC or local, tz-naive)
      - solar_zenith (degrees)
      - spectral columns in mW/m²/nm

MODEL_OUT_DIR:
    Directory containing libRadtran OUT files produced for each SZA.
    Supports nested directories (e.g. uvspec_runs/YYYY-mm-dd/*.out)

AERONET_INV_DIR:
    AERONET almucantar inversion files (.lev15),
    filenames like YYYYMMDD_YYYYMMDD_Thessaloniki.lev15

Outputs
-------
For each date:
    epanomi_YYYY-mm-dd_HHMM_dni_ratio_inversion_closest.png
        → model/measured spectral ratio for each inversion time

    epanomi_YYYY-mm-dd_all_inversions_dni_ratio_inversion_closest.png
        → all inversion times plotted together

    epanomi_YYYY-mm-dd_daily_mean_dni_ratio_inversion_closest.png
        → daily mean spectral ratio
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple
import re

# ================================================================
# USER SETTINGS
# ================================================================

MEAS_FILE = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\epanomi\eko-ms711-dni-epanomi\2025\sza_calculation\sza_calculation_with_integrated_dni.csv"
)

MODEL_OUT_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\DNI\uvspec_runs"
)

AERONET_INV_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\DNI\AERONET_inversions_data\all_data"
)

# Adjust this to match your AERONET inversion filenames, e.g.
# 20250422_20250422_Thessaloniki.lev15 → SITE_TAG = "Thessaloniki"
SITE_TAG = "Thessaloniki"

# Max allowed time difference between inversion time and EKO time (minutes)
MAX_TIME_DIFF_MIN = 5.0

# Max allowed SZA difference between EKO SZA and chosen model SZA (degrees)
MAX_SZA_DIFF_DEG = 0.4

OUT_FIG_DIR = Path(
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\DNI\figures_inversion_times"
)
OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)


# ================================================================
# Helper functions
# ================================================================

def find_wavelength_columns(df: pd.DataFrame, min_nm: float = 350.0):
    """
    Return wavelength columns (numeric column names) sorted ascending,
    but only those >= min_nm (default: 350 nm).
    """
    wl_cols = []
    wl_vals = []

    for col in df.columns:
        try:
            wl = float(col)
            if wl >= min_nm:
                wl_cols.append(col)
                wl_vals.append(wl)
        except ValueError:
            continue

    if not wl_cols:
        raise ValueError(f"No numeric wavelength columns >= {min_nm} nm found in EKO file.")

    wl_vals = np.array(wl_vals)
    sort_idx = np.argsort(wl_vals)
    wl_vals_sorted = wl_vals[sort_idx]
    wl_cols_sorted = [wl_cols[i] for i in sort_idx]

    return wl_vals_sorted, wl_cols_sorted


def parse_uvspec_out(path: Path) -> pd.DataFrame:
    data_rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not (line[0].isdigit() or line[0] == '.'):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                wvl = float(parts[0])
                edir = float(parts[1])
                edn = float(parts[2])
                eup = float(parts[3])
            except ValueError:
                continue
            data_rows.append((wvl, edir, edn, eup))
    if not data_rows:
        raise ValueError(f"No numeric data found in uvspec OUT file: {path}")
    df = pd.DataFrame(data_rows, columns=["wavelength_nm", "edir_mW", "edn_mW", "eup_mW"])
    return df


def build_model_map() -> Dict[pd.Timestamp, List[Tuple[float, Path]]]:
    """
    Scan MODEL_OUT_DIR (recursively) and build:
        { date_normalized : [(sza_deg, path), ...] }

    Works for structures like:
      uvspec_runs/
        2025-04-22/
          epanomi_2025-04-22_sza_015p0.out
          epanomi_2025-04-22_sza_016p0.out
          ...
    """
    mapping: Dict[pd.Timestamp, List[Tuple[float, Path]]] = {}

    print(f"Debug: MODEL_OUT_DIR = {MODEL_OUT_DIR}")
    print(f"Debug: MODEL_OUT_DIR exists? {MODEL_OUT_DIR.exists()}")

    files = [f for f in MODEL_OUT_DIR.rglob("*") if f.is_file() and f.suffix.lower() == ".out"]
    print(f"Debug: found {len(files)} *.out files under {MODEL_OUT_DIR}")

    date_re = re.compile(r"(\d{4}-\d{2}-\d{2})")
    sza_re  = re.compile(r"sza_([0-9]{3}p[0-9])", re.IGNORECASE)

    n_parsed = 0
    for f in files:
        stem = f.stem  # epanomi_2025-04-22_sza_015p0
        m_date = date_re.search(stem)
        m_sza  = sza_re.search(stem)
        if not m_date or not m_sza:
            print(f"  Debug: could not parse date/SZA from '{f.name}', skipping.")
            continue

        date_str = m_date.group(1)
        sza_tag  = m_sza.group(1)

        try:
            date = pd.to_datetime(date_str).normalize()
            sza_deg = float(sza_tag.replace("p", "."))
        except Exception as e:
            print(f"  Debug: failed to convert '{f.name}' -> date/SZA ({e}), skipping.")
            continue

        mapping.setdefault(date, []).append((sza_deg, f))
        n_parsed += 1

    print(f"Debug: successfully parsed {n_parsed} model files into {len(mapping)} dates.")
    return mapping


def find_model_file_for_row(date_ts: pd.Timestamp,
                            sza_deg: float,
                            model_map: Dict[pd.Timestamp, List[Tuple[float, Path]]]
                            ) -> Path:
    """
    Choose the model OUT file with SZA closest to sza_deg for that date.
    Require difference <= MAX_SZA_DIFF_DEG.
    """
    date_key = pd.to_datetime(date_ts).normalize()
    if date_key not in model_map:
        raise FileNotFoundError(f"No model files for date {date_key.date()}")

    candidates = model_map[date_key]
    sza_vals = np.array([c[0] for c in candidates])
    idx = int(np.argmin(np.abs(sza_vals - sza_deg)))
    best_sza, best_path = candidates[idx]
    diff = abs(best_sza - sza_deg)
    if diff > MAX_SZA_DIFF_DEG:
        raise FileNotFoundError(
            f"No model SZA within {MAX_SZA_DIFF_DEG}° of {sza_deg:.2f}° "
            f"(closest is {best_sza:.2f}°)"
        )
    return best_path


def read_aeronet_inversion_times(inv_file: Path) -> List[pd.Timestamp]:
    """Return list of timestamps for which inversions exist (SSA or AOD inversion)."""
    header_line = None
    with open(inv_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "Date(dd:mm:yyyy)" in line and "Time(hh:mm:ss)" in line:
                header_line = i
                break

    if header_line is None:
        raise ValueError(f"Could not find data header in AERONET file: {inv_file}")

    df = pd.read_csv(inv_file, skiprows=header_line)

    date_col = [c for c in df.columns if c.startswith("Date")][0]
    time_col = [c for c in df.columns if c.startswith("Time")][0]

    dt_str = df[date_col].astype(str) + " " + df[time_col].astype(str)
    dt = pd.to_datetime(dt_str, format="%d:%m:%Y %H:%M:%S", errors="coerce")
    dt = dt.dt.tz_localize(None)
    dt = dt.dropna()
    return sorted(dt.unique())


def build_aeronet_file_map() -> Dict[pd.Timestamp, Path]:
    """
    Map each date to its AERONET inversion file (AOD .lev15 or SSA .ssa).

    Works with filenames like:
      20250422_20250422_Thessaloniki.lev15
      20250423_20250423_Thessaloniki.lev15
    """
    mapping: Dict[pd.Timestamp, Path] = {}

    for f in AERONET_INV_DIR.glob(f"*_{SITE_TAG}.*"):
        if f.suffix.lower() not in [".lev15", ".ssa"]:
            continue
        try:
            ymd = f.name[:8]
            date = pd.to_datetime(ymd, format="%Y%m%d")
            mapping[date.normalize()] = f
        except Exception:
            continue

    print(f"Debug: AERONET_INV_DIR = {AERONET_INV_DIR}")
    print(f"Debug: found {len(mapping)} inversion files (lev15/ssa).")
    return mapping


# ================================================================
# Main processing
# ================================================================

def main():
    df_meas = pd.read_csv(MEAS_FILE)
    if "Datetime" not in df_meas.columns:
        raise ValueError("EKO file must have a 'Datetime' column.")
    if "solar_zenith" not in df_meas.columns:
        raise ValueError("EKO file must have a 'solar_zenith' column (degrees).")

    df_meas["Datetime"] = pd.to_datetime(df_meas["Datetime"])
    df_meas["Datetime"] = df_meas["Datetime"].dt.tz_localize(None)

    df_meas["date"] = df_meas["Datetime"].dt.date
    df_meas["date_ts"] = pd.to_datetime(df_meas["date"])

    wl_nm, wl_cols = find_wavelength_columns(df_meas)
    print(f"Using {len(wl_nm)} wavelength channels from {wl_nm.min()} to {wl_nm.max()} nm.")

    # mW → W
    df_meas[wl_cols] = df_meas[wl_cols] / 1000.0

    aeronet_map = build_aeronet_file_map()
    print(f"Found {len(aeronet_map)} AERONET inversion files.")

    model_map = build_model_map()
    print(f"Found model files for {len(model_map)} dates in MODEL_OUT_DIR.")

    for date_val, df_day in df_meas.groupby("date_ts"):
        date_norm = pd.to_datetime(date_val).normalize()
        date_str = date_norm.strftime("%Y-%m-%d")

        if date_norm not in aeronet_map:
            print(f"[{date_str}] No AERONET inversion file found, skipping.")
            continue
        if date_norm not in model_map:
            print(f"[{date_str}] No model files found in MODEL_OUT_DIR, skipping.")
            continue

        inv_file = aeronet_map[date_norm]
        print(f"[{date_str}] Using AERONET inversion file: {inv_file.name}")

        inv_times = read_aeronet_inversion_times(inv_file)
        if not inv_times:
            print(f"[{date_str}] No inversion times found in AERONET file, skipping.")
            continue

        df_day = df_day.copy()

        used_indices = []
        for t in inv_times:
            mask_same_day = df_day["Datetime"].dt.date == t.date()
            df_same = df_day[mask_same_day]
            if df_same.empty:
                continue
            deltas = (df_same["Datetime"] - t).abs()
            i_min = deltas.idxmin()
            min_delta = deltas.min()
            if pd.isna(min_delta):
                continue
            min_minutes = abs(min_delta.total_seconds()) / 60.0
            if min_minutes <= MAX_TIME_DIFF_MIN:
                used_indices.append(i_min)

        used_indices = sorted(set(used_indices))
        if not used_indices:
            print(f"[{date_str}] No EKO rows within {MAX_TIME_DIFF_MIN} min of inversion times, skipping.")
            continue

        df_sel = df_day.loc[used_indices].copy()
        print(f"[{date_str}] {len(df_sel)} EKO rows matched to inversion times (≤ {MAX_TIME_DIFF_MIN} min).")

        all_ratio_curves = []
        all_labels = []

        for idx, row in df_sel.iterrows():
            dt = row["Datetime"]
            sza_deg = float(row["solar_zenith"])
            time_str = dt.strftime("%H%M")

            try:
                model_path = find_model_file_for_row(date_norm, sza_deg, model_map)
            except FileNotFoundError as e:
                print(f"  {dt} | {e}")
                continue

            df_model = parse_uvspec_out(model_path)

            dni_model_W = (
                np.interp(wl_nm, df_model["wavelength_nm"], df_model["edir_mW"])
                / 1000.0
            )

            dni_meas_W = row[wl_cols].to_numpy(dtype=float)

            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = dni_model_W / dni_meas_W
                ratio[~np.isfinite(ratio)] = np.nan

            all_ratio_curves.append(ratio)
            all_labels.append(dt.strftime("%H:%M"))

            plt.figure(figsize=(8, 4))
            plt.plot(wl_nm, ratio)
            plt.axhline(1.0, linestyle="--")
            plt.xlabel("Wavelength [nm]")
            plt.ylabel("DNI_model / DNI_meas [-]")
            plt.title(f"Epanomi {date_str} {dt.strftime('%H:%M')} (closest inversion + model SZA)")
            plt.grid(True)

            fig_name = OUT_FIG_DIR / f"epanomi_{date_str}_{time_str}_dni_ratio_inversion_closest.png"
            plt.tight_layout()
            plt.savefig(fig_name, dpi=150)
            plt.close()

            print(f"  Saved figure for {dt.strftime('%H:%M')}: {fig_name}")

        if all_ratio_curves:
            all_ratio_arr = np.vstack(all_ratio_curves)

            # ---------- overlay of all inversion times ----------
            plt.figure(figsize=(8, 4))
            for label, curve in zip(all_labels, all_ratio_curves):
                plt.plot(wl_nm, curve)
            plt.axhline(1.0, linestyle="--")
            plt.xlabel("Wavelength [nm]")
            plt.ylabel("DNI_model / DNI_meas [-]")
            plt.title(f"Epanomi {date_str} – all inversion times (closest EKO + model SZA)")
            plt.grid(True)

            if len(all_labels) <= 15:
                plt.legend(all_labels, fontsize=7, ncol=2)

            overlay_name = OUT_FIG_DIR / f"epanomi_{date_str}_all_inversions_dni_ratio_inversion_closest.png"
            plt.tight_layout()
            plt.savefig(overlay_name, dpi=150)
            plt.close()

            print(f"[{date_str}] Saved all-inversions overlay figure: {overlay_name}")

            # ---------- daily mean ----------
            daily_mean = np.nanmean(all_ratio_arr, axis=0)

            plt.figure(figsize=(8, 4))
            plt.plot(wl_nm, daily_mean)
            plt.axhline(1.0, linestyle="--")
            plt.xlabel("Wavelength [nm]")
            plt.ylabel("Mean DNI_model / DNI_meas [-]")
            plt.title(f"Epanomi {date_str} mean over inversion times (closest EKO + model SZA)")
            plt.grid(True)

            daily_fig_name = OUT_FIG_DIR / f"epanomi_{date_str}_daily_mean_dni_ratio_inversion_closest.png"
            plt.tight_layout()
            plt.savefig(daily_fig_name, dpi=150)
            plt.close()

            print(f"[{date_str}] Saved daily mean DNI figure: {daily_fig_name}")


if __name__ == "__main__":
    main()
