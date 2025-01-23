import glob
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Define the lists of sza, ssa, and angstrom values
sza = [10, 40, 70, 85]
ssa = [0.65, 0.75, 0.85, 0.95]
angstrom = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Directory where the files are located
directory = "." 

# List of column names for your data
col_names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance',
             'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward',
             'uavgdiffuse upward']

# List to store DataFrames for all files
all_data = []

# Generate the filenames by iterating over all combinations
for sza_value in sza:
    for ssa_value in ssa:
        for angstrom_value in angstrom:
            # Create the file pattern for the current combination
            file_pattern = f"{directory}/run_set_*_sza_{sza_value}_ssa_{ssa_value}_angstrom_{angstrom_value}.out"
            files = glob.glob(file_pattern)

            # If files are found, read and process them
            for file in files:
                df = pd.read_csv(file, sep=r'\s+', names=col_names, header=None)
                df['sza'] = sza_value
                df['ssa'] = ssa_value
                df['angstrom'] = angstrom_value
                all_data.append(df)

# Combine all DataFrames into one large DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Show a preview of the combined DataFrame
print(combined_df.head())

# Prepare the data for the ratios
# Direct Horizontal Irradiance
direct_irradiance = combined_df['direct horizontal irradiance']

# Diffuse Downward Horizontal Irradiance
diffuse_irradiance = combined_df['diffuse downward horizontal irradiance']

# Global Irradiance (sum of direct and diffuse)
global_irradiance = direct_irradiance + diffuse_irradiance

# Calculate the ratios based on angstrom = 0 (reference value)
# Initialize arrays for the ratios
ratio_direct_diffuse = np.zeros(len(combined_df))
ratio_direct_global = np.zeros(len(combined_df))
ratio_diffuse_global = np.zeros(len(combined_df))

# Create a dictionary to store values for angstrom = 0
reference_values = {}

# Loop over combinations of sza and ssa to extract reference values for angstrom = 0
for sza_value in sza:
    for ssa_value in ssa:
        # Filter data for the specific sza and ssa values and angstrom = 0
        ref_data = combined_df[(combined_df['sza'] == sza_value) & (combined_df['ssa'] == ssa_value) & (combined_df['angstrom'] == 0.0)]
        
        if not ref_data.empty:
            # Store the reference values for direct, diffuse, and global irradiance
            reference_values[(sza_value, ssa_value)] = {
                'direct': ref_data['direct horizontal irradiance'].values[0],
                'diffuse': ref_data['diffuse downward horizontal irradiance'].values[0],
                'global': ref_data['direct horizontal irradiance'].values[0] + ref_data['diffuse downward horizontal irradiance'].values[0]
            }

# Calculate the ratios for each combination of sza, ssa, and angstrom
for index, row in combined_df.iterrows():
    sza_value = row['sza']
    ssa_value = row['ssa']
    angstrom_value = row['angstrom']
    
    # Retrieve reference values for the current combination of sza and ssa
    if (sza_value, ssa_value) in reference_values:
        reference = reference_values[(sza_value, ssa_value)]
        direct_ref = reference['direct']
        diffuse_ref = reference['diffuse']
        global_ref = reference['global']
        
        # Calculate ratios
        if diffuse_ref != 0:
            ratio_direct_diffuse[index] = row['direct horizontal irradiance'] / diffuse_ref
        if global_ref != 0:
            ratio_direct_global[index] = row['direct horizontal irradiance'] / global_ref
            ratio_diffuse_global[index] = row['diffuse downward horizontal irradiance'] / global_ref

# Determine global min and max values for all ratios
ratio_min = min(np.min(ratio_direct_diffuse), np.min(ratio_direct_global), np.min(ratio_diffuse_global))
ratio_max = max(np.max(ratio_direct_diffuse), np.max(ratio_direct_global), np.max(ratio_diffuse_global))

# Create the 3D scatter plots
fig = plt.figure(figsize=(18, 6))

# Ratio of direct horizontal irradiance / diffuse downward horizontal irradiance
ax1 = fig.add_subplot(131, projection='3d')
scatter1 = ax1.scatter(combined_df['angstrom'], combined_df['ssa'], combined_df['sza'], c=ratio_direct_diffuse, cmap='jet', marker='o', vmin=ratio_min, vmax=ratio_max)
ax1.set_title('Direct / Diffuse Horizontal Irradiance')
ax1.set_xlabel('Angstrom')
ax1.set_ylabel('SSA')
ax1.set_zlabel('SZA')
fig.colorbar(scatter1, ax=ax1, label='Ratio')  # Add color bar for ratio values

# Ratio of direct horizontal irradiance / global horizontal irradiance
ax2 = fig.add_subplot(132, projection='3d')
scatter2 = ax2.scatter(combined_df['angstrom'], combined_df['ssa'], combined_df['sza'], c=ratio_direct_global, cmap='jet', marker='o', vmin=ratio_min, vmax=ratio_max)
ax2.set_title('Direct / Global Horizontal Irradiance')
ax2.set_xlabel('Angstrom')
ax2.set_ylabel('SSA')
ax2.set_zlabel('SZA')
fig.colorbar(scatter2, ax=ax2, label='Ratio')  # Add color bar for ratio values

# Ratio of diffuse downward horizontal irradiance / global horizontal irradiance
ax3 = fig.add_subplot(133, projection='3d')
scatter3 = ax3.scatter(combined_df['angstrom'], combined_df['ssa'], combined_df['sza'], c=ratio_diffuse_global, cmap='jet', marker='o', vmin=ratio_min, vmax=ratio_max)
ax3.set_title('Diffuse / Global Horizontal Irradiance')
ax3.set_xlabel('Angstrom')
ax3.set_ylabel('SSA')
ax3.set_zlabel('SZA')
fig.colorbar(scatter3, ax=ax3, label='Ratio')  # Add color bar for ratio values

# Save the figure
plt.tight_layout()
plt.savefig("irradiance_ratios_3d_scatter_plots.png", dpi=300)  

# Show the plots
plt.show()
