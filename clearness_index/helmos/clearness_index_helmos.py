"""
Clearness index calculator for Helmos data.

What it does
------------
- Loads all CSVs found in the given GHI and DNI directories.
- Merges on 'Datetime' (minute resolution).
- Computes observed DHI = GHI - DNI * cos(SZA).
- Loads theoretical (libradtran) CSV keyed by SZA (degrees).
- Interpolates theoretical GHI, DHI, and DNI to each observed SZA.
- Computes clearness indices: Kt_GHI, Kt_DHI, Kt_DNI.
- Saves a tidy CSV with all inputs + outputs.

Notes
-----
- Angles: SZA is expected in degrees in input; we convert to radians for cos().
- Negative DHI results are clipped to 0 (common practice when small numeric mismatches occur).
- The script looks for corrected theoretical columns if present; otherwise falls back.

Outputs
-------
CSV:
  C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\clearness_index\helmos\helmos_clearness_indices_per_minute.csv
Plots (PNG) 
  Kt_GHI_timeseries.png
  Kt_DHI_timeseries.png
  Kt_DNI_timeseries.png
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === INPUTS ===
GHI_DIR = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\helmos\eko-ms711-helmos\2024\sza_calculation"
DNI_DIR = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\helmos\eko-ms711-dni-helmos\2024\sza_calculation"
THEO_CSV = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\helmos_model\intergrated_data\integrated_irradiance_by_sza_ecc_corrected.csv"

# === OUTPUTS ===
OUT_DIR = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\clearness_index\helmos")
FIG_DIR = OUT_DIR / "figures"
OUT_CSV = OUT_DIR / "helmos_clearness_indices_per_minute.csv"
PLOT_FILES = {
    "Kt_GHI": FIG_DIR / "Kt_GHI_timeseries.png",
    "Kt_DHI": FIG_DIR / "Kt_DHI_timeseries.png",
    "Kt_DNI": FIG_DIR / "Kt_DNI_timeseries.png",
}

# === Helper: find likely column by keywords ===
def find_col(columns, *keywords, default=None):
    cols_lower = {c.lower(): c for c in columns}
    for cl, orig in cols_lower.items():
        if all(k in cl for k in keywords):
            return orig
    return default

def load_and_prepare_obs(folder, mode="ghi"):
    folder = Path(folder)
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")

    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

    # Standardize key columns
    dt_col = find_col(df.columns, "datetime", default="Datetime")
    if dt_col not in df.columns:
        raise KeyError(f"Could not find a 'Datetime' column in {folder}")

    sza_col = (
        find_col(df.columns, "solar", "zenith")
        or find_col(df.columns, "sza")
        or "solar_zenith"
    )
    if sza_col not in df.columns:
        raise KeyError(f"Could not find a solar zenith column (e.g., 'solar_zenith' or 'sza') in {folder}")

    if mode == "ghi":
        val_col = (
            find_col(df.columns, "ghi", "integrated")
            or find_col(df.columns, "global", "horiz")
            or "GHI_integrated_Wm2"
        )
        if val_col not in df.columns:
            raise KeyError(f"Could not find a GHI column in {folder}")
        out = df[[dt_col, sza_col, val_col]].copy()
        out.columns = ["Datetime", "solar_zenith_deg", "GHI_Wm2"]
    elif mode == "dni":
        val_col = (
            find_col(df.columns, "dni", "integrated")
            or find_col(df.columns, "dni")
            or "DNI_integrated_Wm2"
        )
        if val_col not in df.columns:
            raise KeyError(f"Could not find a DNI column in {folder}")
        out = df[[dt_col, sza_col, val_col]].copy()
        out.columns = ["Datetime", "solar_zenith_deg", "DNI_Wm2"]
    else:
        raise ValueError("mode must be 'ghi' or 'dni'")

    # Parse datetime, sort, drop duplicates
    out["Datetime"] = pd.to_datetime(out["Datetime"])
    out = out.sort_values("Datetime").drop_duplicates(subset=["Datetime"])
    return out

def load_theoretical(csv_path):
    theo = pd.read_csv(csv_path)

    # Base SZA column
    sza_col = (
        find_col(theo.columns, "sza", "deg")
        or find_col(theo.columns, "sza")
        or "sza_deg"
    )
    if sza_col not in theo.columns:
        raise KeyError("Could not find 'sza_deg' column in theoretical CSV")

    # Prefer corrected columns if present
    ghi_cols_pref = ["total_global_horiz_corr", "total_global_horiz"]
    dhi_cols_pref = ["total_diffuse_down_horiz_corr", "total_diffuse_down_horiz"]
    dni_cols_pref = ["dni_reconstructed_corr", "dni_reconstructed"]

    def pick(cols_pref):
        for c in cols_pref:
            if c in theo.columns:
                return c
        raise KeyError(f"Could not find any of these columns in theoretical CSV: {cols_pref}")

    ghi_col = pick(ghi_cols_pref)
    dhi_col = pick(dhi_cols_pref)
    dni_col = pick(dni_cols_pref)

    theo_small = theo[[sza_col, ghi_col, dhi_col, dni_col]].copy()
    theo_small.columns = ["sza_deg", "GHI_theo_Wm2", "DHI_theo_Wm2", "DNI_theo_Wm2"]

    #  Convert from mW/m² to W/m²
    theo_small["GHI_theo_Wm2"] = theo_small["GHI_theo_Wm2"].astype(float) / 1000.0
    theo_small["DHI_theo_Wm2"] = theo_small["DHI_theo_Wm2"].astype(float) / 1000.0
    theo_small["DNI_theo_Wm2"] = theo_small["DNI_theo_Wm2"].astype(float) / 1000.0

    theo_small = theo_small.sort_values("sza_deg").dropna()

    return theo_small

def interpolate_theoretical_at_sza(theo_df, sza_deg_array):
    # Guard against out-of-range SZA by clipping to available domain
    sza_grid = theo_df["sza_deg"].to_numpy()
    ghi_grid = theo_df["GHI_theo_Wm2"].to_numpy()
    dhi_grid = theo_df["DHI_theo_Wm2"].to_numpy()
    dni_grid = theo_df["DNI_theo_Wm2"].to_numpy()

    sza_min, sza_max = np.nanmin(sza_grid), np.nanmax(sza_grid)
    sza_q = np.clip(sza_deg_array, sza_min, sza_max)

    ghi_q = np.interp(sza_q, sza_grid, ghi_grid)
    dhi_q = np.interp(sza_q, sza_grid, dhi_grid)
    dni_q = np.interp(sza_q, sza_grid, dni_grid)

    return ghi_q, dhi_q, dni_q

def safe_div(a, b):
    out = np.full_like(a, np.nan, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b) & (b > 0)
    out[mask] = a[mask] / b[mask]
    return out

def plot_timeseries(df, col, out_path, ylim=None):
    # Simple minute-resolution time series; no style/colors specified.
    fig, ax = plt.subplots(figsize=(12, 4))

    # Drop NaNs for plotting to ensure a visible line
    to_plot = df[["Datetime", col]].dropna()
    ax.plot(to_plot["Datetime"], to_plot[col])

    ax.set_title(f"{col} time series")
    ax.set_xlabel("Time")
    ax.set_ylabel(col)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    fig.autofmt_xdate()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def main():
    ghi_obs = load_and_prepare_obs(GHI_DIR, mode="ghi")
    dni_obs = load_and_prepare_obs(DNI_DIR, mode="dni")

    df = pd.merge(ghi_obs, dni_obs[["Datetime", "DNI_Wm2"]], on="Datetime", how="inner")

    cosz = np.cos(np.deg2rad(df["solar_zenith_deg"].astype(float))).clip(lower=0)
    df["DHI_obs_Wm2"] = (df["GHI_Wm2"] - df["DNI_Wm2"] * cosz).clip(lower=0)

    theo = load_theoretical(THEO_CSV)
    ghi_theo, dhi_theo, dni_theo = interpolate_theoretical_at_sza(theo, df["solar_zenith_deg"].to_numpy())
    df["GHI_theo_Wm2"] = ghi_theo
    df["DHI_theo_Wm2"] = dhi_theo
    df["DNI_theo_Wm2"] = dni_theo

    df["Kt_GHI"] = safe_div(df["GHI_Wm2"].to_numpy(), df["GHI_theo_Wm2"].to_numpy())
    df["Kt_DHI"] = safe_div(df["DHI_obs_Wm2"].to_numpy(), df["DHI_theo_Wm2"].to_numpy())
    df["Kt_DNI"] = safe_div(df["DNI_Wm2"].to_numpy(), df["DNI_theo_Wm2"].to_numpy())

    # Optional: keep only daytime (cosZ > 0) rows
    mask_day = cosz > 0
    if mask_day.any():
        df = df.loc[mask_day].copy()

    cols = [
        "Datetime", "solar_zenith_deg",
        "GHI_Wm2", "DNI_Wm2", "DHI_obs_Wm2",
        "GHI_theo_Wm2", "DHI_theo_Wm2", "DNI_theo_Wm2",
        "Kt_GHI", "Kt_DHI", "Kt_DNI"
    ]
    df = df[cols].sort_values("Datetime")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    # Save figures in separate folder
    for col, path in PLOT_FILES.items():
        # Let y-limits auto-scale for visibility
        plot_timeseries(df, col, path, ylim=None)

if __name__ == "__main__":
    main()