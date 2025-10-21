# integrate_libradtran_by_sza.py
# Integrates libRadtran spectra per file (per SZA) to get totals:
# - total_direct_horizontal (DNI * cos(SZA))
# - total_diffuse_down_horizontal (DHI)
# - total_diffuse_up_horizontal
# - total_global_horizontal (GHI = DirH + DiffDn)
# Also reconstructs DNI and checks GHI = DHI + DNI*cos(SZA)

from pathlib import Path
import re
import numpy as np
import pandas as pd

# === USER SETTINGS ===
INPUT_DIR = Path(r"c:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\helmos_model\outputs")
FILE_GLOB = "typical_profile_sza_*.OUT"

OUT_DIR = INPUT_DIR.parent / "intergrated_data"  
OUT_DIR.mkdir(exist_ok=True)                      
OUT_CSV = OUT_DIR / "integrated_irradiance_by_sza.csv"


# column names 
COLS = [
    "wavelength",
    "direct_horiz",          # DNI * cos(SZA)
    "diffuse_down_horiz",    # DHI
    "diffuse_up_horiz",
    "uavg_direct",
    "uavg_diffuse_down",
    "uavg_diffuse_up",
]

# extract SZA from filenames 
SZA_RE = re.compile(r"sza_([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)


def robust_read(fp: Path, skiprows: int = 9) -> pd.DataFrame:
    """
    Read a libRadtran OUT file even if some lines have extra tokens or stray text.
    - Skips the first `skiprows` lines (known to be blank in this dataset).
    - Ignores empty lines and comment lines.
    - Splits on whitespace and keeps only the first 7 numeric tokens.
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
            if len(parts) < 7:
                continue
            parts = parts[:7]
            # convert to floats; if a token is non-numeric, skip the line
            try:
                vals = [float(x) for x in parts]
            except ValueError:
                # Try to salvage numeric prefix
                vals = []
                for x in parts:
                    try:
                        vals.append(float(x))
                    except ValueError:
                        break
                if len(vals) != 7:
                    continue
            rows.append(vals)

    df = pd.DataFrame(rows, columns=COLS)
    
    # sort by wavelength & drop dup wavelengths (keep first)
    if not df.empty:
        df = df.sort_values("wavelength").drop_duplicates(subset="wavelength", keep="first")
    return df.reset_index(drop=True)


def integrate_xy(x: np.ndarray, y: np.ndarray) -> float:
    """Trapezoid integration with NaN masking. Returns np.nan if <2 valid points."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2:
        return np.nan
    # x must be increasing for a well-defined integral; sort masked points just in case
    xm, ym = x[m], y[m]
    if np.any(np.diff(xm) < 0):
        order = np.argsort(xm)
        xm, ym = xm[order], ym[order]
    return np.trapezoid(ym, xm)  # np.trapz is deprecated in NumPy 2.0+


def main():
    rows = []

    files = sorted(INPUT_DIR.glob(FILE_GLOB))
    if not files:
        print(f"No files found in {INPUT_DIR} matching {FILE_GLOB}")
        return

    for fp in files:
        m = SZA_RE.search(fp.name)
        if not m:
            print(f"Skipping (no SZA found): {fp.name}")
            continue
        sza = float(m.group(1))

        df = robust_read(fp, skiprows=9)
        if df.empty:
            print(f"Warning: no data rows parsed in {fp.name}")
            continue

        # Build spectral GHI for clarity (DirH + DiffDn)
        df["global_horiz"] = df["direct_horiz"] + df["diffuse_down_horiz"]

        wl = df["wavelength"].to_numpy(float)
        direct_h = df["direct_horiz"].to_numpy(float)         # DNI * cos(SZA)
        diffuse_dn = df["diffuse_down_horiz"].to_numpy(float) # DHI
        diffuse_up = df["diffuse_up_horiz"].to_numpy(float)
        global_h = df["global_horiz"].to_numpy(float)         # GHI spectrum

        # Integrate spectra over wavelength
        total_direct_horiz = integrate_xy(wl, direct_h)
        total_diffuse_down = integrate_xy(wl, diffuse_dn)
        total_diffuse_up = integrate_xy(wl, diffuse_up)
        total_global_horiz = integrate_xy(wl, global_h)

        # Reconstruct DNI and verify identity: GHI = DHI + DNI*cos(SZA)
        theta = np.deg2rad(sza)
        mu0 = float(np.cos(theta))
        dni_from_dirh = np.nan if mu0 < 1e-12 else (total_direct_horiz / mu0)
        ghi_from_identity = (
            np.nan if not np.isfinite(dni_from_dirh) else total_diffuse_down + dni_from_dirh * mu0
        )
        ghi_check_error = (
            np.nan if not np.isfinite(ghi_from_identity) else total_global_horiz - ghi_from_identity
        )

        rows.append({
            "sza_deg": sza,
            "mu0_cos_sza": mu0,
            "total_direct_horiz": total_direct_horiz,          # DNI*cos(SZA)
            "total_diffuse_down_horiz": total_diffuse_down,    # DHI
            "total_diffuse_up_horiz": total_diffuse_up,
            "total_global_horiz": total_global_horiz,          # GHI
            "dni_reconstructed": dni_from_dirh,                # from DirH / cos(SZA)
            "ghi_from_identity": ghi_from_identity,            # DHI + DNI*cos(SZA)
            "ghi_check_error": ghi_check_error                 # should be ~0 (round-off)
        })

    result = pd.DataFrame(rows).sort_values("sza_deg").reset_index(drop=True)
    result.to_csv(OUT_CSV, index=False)
    print(f"Saved: {OUT_CSV.resolve()}\n")
    print(result.to_string(index=False, float_format=lambda x: f"{x:.6g}"))


if __name__ == "__main__":
    main()
