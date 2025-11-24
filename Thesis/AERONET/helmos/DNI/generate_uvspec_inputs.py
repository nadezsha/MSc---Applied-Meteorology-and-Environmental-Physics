"""
uvspec input generator from AERONET daily medians (Helmos)
----------------------------------------------------------

Purpose
-------
For each day in the AERONET daily summary csv, create a set of libRadtran
uvspec .inp files over a solar-zenith-angle (sza) grid. Each input encodes:
- Aerosol via Ångström law: tau(λ) = β * λ^(−α)  (λ in µm).
- Water vapour column (PWV) if available.
- Common radiative-transfer settings (solver, atmosphere, solar spectrum).
- 1 nm spectral outputs (400–1100 nm): lambda, edir, edn, eup.

Inputs
------
- CSV: outputs/aeronet_alpha_beta_pwv_daily.csv
  Required columns: date, alpha_med, beta440_med, pwv_cm_med (PWV may be NaN).

Outputs
-------
- One folder per day: BASE_DIR/uvspec_runs/<YYYY-MM-DD>/
- Inside: helmos_<date>_sza_<XXXpX>.inp for SZAs 15.0..90.0 every 0.5 deg.

Key settings
------------
- Ångström parameters: "aerosol_angstrom <alpha> <beta>" using µm units.
- Altitude: 1.75 km a.s.l.
- Solar flux: kurudz_1.0nm.dat
- Atmosphere: afglmw.dat
- Solver: sdisort with 4 streams
- Spectral grid: wavelength 300 1100; spline 300 1100 1
- Output: output_user lambda edir edn eup

Notes
-----
- β here is the Ångström turbidity coefficient computed from AERONET (β at 0.44 µm).
- PWV is converted from cm to mm for "mol_modify H2O <PWV_mm> MM".
- If PWV is missing for a day, the H2O line is commented out.
- Files are written with Unix newlines to avoid CRLF issues under WSL.
- The script prints the equivalent /mnt/c/... path for running from Ubuntu/WSL.

"""


import pandas as pd
from pathlib import Path
import numpy as np

# ---------------- CONFIG (WINDOWS paths) ----------------
# Base project folder
BASE_DIR = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI")
CSV = BASE_DIR / r"outputs\aeronet_alpha_beta_pwv_daily.csv"  # daily medians CSV

# Where to place generated input files (Windows side; WSL sees it at /mnt/c/...)
OUTROOT = BASE_DIR / "uvspec_runs"
OUTROOT.mkdir(parents=True, exist_ok=True)

# SZA grid (deg)
SZA_START, SZA_END, SZA_STEP = 15.0, 90.0, 0.5

# Base uvspec block (common configuration)
BASE = """# file for Helmos
atmosphere_file /home/nadezsha/libRadtran-2.0.6/data/atmmod/afglmw.dat
source solar /home/nadezsha/libRadtran-2.0.6/data/solar_flux/kurudz_1.0nm.dat

wavelength 400 1100
spline 400 1100 1          # 1 nm output grid

mol_abs_param SBDART
altitude 1.75               # km a.s.l.
rte_solver sdisort
number_of_streams 4

# outputs
output_user lambda edir edn eup
"""

# ---------------- LOAD & VALIDATE ----------------
df = pd.read_csv(CSV)
required_cols = {"date", "alpha_med", "beta440_med", "pwv_cm_med"}
missing = required_cols - set(df.columns)
if missing:
    raise SystemExit(f"Missing columns in CSV: {missing}")

df = df.dropna(subset=["alpha_med", "beta440_med"])

def sza_tag(x: float) -> str:
    """Generate compact tag like 015p0, 059p5, etc."""
    return f"{x:05.1f}".replace(".", "p")

count = 0

# ---------------- GENERATE .inp FILES ----------------
for _, row in df.iterrows():
    date_str = str(row["date"])
    alpha = float(row["alpha_med"])
    beta = float(row["beta440_med"])
    pwv_cm = row["pwv_cm_med"]
    pwv_mm = None if pd.isna(pwv_cm) else float(pwv_cm) * 10.0  # convert cm → mm

    # τ(440) from Angström’s law: τ(λ) = β·λ^(−α)
    tau440 = beta * (0.44 ** (-alpha))

    # Create folder for this day
    daydir = OUTROOT / date_str
    daydir.mkdir(parents=True, exist_ok=True)

    sza_vals = np.arange(SZA_START, SZA_END + 1e-9, SZA_STEP)

    for sza in sza_vals:
        body = [
            BASE.strip(),
            f"sza {sza:.1f}",
            "",
            "# ---- AEROSOL (Angstrom law) ----",
            "aerosol_default",
            f"aerosol_angstrom {alpha:.6f} {beta:.6f}",
            "",
            "# ---- WATER VAPOUR COLUMN ----",
            (f"mol_modify H2O {pwv_mm:.4f} MM" if pwv_mm is not None else "# mol_modify H2O <missing>"),
            "",
            "quiet",
            ""
        ]

        fname = daydir / f"helmos_{date_str}_sza_{sza_tag(sza)}.inp"
        # Write with Unix newlines so WSL uvSpec reads cleanly
        with open(fname, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(body) + "\n")
        count += 1

print(f"✅ Generated {count} input files under (Windows): {OUTROOT}")

# Print equivalent WSL path for reference
wsl_path = "/mnt/" + str(OUTROOT.drive)[0].lower() + str(OUTROOT).split(":")[1].replace("\\", "/")
print("Run from WSL using path:", wsl_path)
