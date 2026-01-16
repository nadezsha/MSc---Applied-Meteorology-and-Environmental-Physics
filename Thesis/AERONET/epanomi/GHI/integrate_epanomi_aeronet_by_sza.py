# Postprocess Epanomi AERONET uvspec OUT files (GHI run).
#
# For each file like:
#   epanomi_GHI_2025-05-10_sza_083p0.out
#
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
    r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\epanomi\GHI\uvspec_runs_GHI"
)

# Pattern for OUT files
FILE_PATTERN = "*.out"

# Output directory + file
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "integrated_data"
OUT_DIR.mkdir(exist_ok=True)
OUT_CSV = OUT_DIR / "epanomi_GHI_aeronet_integrated_by_sza.csv"

# libRadtran output columns
COLS = [
    "wavelength",
    "edir",
    "edn",
    "eup",
]

# Filename example:
#   epanomi_GHI_2025-05-10_sza_083p0.out
FNAME_RE = re.compile(
    r"epanomi_GHI_(\d{4}-\d{2}-\d{2})_sza_([0-9]{1,3})p([0-9])",
    re.IGNORECASE,
)


def robust_read(fp: Path, skiprows: int = 9) -> pd.DataFrame:
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
                continue

            rows.append(vals)

    df = pd.DataFrame(rows, columns=COLS)
    if not df.empty:
        df = df.sort_values("wavelength").drop_duplicates("wavelength", keep="first")
    return df.reset_index(drop=True)


def integrate_xy(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2:
        return np.nan
    xm, ym = x[m], y[m]
    if np.any(np.diff(xm) < 0):
        ix = np.argsort(xm)
        xm, ym = xm[ix], ym[ix]
    return np.trapezoid(ym, xm)


def parse_date_sza_from_name(name: str):
    m = FNAME_RE.search(name)
    if not m:
        return None, None
    date_str = m.group(1)
    sza = int(m.group(2)) + 0.1 * int(m.group(3))
    return date_str, sza


def main():
    files = [
        fp for fp in BASE_DIR.rglob("epanomi_GHI_*")
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
            print(f"Skipping: {fp.name}")
            continue

        df = robust_read(fp)
        if df.empty:
            print(f"Warning: {fp} contains no data")
            continue

        wl = df["wavelength"].to_numpy(float)
        edir = df["edir"].to_numpy(float)
        edn = df["edn"].to_numpy(float)
        eup = df["eup"].to_numpy(float)

        mu0 = np.cos(np.radians(sza))
        direct_h = edir * mu0
        global_h = direct_h + edn

        total_direct = integrate_xy(wl, direct_h)
        total_diffuse_dn = integrate_xy(wl, edn)
        total_diffuse_up = integrate_xy(wl, eup)
        total_ghi = integrate_xy(wl, global_h)

        if mu0 > 1e-12:
            dni = total_direct / mu0
            ghi_identity = total_diffuse_dn + dni * mu0
            ghi_err = total_ghi - ghi_identity
        else:
            dni = np.nan
            ghi_identity = np.nan
            ghi_err = np.nan

        rows.append(
            {
                "date": date_str,
                "sza_deg": sza,
                "mu0_cos_sza": mu0,
                "total_direct_horiz": total_direct,
                "total_diffuse_down_horiz": total_diffuse_dn,
                "total_diffuse_up_horiz": total_diffuse_up,
                "total_global_horiz": total_ghi,
                "dni_reconstructed": dni,
                "ghi_from_identity": ghi_identity,
                "ghi_check_error": ghi_err,
                "source_file": str(fp.relative_to(BASE_DIR)),
            }
        )

    df_out = pd.DataFrame(rows).sort_values(["date", "sza_deg"])
    df_out.to_csv(OUT_CSV, index=False)

    print("\nSaved integrated data to:")
    print(" ", OUT_CSV)


if __name__ == "__main__":
    main()
