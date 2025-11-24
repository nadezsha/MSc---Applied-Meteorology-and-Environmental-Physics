"""
AERONET α–β–PWV processor for Helmos station
---------------------------------------------

- Loads all .lev15 AERONET files for AOD and PWV from given folders.
- Detects and merges the data tables automatically.
- Derives Ångström exponent (α) from AERONET columns (or 440–870 nm pair if needed).
- Computes turbidity coefficient β at 0.44 µm and AOD at 0.55 µm using τ(λ) = β λ^(−α).
- Merges AOD with PWV by timestamp (nearest within ±2 min if needed).
- Produces daily median and IQR statistics for α, β, τ₅₅₀, and PWV.
- Generates per-timestamp and daily-median AOD spectra (400–1100 nm).
- Saves three CSVs:
    1. aeronet_alpha_beta_pwv_detail.csv — full merged data per timestamp
    2. aeronet_alpha_beta_pwv_daily.csv  — daily summary (median, IQR)
    3. aeronet_tau_spectra.csv           — spectral AOD (per timestamp + daily median)

Notes
-----
- Wavelengths are in micrometers (µm).
- AERONET "Precipitable_Water(cm)" is converted directly to cm.
- Missing or invalid values are dropped before saving.
- Tested with AERONET Version 3 Level 1.5 data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ------------------ CONFIG ------------------
AOD_DIR = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI\AERONET_AOD_data\all_data")
PWV_DIR = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI\AERONET_water_vapour_data\all_data")

# Where to save ALL outputs (will be created if missing)
OUT_DIR = Path(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\AERONET\helmos\DNI\outputs")

# Spectral grid (nm)
LAMBDA_NM = np.arange(400, 1101, 1)              # 400..1100 nm
LAMBDA_UM = LAMBDA_NM / 1000.0                   # µm for Ångström law

MISSING = -999.0
NEAREST_TOL = pd.Timedelta("2min")
# --------------------------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DETAIL = OUT_DIR / "aeronet_alpha_beta_pwv_detail.csv"
OUT_DAILY  = OUT_DIR / "aeronet_alpha_beta_pwv_daily.csv"
OUT_SPEC   = OUT_DIR / "aeronet_tau_spectra.csv" 

def read_lev15_table(folder: Path):
    files = sorted(folder.glob("*.lev15"))
    if not files:
        raise SystemExit(f"No .lev15 files in {folder}")
    frames = []
    for p in files:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            start = None
            for i, line in enumerate(f):
                if line.startswith("Date("):
                    start = i
                    break
        if start is None:
            raise ValueError(f"Header not found in {p}")
        df = pd.read_csv(p, skiprows=start, na_values=[MISSING], low_memory=False)
        df["Datetime"] = pd.to_datetime(
            df["Date(dd:mm:yyyy)"] + " " + df["Time(hh:mm:ss)"],
            format="%d:%m:%Y %H:%M:%S", errors="coerce"
        )
        df["source_file"] = p.name
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values("Datetime")
    return out

# ---------- Load AOD and compute alpha/beta ----------
aod = read_lev15_table(AOD_DIR)

# Pick Angstrom exponent column if available
alpha_col = None
for cand in aod.columns:
    if cand.strip() == "440-870_Angstrom_Exponent":
        alpha_col = cand; break
if alpha_col is None:
    for cand in aod.columns:
        if cand.strip() == "440-675_Angstrom_Exponent":
            alpha_col = cand; break

has_440 = "AOD_440nm" in aod.columns
has_870 = "AOD_870nm" in aod.columns

res = aod[["Datetime","source_file"]].copy()

if alpha_col is not None:
    res["alpha"] = pd.to_numeric(aod[alpha_col], errors="coerce")
else:
    if not (has_440 and has_870):
        raise SystemExit("Need AOD_440nm and AOD_870nm or an Angstrom exponent column.")
    tau440 = pd.to_numeric(aod["AOD_440nm"], errors="coerce")
    tau870 = pd.to_numeric(aod["AOD_870nm"], errors="coerce")
    res["alpha"] = -np.log(tau440 / tau870) / np.log(0.44 / 0.87)

if not has_440:
    raise SystemExit("AOD_440nm not found in AOD files.")
res["AOD_440nm"] = pd.to_numeric(aod["AOD_440nm"], errors="coerce")

# β at 0.44 µm: β = τ(0.44) * (0.44)^α
res["beta_440"] = res["AOD_440nm"] * (0.44 ** res["alpha"])

# τ550 using α,β
res["tau_550"] = res["beta_440"] * (0.55 ** (-res["alpha"]))

# ---------- Load PWV ----------
pwv = read_lev15_table(PWV_DIR)
if "Precipitable_Water(cm)" not in pwv.columns:
    raise SystemExit("Precipitable_Water(cm) not found in PWV files.")
pwv_small = pwv[["Datetime","Precipitable_Water(cm)"]].rename(columns={"Precipitable_Water(cm)":"PWV_cm"})
pwv_small["PWV_cm"] = pd.to_numeric(pwv_small["PWV_cm"], errors="coerce")

# ---------- Merge (exact, then nearest if needed) ----------
merged = res.merge(pwv_small, on="Datetime", how="left")
if merged["PWV_cm"].isna().mean() > 0.5:
    merged = pd.merge_asof(
        res.sort_values("Datetime"),
        pwv_small.sort_values("Datetime"),
        on="Datetime", direction="nearest", tolerance=NEAREST_TOL
    )

merged = merged.dropna(subset=["Datetime","alpha","beta_440","AOD_440nm"])

# ---------- Daily stats ----------
merged["date"] = merged["Datetime"].dt.date
daily = merged.groupby("date").agg(
    n=("alpha","size"),
    alpha_med=("alpha","median"),
    alpha_iqr=("alpha", lambda x: x.quantile(0.75)-x.quantile(0.25)),
    beta440_med=("beta_440","median"),
    beta440_iqr=("beta_440", lambda x: x.quantile(0.75)-x.quantile(0.25)),
    tau550_med=("tau_550","median"),
    tau550_iqr=("tau_550", lambda x: x.quantile(0.75)-x.quantile(0.25)),
    pwv_cm_med=("PWV_cm","median"),
    pwv_cm_iqr=("PWV_cm", lambda x: x.quantile(0.75)-x.quantile(0.25)),
).reset_index()

# ---------- Spectral AOD: 400–1100 nm ----------
# Per-timestamp spectra (LONG format to keep file size reasonable)
def spectra_long(df):
    # df needs columns: Datetime, alpha, beta_440
    lam_um = pd.Series(LAMBDA_UM, name="lambda_um")
    # broadcasting: tau(λ) = β * λ^{-α}
    # For varying α,β by row, use apply for memory safety
    rows = []
    for _, r in df[["Datetime","alpha","beta_440"]].dropna().iterrows():
        tau = r["beta_440"] * (LAMBDA_UM ** (-r["alpha"]))
        tmp = pd.DataFrame({
            "Datetime": r["Datetime"],
            "lambda_nm": LAMBDA_NM,
            "lambda_um": LAMBDA_UM,
            "tau_lambda": tau
        })
        tmp["kind"] = "per_timestamp"
        rows.append(tmp)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["Datetime","lambda_nm","lambda_um","tau_lambda","kind"])

spec_detail = spectra_long(merged)

# Daily-median spectra (use α_med, β_med per date)
def spectra_daily(df_daily):
    rows = []
    for _, r in df_daily.iterrows():
        tau = r["beta440_med"] * (LAMBDA_UM ** (-r["alpha_med"]))
        tmp = pd.DataFrame({
            "date": r["date"],
            "lambda_nm": LAMBDA_NM,
            "lambda_um": LAMBDA_UM,
            "tau_lambda": tau
        })
        tmp["kind"] = "daily_median"
        rows.append(tmp)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["date","lambda_nm","lambda_um","tau_lambda","kind"])

spec_daily = spectra_daily(daily)

# Combine spectra (Datetime for per_timestamp; date for daily_median)
spec_all = pd.concat([spec_detail, spec_daily], ignore_index=True, sort=False)

# ---------- Save ----------
merged.to_csv(OUT_DETAIL, index=False)
daily.to_csv(OUT_DAILY, index=False)
spec_all.to_csv(OUT_SPEC, index=False)

print("Wrote:", OUT_DETAIL)
print("Wrote:", OUT_DAILY)
print("Wrote:", OUT_SPEC)
print("\nDaily summary:")
print(daily)