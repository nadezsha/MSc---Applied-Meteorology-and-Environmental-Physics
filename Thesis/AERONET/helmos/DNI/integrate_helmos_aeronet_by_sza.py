# Postprocess Helmos AERONET uvspec OUT files.
#
# For each file like:
#   helmos_2024-11-10_sza_083p0.OUT
# it:
#   - parses date and sza
#   - integrates spectra to broadband:
#       * total_direct_horizontal (DNI * cos(SZA))
#       * total_diffuse_down_horizontal (DHI)
#       * total_diffuse_up_horizontal
#       * total_global_horizontal (GHI = DirH + DiffDn)
#   - reconstructs DNI from DirH / cos(SZA)
#   - checks GHI = DHI + DNI * cos(SZA)
#
# Output: a single CSV with one row per OUT file.
# We only care about DNI at this stage

from pathlib import Path
import re
import numpy as np
import pandas as pd

# === USER SETTINGS ===
BASE_DIR = Path(
    r"c:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI\uvspec_runs"
)

# Pattern for OUT files; rglob searches all subfolders (dates)
FILE_PATTERN = "*.out"

# Output directory + file 
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "integrated_data"
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "helmos_aeronet_integrated_by_sza.csv"

# Expected column names in OUT files (wavelength + 6 fields)
COLS = [
    "wavelength",
    "direct_horiz",          # DNI * cos(SZA)
    "diffuse_down_horiz",    # DHI
    "diffuse_up_horiz",
]

# Regex to extract date and SZA from filenames like:
#   helmos_2024-11-10_sza_083p0.OUT

# Captures:
#   1) date YYYY-MM-DD
#   2) integer degrees (e.g. 083)
#   3) tenths (e.g. 0) after 'p'
FNAME_RE = re.compile(
    r"helmos_(\d{4}-\d{2}-\d{2})_sza_([0-9]{1,3})p([0-9])",
    re.IGNORECASE,
)


def robust_read(fp: Path, skiprows: int = 9) -> pd.DataFrame:
    """
    Read a libRadtran OUT file even if some lines have extra tokens or stray text.

    - Skips the first `skiprows` lines (header / comments).
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
            if len(parts) < 4:
                continue
            parts = parts[:4]

            try:
                vals = [float(x) for x in parts]
            except ValueError:
                # Try to salvage partial numeric content
                vals = []
                for x in parts:
                    try:
                        vals.append(float(x))
                    except ValueError:
                        break
                if len(vals) != 4:
                    continue

            rows.append(vals)

    df = pd.DataFrame(rows, columns=COLS)

    # Sort by wavelength & drop duplicates just in case
    if not df.empty:
        df = df.sort_values("wavelength").drop_duplicates(
            subset="wavelength", keep="first"
        )

    return df.reset_index(drop=True)


def integrate_xy(x: np.ndarray, y: np.ndarray) -> float:
    """
    Trapezoid integration with NaN masking.
    Returns np.nan if fewer than 2 valid points.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2:
        return np.nan

    xm, ym = x[m], y[m]

    # Enforce increasing x
    if np.any(np.diff(xm) < 0):
        order = np.argsort(xm)
        xm, ym = xm[order], ym[order]

    # np.trapz is deprecated in NumPy 2.0+, use trapezoid
    return np.trapezoid(ym, xm)


def parse_date_sza_from_name(name: str):
    """
    Extract date and SZA (deg) from filename.
    Returns (date_str, sza_deg_float) or (None, None) if no match.
    """
    m = FNAME_RE.search(name)
    if not m:
        return None, None

    date_str = m.group(1)

    deg_int = int(m.group(2))
    tenth = int(m.group(3))
    sza_deg = deg_int + 0.1 * tenth

    return date_str, sza_deg


def main():
    files = sorted(BASE_DIR.rglob(FILE_PATTERN))

    if not files:
        print(f"No OUT files found under {BASE_DIR} matching pattern {FILE_PATTERN}")
        return

    rows = []

    for fp in files:
        date_str, sza = parse_date_sza_from_name(fp.name)
        if date_str is None:
            # Not a standard Helmos file; you can comment this out if you want stricter behaviour
            print(f"Skipping (filename pattern not recognized): {fp}")
            continue

        df = robust_read(fp, skiprows=9)
        if df.empty:
            print(f"Warning: no data rows parsed in {fp}")
            continue

        # Build spectral GHI = DirH + DiffDn
        df["global_horiz"] = df["direct_horiz"] + df["diffuse_down_horiz"]

        wl = df["wavelength"].to_numpy(float)
        direct_h = df["direct_horiz"].to_numpy(float)         # DNI * cos(SZA)
        diffuse_dn = df["diffuse_down_horiz"].to_numpy(float) # DHI
        diffuse_up = df["diffuse_up_horiz"].to_numpy(float)
        global_h = df["global_horiz"].to_numpy(float)         # GHI

        # Integrate spectra over wavelength
        total_direct_horiz = integrate_xy(wl, direct_h)
        total_diffuse_down = integrate_xy(wl, diffuse_dn)
        total_diffuse_up = integrate_xy(wl, diffuse_up)
        total_global_horiz = integrate_xy(wl, global_h)

        # Reconstruct DNI; protect against cos(SZA) ~ 0 (sun at horizon)
        theta = np.deg2rad(sza)
        mu0 = float(np.cos(theta))

        if mu0 < 1e-12:
            dni_from_dirh = np.nan
            ghi_from_identity = np.nan
            ghi_check_error = np.nan
        else:
            dni_from_dirh = total_direct_horiz / mu0
            ghi_from_identity = total_diffuse_down + dni_from_dirh * mu0
            ghi_check_error = total_global_horiz - ghi_from_identity

        rows.append(
            {
                "date": date_str,
                "sza_deg": sza,
                "mu0_cos_sza": mu0,
                "total_direct_horiz": total_direct_horiz,          # DNI*cos(SZA)
                "total_diffuse_down_horiz": total_diffuse_down,    # DHI
                "total_diffuse_up_horiz": total_diffuse_up,
                "total_global_horiz": total_global_horiz,          # GHI
                "dni_reconstructed": dni_from_dirh,
                "ghi_from_identity": ghi_from_identity,
                "ghi_check_error": ghi_check_error,                # should be ~0
                "source_file": str(fp.relative_to(BASE_DIR)),
            }
        )

    if not rows:
        print("No valid rows were produced – check that your OUT files are readable.")
        return

    result = (
        pd.DataFrame(rows)
        .sort_values(["date", "sza_deg"])
        .reset_index(drop=True)
    )

    result.to_csv(OUT_CSV, index=False)
    print(f"Saved integrated data to:\n  {OUT_CSV.resolve()}\n")
    print(
        result.to_string(
            index=False,
            float_format=lambda x: f"{x:.6g}",
            max_rows=50,
            max_cols=20,
        )
    )


if __name__ == "__main__":
    main()