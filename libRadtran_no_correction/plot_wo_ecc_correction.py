import pandas as pd
import matplotlib.pyplot as plt
import os

# File paths
epanomi_file = "./data/epanomi_integrated_irradiance_by_sza.csv"
helmos_file = "./data/helmos_integrated_irradiance_by_sza.csv"

# Read CSVs
epanomi = pd.read_csv(epanomi_file)
helmos = pd.read_csv(helmos_file)

# Convert only irradiance columns from mW to W
for df in [epanomi, helmos]:
    df["total_global_horiz"] /= 1000  # GHI
    df["dni_reconstructed"] /= 1000   # DNI
    df["total_diffuse_down_horiz"] /= 1000  # DHI

# Create "figures" directory
figures_dir = "./figures"
os.makedirs(figures_dir, exist_ok=True)

# Plot
plt.figure(figsize=(10,6))

# Epanomi (blue tones)
plt.plot(epanomi["sza_deg"], epanomi["total_global_horiz"], label="Epanomi GHI", color="blue")
plt.plot(epanomi["sza_deg"], epanomi["dni_reconstructed"], label="Epanomi DNI", color="navy")
plt.plot(epanomi["sza_deg"], epanomi["total_diffuse_down_horiz"], label="Epanomi DHI", color="skyblue")

# Helmos (pink tones)
plt.plot(helmos["sza_deg"], helmos["total_global_horiz"], label="Helmos GHI", color="deeppink")
plt.plot(helmos["sza_deg"], helmos["dni_reconstructed"], label="Helmos DNI", color="darkred")
plt.plot(helmos["sza_deg"], helmos["total_diffuse_down_horiz"], label="Helmos DHI", color="lightpink")

# Formatting
plt.xlabel("SZA (deg)")
plt.ylabel("Irradiance (W/m²)")
plt.title("GHI, DNI, DHI vs SZA for Epanomi and Helmos")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Save figure
fig_path = os.path.join(figures_dir, "irradiance_comparison.png")
plt.savefig(fig_path, dpi=300)
plt.close()

print("Figure saved at:", fig_path)