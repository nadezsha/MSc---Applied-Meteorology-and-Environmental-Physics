import math
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# === USER SETTINGS ===
SCRIPT_DIR = Path(__file__).resolve().parent
FILE = SCRIPT_DIR / "integrated_data" / "epanomi_GHI_aeronet_integrated_by_sza.csv"

# If you want to force a single DOY for all rows, set DOY to an integer 1..365.
# Otherwise leave DOY=None to use per-row DOY (from 'doy' or 'date' column) or today's DOY as fallback.
DOY = None

# === eccentricity factor ===
def ecc_factor_from_doy(doy: int) -> float:
    return 1 + 0.033 * math.cos(2 * math.pi * doy / 365)

def choose(colnames, options):
    for name in options:
        if name in colnames:
            return name
    return None

df = pd.read_csv(FILE)

col_sza = choose(df.columns, ["sza_deg", "SZA", "sza"])
col_mu0 = choose(df.columns, ["mu0_cos_sza", "mu0", "cos_zenith"])
col_GHI = choose(df.columns, ["total_global_horiz", "ghi_from_identity", "GHI"])
col_DHI = choose(df.columns, ["total_diffuse_down_horiz", "DHI"])
col_DNI = choose(df.columns, ["dni_reconstructed", "DNI"])

if col_sza:
    df = df.sort_values(col_sza).reset_index(drop=True)

if col_DNI is None:
    col_DIR_h = choose(df.columns, ["total_direct_horiz", "direct_horizontal", "DIR_horiz"])
    if col_DIR_h and col_mu0:
        df["DNI_reconstructed_from_horizontal"] = df[col_DIR_h] / df[col_mu0]
        col_DNI = "DNI_reconstructed_from_horizontal"

missing = [n for n in [col_GHI, col_DHI, col_DNI] if n is None]
if missing:
    raise ValueError(
        f"Could not find required columns. Found: GHI={col_GHI}, DHI={col_DHI}, DNI={col_DNI}"
    )

if DOY is not None:
    df["ecc_factor"] = ecc_factor_from_doy(int(DOY))
elif "doy" in df.columns:
    df["ecc_factor"] = df["doy"].astype(int).clip(1, 365).apply(ecc_factor_from_doy)
elif "date" in df.columns:
    dates = pd.to_datetime(df["date"], errors="coerce")
    df["ecc_factor"] = dates.dt.dayofyear.fillna(1).astype(int).apply(ecc_factor_from_doy)
else:
    today_doy = datetime.utcnow().timetuple().tm_yday
    df["ecc_factor"] = ecc_factor_from_doy(today_doy)

df[f"{col_GHI}_corr"] = df[col_GHI] * df["ecc_factor"]
df[f"{col_DHI}_corr"] = df[col_DHI] * df["ecc_factor"]
df[f"{col_DNI}_corr"] = df[col_DNI] * df["ecc_factor"]

out_dir = Path(FILE).parent
out_path = out_dir / (Path(FILE).stem + "_ecc_corrected.csv")
df.to_csv(out_path, index=False)
print(f"Saved: {out_path}")

figures_dir = SCRIPT_DIR / "figures_GHI"
figures_dir.mkdir(exist_ok=True)

x = df[col_sza] if col_sza else df.index

# All three together
plt.figure()
plt.plot(x, df[f"{col_GHI}_corr"] / 1000, label="GHI")
plt.plot(x, df[f"{col_DHI}_corr"] / 1000, label="DHI")
plt.plot(x, df[f"{col_DNI}_corr"] / 1000, label="DNI")
plt.xlabel("Solar Zenith Angle (deg)" if col_sza else "Index")
plt.ylabel("Irradiance (W/m²)")
plt.title("Irradiances corrected for Earth–Sun distance (Epanomi AERONET, inversion run)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig(figures_dir / "epanomi_GHI_corrected_irradiances.png", dpi=300)
plt.show()

# DNI only
plt.figure()
plt.plot(x, df[f"{col_DNI}_corr"] / 1000, label="DNI", color="green")
plt.xlabel("Solar Zenith Angle (deg)" if col_sza else "Index")
plt.ylabel("Irradiance (W/m²)")
plt.title("DNI corrected for Earth–Sun distance (Epanomi AERONET, inversion run)")
plt.grid()
plt.tight_layout()
plt.savefig(figures_dir / "epanomi_GHI_corrected_DNI_irradiance.png", dpi=300)
plt.show()

# DHI only
plt.figure()
plt.plot(x, df[f"{col_DHI}_corr"] / 1000, label="DHI", color="orange")
plt.xlabel("Solar Zenith Angle (deg)" if col_sza else "Index")
plt.ylabel("Irradiance (W/m²)")
plt.title("DHI corrected for Earth–Sun distance (Epanomi AERONET, inversion run)")
plt.grid()
plt.tight_layout()
plt.savefig(figures_dir / "epanomi_GHI_corrected_DHI_irradiance.png", dpi=300)
plt.show()
