import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson

# Define the lists of sza values
sza = [20, 50, 80]

# Wavelength ranges for UVB, UVA, VIS, and IR
wavelength_ranges = {
    'UVB': (300, 320),
    'UVA': (320, 400),
    'VIS': (400, 700),
    'IR': (700, 1100)
}

# List of column names
col_names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance',
             'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 
             'uavgdiffuse downward', 'uavgdiffuse upward']

# Directory where the files are located
directory = "." 

# Function to integrate flux using Simpson's rule
def integrate_flux(df, flux_column, wavelength_range):
    mask = (df['wavelength'] >= wavelength_range[0]) & (df['wavelength'] <= wavelength_range[1])
    # Integrate the flux using Simpson's rule
    return simpson(df.loc[mask, flux_column], x=df.loc[mask, 'wavelength'])

# Loop through the combinations of sza and region (UVB, UVA, VIS, IR)
for sza_value in sza:
    for region, wavelength_range in wavelength_ranges.items():

        integral_direct = []
        integral_diffuse_down = []
        integral_global = []
        integral_actinic_flux = []
        tau_values = []

        # Process the corresponding files for each SZA and region
        for tau_value in [0, 5, 10, 15, 20, 30, 40, 50, 100, 150, 200]:
            # Generate file pattern for current SZA and tau_value
            file_pattern = f"{directory}/config_sza{sza_value}_tau{tau_value}.out"
            files = glob.glob(file_pattern)
            
            # If files are found, process them
            for file in files:
                df = pd.read_csv(file, sep=r'\s+', names=col_names, header=None)
                df['sza'] = sza_value
                df['tau'] = tau_value

                # Calculate Actinic Flux (uavgdirect + uavgdiffuse downward) * 4 * pi
                df['actinic_flux'] = (df['uavgdirect'] + df['uavgdiffuse downward']) * 4 * np.pi
                
                # Calculate Global Irradiance (direct + diffuse downward)
                df['global_irradiance'] = df['direct horizontal irradiance'] + df['diffuse downward horizontal irradiance']
                
                # Integrate flux over the given wavelength range for direct, diffuse downward, global, and actinic flux
                integral_direct.append(integrate_flux(df, 'direct horizontal irradiance', wavelength_range))
                integral_diffuse_down.append(integrate_flux(df, 'diffuse downward horizontal irradiance', wavelength_range))
                integral_global.append(integrate_flux(df, 'global_irradiance', wavelength_range))
                integral_actinic_flux.append(integrate_flux(df, 'actinic_flux', wavelength_range))
                
                # Add the corrected tau value (divide by 10)
                tau_values.append(tau_value / 10.0)

        # Plot the results for the current SZA and region
        plt.figure(figsize=(10, 6))

        # Plot the integrated curves for the 4 irradiance types 
        plt.plot(tau_values, integral_direct, label="Direct Irradiance", color='blue', linestyle='-', marker='o')
        plt.plot(tau_values, integral_diffuse_down, label="Diffuse Downward Irradiance", color='orange', linestyle='-', marker='o')
        plt.plot(tau_values, integral_global, label="Global Irradiance", color='green', linestyle='-', marker='o')
        plt.plot(tau_values, integral_actinic_flux, label="Actinic Flux", color='red', linestyle='-', marker='o')

        # Title and labels
        plt.title(f"SZA {sza_value}° and Region {region}")
        plt.xlabel("Optical Depth (τ)")
        plt.ylabel("Integrated Irradiance (W/m²)")
        plt.legend()
        plt.grid(True)

        # Save the figure
        plt.savefig(f"sza{sza_value}_region_{region}.png")
        
        # Show the plot
        plt.show()
