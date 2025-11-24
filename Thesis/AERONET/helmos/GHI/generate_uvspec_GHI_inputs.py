import pandas as pd
import numpy as np
from pathlib import Path

# ------------------ CONFIG ------------------
BASE = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos")
CSV  = BASE / r"GHI\outputs\aeronet_ext_abs_g_daily.csv"

# Output folder for the generated uvspec input files
OUTROOT = BASE / r"GHI\uvspec_runs_GHI"
OUTROOT.mkdir(parents=True, exist_ok=True)

# SZA grid
SZA_START, SZA_END, SZA_STEP = 15.0, 90.0, 0.5

# Base configuration for libRadtran
BASE_CONFIG = """# GHI file for Helmos using inversion inputs
atmosphere_file /home/nadezsha/libRadtran-2.0.6/data/atmmod/afglmw.dat
source solar /home/nadezsha/libRadtran-2.0.6/data/solar_flux/kurudz_1.0nm.dat

wavelength 400 1100
spline 400 1100 1

mol_abs_param SBDART
altitude 1.75
rte_solver sdisort
number_of_streams 4

output_user lambda edir edn eup
"""

def sza_tag(x: float) -> str:
    return f"{x:05.1f}".replace(".", "p")

# ------------------ LOAD DAILY CSV ------------------
df = pd.read_csv(CSV)

required = {"date", "alpha_med", "beta_ext_med", "ssa440_med", "g440_med"}
missing = required - set(df.columns)
if missing:
    raise SystemExit(f"Missing columns in CSV: {missing}")

df = df.dropna(subset=list(required))

count = 0

# ------------------ GENERATE INPUT FILES ------------------
for _, row in df.iterrows():
    date = str(row["date"])
    alpha = float(row["alpha_med"])
    beta  = float(row["beta_ext_med"])
    ssa   = float(row["ssa440_med"])
    gg    = float(row["g440_med"])

    # create folder for this date
    daydir = OUTROOT / date
    daydir.mkdir(exist_ok=True)

    sza_vals = np.arange(SZA_START, SZA_END + 1e-9, SZA_STEP)

    for sza in sza_vals:
        body = [
            BASE_CONFIG.strip(),
            f"sza {sza:.1f}",
            "",
            "# ---- Aerosol: Angström + SSA + asymmetry factor ----",
            "aerosol_default",
            f"aerosol_angstrom {alpha:.6f} {beta:.6f}",
            f"aerosol_modify ssa set {ssa:.6f}",
            f"aerosol_modify gg set {gg:.6f}",
            "",
            "quiet"
        ]

        fname = daydir / f"helmos_GHI_{date}_sza_{sza_tag(sza)}.inp"
        with open(fname, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(body) + "\n")

        count += 1

print(f"Generated {count} input files in: {OUTROOT}")