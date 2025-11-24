import pandas as pd
from pathlib import Path
import numpy as np

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

BASE = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos")
DATA_DIR = BASE / r"GHI\AERONET_data"

AOD_FILE = DATA_DIR / r"20241105_20241110_Helmos_NTUA.aod"  # EXTINCTION
ASY_FILE = DATA_DIR / r"20241105_20241110_Helmos_NTUA.asy"  # ASYMMETRY
TAB_FILE = DATA_DIR / r"20241105_20241110_Helmos_NTUA.tab"  # ABSORPTION

DETAIL_CSV = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI\outputs\aeronet_alpha_beta_pwv_detail.csv")

# Where to put the outputs for GHI work
OUT_DIR = BASE / r"GHI\outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_PER_TS  = OUT_DIR / "aeronet_ext_abs_g_per_timestamp.csv"
OUT_DAILY   = OUT_DIR / "aeronet_ext_abs_g_daily.csv"

NEAREST_TOL = pd.Timedelta("10min")  # how close alpha must be in time
LAMBDA_REF = 0.44                    # µm (440 nm) for Angström β
DATE_START = pd.Timestamp("2024-11-05")
DATE_END   = pd.Timestamp("2024-11-11")  # exclusive -> up to 10/11

# quick sanity check
print("AOD exists:", AOD_FILE.exists())
print("ASY exists:", ASY_FILE.exists())
print("TAB exists:", TAB_FILE.exists())
print("DETAIL_CSV exists:", DETAIL_CSV.exists())
if not DETAIL_CSV.exists():
    raise SystemExit(f"DETAIL_CSV not found at: {DETAIL_CSV}\n"
                     f"Locate 'aeronet_alpha_beta_pwv_detail.csv' and update this path.")

# -------------------------------------------------
# Helper: read AERONET inversion-style file
# -------------------------------------------------
def read_inv_file(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        start = None
        for i, line in enumerate(f):
            if line.startswith("Site,Date(dd:mm:yyyy)"):
                start = i
                break
    if start is None:
        raise ValueError(f"Header line not found in {path}")

    df = pd.read_csv(path, skiprows=start)
    df["Datetime"] = pd.to_datetime(
        df["Date(dd:mm:yyyy)"] + " " + df["Time(hh:mm:ss)"],
        format="%d:%m:%Y %H:%M:%S",
        errors="coerce"
    )
    df = df.dropna(subset=["Datetime"])
    df = df.sort_values("Datetime")
    return df

def pick_col(df: pd.DataFrame, pattern: str) -> str:
    """
    Find the first column whose name contains the given pattern
    (after removing spaces). Raises a clear error if nothing matches.
    """
    matches = [c for c in df.columns if pattern in c.replace(" ", "")]
    if not matches:
        raise SystemExit(
            f"Could not find a column containing '{pattern}'\n"
            f"Available columns:\n{list(df.columns)}"
        )
    if len(matches) > 1:
        print(f"Warning: multiple matches for '{pattern}', using '{matches[0]}'")
    return matches[0]

# -------------------------------------------------
# 1. Read the three files
# -------------------------------------------------
aod = read_inv_file(AOD_FILE)  # extinction
asy = read_inv_file(ASY_FILE)  # asymmetry
tab = read_inv_file(TAB_FILE)  # absorption

print("AOD columns:", list(aod.columns))
print("ASY columns:", list(asy.columns))
print("TAB columns:", list(tab.columns))

# --- auto-detect the 440 nm columns we care about ---
# .aod: extinction
ext440_col = pick_col(aod, "AOD_Extinction-Total[440")
# .tab: absorption
abs440_col = pick_col(tab, "Absorption_AOD[440")
# .asy: asymmetry factor
g440_col   = pick_col(asy, "Asymmetry_Factor-Total[440")

print("Using columns:")
print("  tau_ext_440  <-", ext440_col)
print("  tau_abs_440  <-", abs440_col)
print("  g_440        <-", g440_col)

aod["tau_ext_440"] = pd.to_numeric(aod[ext440_col], errors="coerce")
tab["tau_abs_440"] = pd.to_numeric(tab[abs440_col], errors="coerce")
asy["g_440"]       = pd.to_numeric(asy[g440_col],   errors="coerce")

ext_small = aod[["Datetime", "tau_ext_440"]]
abs_small = tab[["Datetime", "tau_abs_440"]]
asy_small = asy[["Datetime", "g_440"]]

# -------------------------------------------------
# 2. Merge extinction + absorption + asymmetry on exact time
# -------------------------------------------------
merge1 = pd.merge(ext_small, abs_small, on="Datetime", how="inner")
merge2 = pd.merge(merge1,   asy_small, on="Datetime", how="inner")

# filter to 05–10 Nov 2024
mask = (merge2["Datetime"] >= DATE_START) & (merge2["Datetime"] < DATE_END)
inv_all = merge2[mask].copy()

print("Number of inversion points in date window:", len(inv_all))

# -------------------------------------------------
# 3. Compute SSA at 440 nm from τ_abs, τ_ext
#     SSA = 1 - tau_abs / tau_ext
# -------------------------------------------------
inv_all["ssa_440"] = 1.0 - inv_all["tau_abs_440"] / inv_all["tau_ext_440"]

# -------------------------------------------------
# 4. Attach nearest alpha from your DNI table
# -------------------------------------------------
detail = pd.read_csv(DETAIL_CSV, parse_dates=["Datetime"])
detail_small = detail[["Datetime", "alpha"]].dropna().sort_values("Datetime")

inv_all = inv_all.sort_values("Datetime")

inv_match = pd.merge_asof(
    inv_all,
    detail_small,
    on="Datetime",
    direction="nearest",
    tolerance=NEAREST_TOL
)

# drop inversion points that had no nearby alpha
before = len(inv_match)
inv_match = inv_match.dropna(subset=["alpha"]).reset_index(drop=True)
after = len(inv_match)
print(f"Matched {after} points with alpha (dropped {before - after})")

# -------------------------------------------------
# 5. Save per-timestamp table
# -------------------------------------------------
inv_match.to_csv(OUT_PER_TS, index=False)
print("Wrote per-timestamp file:", OUT_PER_TS)

# -------------------------------------------------
# 6. Make daily medians and compute β_ext
# -------------------------------------------------
inv_match["date"] = inv_match["Datetime"].dt.date

daily = inv_match.groupby("date").agg(
    n=("alpha", "size"),
    alpha_med=("alpha", "median"),
    tau_ext440_med=("tau_ext_440", "median"),
    tau_abs440_med=("tau_abs_440", "median"),
    ssa440_med=("ssa_440", "median"),
    g440_med=("g_440", "median"),
).reset_index()

# β_ext from τ_ext(0.44 µm) and α:
daily["beta_ext_med"] = daily["tau_ext440_med"] * (LAMBDA_REF ** daily["alpha_med"])

daily.to_csv(OUT_DAILY, index=False)
print("Wrote daily summary:", OUT_DAILY)
print(daily)