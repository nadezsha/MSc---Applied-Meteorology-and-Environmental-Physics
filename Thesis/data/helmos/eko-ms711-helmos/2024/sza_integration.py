import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---- Paths ----
in_path = Path("sza_calculation/sza_calculation.csv")

# Make a "figures" directory alongside the CSV
fig_dir = in_path.parent / "figures"
fig_dir.mkdir(exist_ok=True)

# ---- Load ----
df = pd.read_csv(in_path)

# ---- Find wavelength columns (numeric headers) ----
wl_cols, wls = [], []
for col in df.columns:
    try:
        wl = float(str(col).strip())
        wl_cols.append(col)
        wls.append(wl)
    except:
        pass
if not wl_cols:
    raise ValueError("No numeric wavelength columns found (e.g., 300..1100).")

wl = np.array(wls, dtype=float)
order = np.argsort(wl)
wl = wl[order]
wl_cols = np.array(wl_cols, dtype=object)[order]

# ---- Convert mW -> W BEFORE integrating ----
spectral_w = df[wl_cols].apply(pd.to_numeric, errors="coerce") / 1000.0

# ---- Integrate over wavelength ----
vals = spectral_w.to_numpy()
ghi_int = np.array([np.trapezoid(row, x=wl) if np.isfinite(row).any() else np.nan for row in vals])
df["GHI_integrated_Wm2"] = ghi_int

# ---- Find SZA column ----
sza_col = None
for c in df.columns:
    cl = c.lower()
    if cl == "sza" or "solar_zenith" in cl or "zenith" in cl:
        sza_col = c
        break
if sza_col is None:
    raise ValueError("Couldn't find SZA column (e.g., 'solar_zenith' or 'sza').")

sza = pd.to_numeric(df[sza_col], errors="coerce")

# ---- Filter valid + SZA <= 90 ----
valid = np.isfinite(sza) & np.isfinite(ghi_int) & (sza <= 90)
sza = sza[valid]
ghi_int = ghi_int[valid]

# ---- SAVE integrated table ----
out_table = in_path.with_name("sza_calculation_with_integrated_ghi.csv")
df.loc[valid].to_csv(out_table, index=False)
print(f"Saved: {out_table}")

# =========================
# Figure 1: Scatter (raw)
# =========================
plt.figure(figsize=(8,5))
plt.scatter(sza, ghi_int, s=10, alpha=0.5, label="Samples")
plt.xlabel("Solar Zenith Angle (degrees)")
plt.ylabel("Integrated GHI (W/m²)")
plt.title("Integrated GHI vs Solar Zenith Angle (Raw Scatter)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

out_plot1 = fig_dir / "integrated_ghi_vs_sza_scatter.png"
plt.savefig(out_plot1, dpi=200)
print(f"Saved: {out_plot1}")
plt.close()

# =========================
# Figure 2: Line-like (binned mean)
# =========================
bin_width_deg = 1.0  # change bin width if needed
bins = np.arange(0, 91 + bin_width_deg, bin_width_deg)
tmp = pd.DataFrame({"sza": sza, "dni": ghi_int})
tmp["bin"] = pd.cut(tmp["sza"], bins=bins, include_lowest=True, right=False)

# Only keep bins with data
grouped = tmp.groupby("bin", observed=True)["dni"]
bin_mean = grouped.mean().to_numpy()
bin_centers = np.array([(b.left + b.right)/2 for b in grouped.groups.keys()])

plt.figure(figsize=(8,5))
plt.plot(bin_centers, bin_mean, linewidth=2.0, marker="o", markersize=3,
         label=f"Mean in {bin_width_deg:.0f}° bins")
plt.xlabel("Solar Zenith Angle (degrees)")
plt.ylabel("Integrated GHI (W/m²)")
plt.title("Integrated GHI vs Solar Zenith Angle (Binned Line)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

out_plot2 = fig_dir / "integrated_ghi_vs_sza_line.png"
plt.savefig(out_plot2, dpi=200)
print(f"Saved: {out_plot2}")
plt.close()
