import pandas as pd
import numpy as np

from pathlib import Path

row_idx = 100  # for example

df = pd.read_csv(r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\data\helmos\eko-ms711-dni-helmos\2024\sza_calculation\sza_calculation_with_integrated_dni.csv")

# find wavelength columns
wl_cols = []
for col in df.columns:
    try:
        float(col)
        wl_cols.append(col)
    except ValueError:
        pass

wl_vals = np.array([float(c) for c in wl_cols])
mask = (wl_vals >= 400) & (wl_vals <= 1100)
wl_vals = wl_vals[mask]
wl_cols = [str(int(w)) for w in wl_vals]

row = df.iloc[row_idx]
spec = row[wl_cols].to_numpy(float)
spec_int = np.trapz(spec, wl_vals)

dni_int = float(row["DNI_integrated_Wm2"])

print("Example row:", row_idx)
print("  Integrated spectral (raw units):", spec_int)
print("  DNI_integrated_Wm2:", dni_int)
print("  Ratio spec_int / DNI_integrated_Wm2 =", spec_int / dni_int)
