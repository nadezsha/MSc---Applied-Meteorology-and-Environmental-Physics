import math
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === USER SETTINGS ===
FILE = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\epanomi_model\intergrated_data\integrated_irradiance_by_sza.csv"
# If the file has a 'doy' (day-of-year) column, set a constant DOY for the whole file [(1..365), e.g. perihelion ~ Jan 3 -> DOY=3]
# otherwise leave DOY=None which is the case here.
DOY = None 

# === eccentricity factor ===
def ecc_factor_from_doy(doy: int) -> float:

    """Eccentricity correction factor E0 = 1 + 0.033*cos(2π n/365)."""
    return 1 + 0.033 * math.cos(2 * math.pi * doy / 365)

def choose(colnames, options):
    """Pick first existing name from 'options' list."""
    for name in options:
        if name in colnames:
            return name
    return None

# === read file and set columns ===
df = pd.read_csv(FILE)

col_sza = choose(df.columns, ["sza_deg", "SZA", "sza"])
col_mu0 = choose(df.columns, ["mu0_cos_sza", "mu0", "cos_zenith"])
col_GHI = choose(df.columns, ["total_global_horiz", "ghi_from_identity", "GHI"])
col_DHI = choose(df.columns, ["total_diffuse_down_horiz", "DHI"])
col_DNI = choose(df.columns, ["dni_reconstructed", "DNI"])

# If DNI is missing but you have direct HORIZ and mu0, reconstruct: DNI = DIR_horiz / mu0
if col_DNI is None:
    col_DIR_h = choose(df.columns, ["total_direct_horiz", "direct_horizontal", "DIR_horiz"])
    if col_DIR_h and col_mu0:
        df["DNI_reconstructed_from_horizontal"] = df[col_DIR_h] / df[col_mu0]
        col_DNI = "DNI_reconstructed_from_horizontal"

# missing columns check
missing = [n for n in [col_GHI, col_DHI, col_DNI] if n is None]
if missing:
    raise ValueError(f"Could not find required columns. Found: GHI={col_GHI}, DHI={col_DHI}, DNI={col_DNI}")

# === ECCENTRICITY FACTOR ===
if DOY is not None:
    E0 = ecc_factor_from_doy(int(DOY))
    df["ecc_factor"] = E0
elif "doy" in df.columns:
    df["ecc_factor"] = df["doy"].astype(int).clip(1, 365).apply(ecc_factor_from_doy)
else:
    # If no DOY provided and no 'doy' column, default to today's DOY
    from datetime import datetime
    today_doy = datetime.utcnow().timetuple().tm_yday
    df["ecc_factor"] = ecc_factor_from_doy(today_doy)

# === APPLY CORRECTION ===
df[f"{col_GHI}_corr"] = df[col_GHI] * df["ecc_factor"]
df[f"{col_DHI}_corr"] = df[col_DHI] * df["ecc_factor"]
df[f"{col_DNI}_corr"] = df[col_DNI] * df["ecc_factor"]

# === SAVE CSV ===
out_dir = Path(FILE).parent     
out_dir.mkdir(exist_ok=True)   

out_path = out_dir / (Path(FILE).stem + "_ecc_corrected.csv")
df.to_csv(out_path, index=False)
print(f"Saved: {out_path}")


# === PLOT IRRADIANCES ===
figures_dir = Path(FILE).parent.parent / "figures" 
figures_dir.mkdir(exist_ok=True)

x = df[col_sza] if col_sza else df.index
plt.figure()
plt.plot(x, df[f"{col_GHI}_corr"] / 1000, label="GHI")
plt.plot(x, df[f"{col_DHI}_corr"] / 1000, label="DHI")
plt.plot(x, df[f"{col_DNI}_corr"] / 1000, label="DNI")
plt.xlabel("Solar Zenith Angle (deg)" if col_sza else "Index")
plt.ylabel("Irradiance (W/m²)")
plt.title("Irradiances corrected for Earth–Sun distance")
plt.legend()
plt.grid()
plt.tight_layout()
fig_path = figures_dir / "corrected_irradiances.png"
plt.savefig(fig_path, dpi=300)
plt.show()

# === PLOT DHI SEPERATELY ===
x = df[col_sza] if col_sza else df.index
plt.figure()
plt.plot(x, df[f"{col_DHI}_corr"] / 1000, label="DHI", color='orange')
plt.xlabel("Solar Zenith Angle (deg)" if col_sza else "Index")
plt.ylabel("Irradiance (W/m²)")
plt.title("DHI corrected for Earth–Sun distance")
plt.grid()
plt.tight_layout()
fig_path = figures_dir / "corrected_DHI_irradiance.png"
plt.savefig(fig_path, dpi=300)
plt.show()