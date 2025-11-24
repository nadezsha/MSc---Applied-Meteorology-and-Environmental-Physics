# Postprocess Helmos AERONET uvspec OUT files (GHI run).
#
# For each file like:
#   helmos_GHI_2024-11-10_sza_083p0.out
# or even without .out extension,
# it:
#   - parses date and sza
#   - constructs spectral:
#       * direct_horizontal   = edir * cos(SZA)
#       * diffuse_down_horiz  = edn
#       * diffuse_up_horiz    = eup
#       * global_horizontal   = direct_horiz + diffuse_down_horiz
#   - integrates over wavelength:
#       * total_direct_horiz        (W/m²)
#       * total_diffuse_down_horiz  (W/m²)
#       * total_diffuse_up_horiz    (W/m²)
#       * total_global_horiz        (W/m²)
#   - reconstructs DNI from DirH / cos(SZA)
#   - checks GHI = DHI + DNI * cos(SZA)
#
# Output: a single CSV with one row per OUT file.

from pathlib import Path
import re
import numpy as np
import pandas as pd

# === USER SETTINGS ===
BASE_DIR = Path(
    r"c:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\GHI\uvspec_runs_GHI"
)

# Pattern for OUT files; rglob searches all subfolders (dates)
FILE_PATTERN = "*.out"

# Output directory + file 
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "integrated_data"
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "helmos_GHI_aeronet_integrated_by_sza.csv"

# For GHI run: output_user lambda edir edn eup
COLS = [
    "wavelength",
    "edir",   # direct normal spectral
    "edn",    # diffuse down
    "eup",    # diffuse up
]

# Filenames: helmos_GHI_YYYY-MM-DD_sza_083p0[.out]
FNAME_RE = re.compile(
    r"helmos_GHI_(\d{4}-\d{2}-\d{2})_sza_([0-9]{1,3})p([0-9])",
    re.IGNORECASE,
)


def robust_read(fp: Path, skiprows: int = 9) -> pd.DataFrame:
    """
    Read a libRadtran OUT file with columns: wl, edir, edn, eup.
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

    df = pd.DataFrame(rows, columns=COLS)

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

    if np.any(np.diff(xm) < 0):
        order = np.argsort(xm)
        xm, ym = xm[order], ym[order]

    return np.trapezoid(ym, xm)


def parse_date_sza_from_name(name: str):
    """
    Extract date and SZA (deg) from filename.
    Works whether or not there is an extension.
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
    # Find all files with "helmos_GHI_" in the name, in all subfolders,
    # but skip .inp files.
    files = [
        fp for fp in BASE_DIR.rglob("helmos_GHI_*")
        if fp.is_file() and fp.suffix.lower() != ".inp"
    ]

    if not files:
        print(f"No model files found under {BASE_DIR}")
        return

    print(f"Found {len(files)} files to process.")

    rows = []

    for fp in files:
        date_str, sza = parse_date_sza_from_name(fp.name)
        if date_str is None:
            print(f"Skipping (filename pattern not recognized): {fp}")
            continue

        df = robust_read(fp, skiprows=9)
        if df.empty:
            print(f"Warning: no data rows parsed in {fp}")
            continue

        wl = df["wavelength"].to_numpy(float)
        edir = df["edir"].to_numpy(float)   # direct normal spectral
        edn  = df["edn"].to_numpy(float)    # diffuse down
        eup  = df["eup"].to_numpy(float)    # diffuse up

        theta = np.deg2rad(sza)
        mu0 = float(np.cos(theta))

        direct_h = edir * mu0
        global_h = direct_h + edn

        total_direct_horiz = integrate_xy(wl, direct_h)
        total_diffuse_down = integrate_xy(wl, edn)
        total_diffuse_up   = integrate_xy(wl, eup)
        total_global_horiz = integrate_xy(wl, global_h)

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
                "total_direct_horiz": total_direct_horiz,
                "total_diffuse_down_horiz": total_diffuse_down,
                "total_diffuse_up_horiz": total_diffuse_up,
                "total_global_horiz": total_global_horiz,
                "dni_reconstructed": dni_from_dirh,
                "ghi_from_identity": ghi_from_identity,
                "ghi_check_error": ghi_check_error,
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