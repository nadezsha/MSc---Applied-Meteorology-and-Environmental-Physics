import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the files (same code as you provided)
ten_sza = []
forty_sza = []
seventy_sza = []
eighty_five_sza = []

b_list = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

filename_ten = [f'4_10_{b}.out' for b in b_list]
filename_forty = [f'4_40_{b}.out' for b in b_list]
filename_seventy = [f'4_70_{b}.out' for b in b_list]
filename_eighty_five = [f'4_85_{b}.out' for b in b_list]

col_names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance',
             'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward',
             'uavgdiffuse upward']

for filename in filename_ten:
    file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
    ten_sza.append(file) 

for filename in filename_forty:
    file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
    forty_sza.append(file) 

for filename in filename_seventy:
    file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
    seventy_sza.append(file) 

for filename in filename_eighty_five:
    file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
    eighty_five_sza.append(file)  

# Add the 'global irradiance' column
for i in range(0, 6):
    ten_sza[i]['global'] = ten_sza[i]['direct horizontal irradiance'] + ten_sza[i]['diffuse downward horizontal irradiance']
    forty_sza[i]['global'] = forty_sza[i]['direct horizontal irradiance'] + forty_sza[i]['diffuse downward horizontal irradiance']
    seventy_sza[i]['global'] = seventy_sza[i]['direct horizontal irradiance'] + seventy_sza[i]['diffuse downward horizontal irradiance']
    eighty_five_sza[i]['global'] = eighty_five_sza[i]['direct horizontal irradiance'] + eighty_five_sza[i]['diffuse downward horizontal irradiance']

# Calculate ratios
def calculate_ratios(reference_df, target_list):
    reference_global = reference_df['global']
    reference_dhi = reference_df['direct horizontal irradiance']
    reference_diffuse = reference_df['diffuse downward horizontal irradiance']  
    
    global_ratios = []
    dhi_ratios = []
    diffuse_ratios = []

    for df in target_list:
        global_ratio = df['global'] / reference_global
        dhi_ratio = df['direct horizontal irradiance'] / reference_dhi
        diffuse_ratio = df['diffuse downward horizontal irradiance'] / reference_diffuse
        
        global_ratios.append(global_ratio)
        dhi_ratios.append(dhi_ratio)
        diffuse_ratios.append(diffuse_ratio)
    
    return global_ratios, dhi_ratios, diffuse_ratios

# Calculate ratios for each list, using the DataFrame with b=0.0 (index 0)
ten_sza_global_ratios, ten_sza_dhi_ratios, ten_sza_diffuse_ratios = calculate_ratios(ten_sza[0], ten_sza)
forty_sza_global_ratios, forty_sza_dhi_ratios, forty_sza_diffuse_ratios = calculate_ratios(forty_sza[0], forty_sza)
seventy_sza_global_ratios, seventy_sza_dhi_ratios, seventy_sza_diffuse_ratios = calculate_ratios(seventy_sza[0], seventy_sza)
eighty_five_sza_global_ratios, eighty_five_sza_dhi_ratios, eighty_five_sza_diffuse_ratios = calculate_ratios(eighty_five_sza[0], eighty_five_sza)

# Store these ratios in new columns in the DataFrames
for i, ratio in enumerate(ten_sza_global_ratios):
    ten_sza[i]['global_ratio'] = ratio
for i, ratio in enumerate(ten_sza_dhi_ratios):
    ten_sza[i]['dhi_ratio'] = ratio
for i, ratio in enumerate(ten_sza_diffuse_ratios):
    ten_sza[i]['diffuse_ratio'] = ratio

for i, ratio in enumerate(forty_sza_global_ratios):
    forty_sza[i]['global_ratio'] = ratio
for i, ratio in enumerate(forty_sza_dhi_ratios):
    forty_sza[i]['dhi_ratio'] = ratio
for i, ratio in enumerate(forty_sza_diffuse_ratios):
    forty_sza[i]['diffuse_ratio'] = ratio

for i, ratio in enumerate(seventy_sza_global_ratios):
    seventy_sza[i]['global_ratio'] = ratio
for i, ratio in enumerate(seventy_sza_dhi_ratios):
    seventy_sza[i]['dhi_ratio'] = ratio
for i, ratio in enumerate(seventy_sza_diffuse_ratios):
    seventy_sza[i]['diffuse_ratio'] = ratio

for i, ratio in enumerate(eighty_five_sza_global_ratios):
    eighty_five_sza[i]['global_ratio'] = ratio
for i, ratio in enumerate(eighty_five_sza_dhi_ratios):
    eighty_five_sza[i]['dhi_ratio'] = ratio
for i, ratio in enumerate(eighty_five_sza_diffuse_ratios):
    eighty_five_sza[i]['diffuse_ratio'] = ratio

# Define the wavelengths 
wavelength = ten_sza[0]['wavelength']  

# List of sza data (for different solar zenith angles)
sza_data = [ten_sza, forty_sza, seventy_sza, eighty_five_sza]
sza_titles = ['10° SZA', '40° SZA', '70° SZA', '85° SZA']

# Define a list of colors (you can change these colors as desired)
colors = ['b', 'g', 'r', 'c', 'm', 'y']

# List of irradiance types and corresponding columns for ratios
irradiance_types = ['global', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance']
irradiance_columns = ['global_ratio', 'dhi_ratio', 'diffuse_ratio']

# Create separate figures for each SZA (10°, 40°, 70°, 85°)
for sza_list, sza_title in zip(sza_data, sza_titles):
    # Create separate figures for each SZA
    for irradiance_type, column_name in zip(irradiance_types, irradiance_columns):
        plt.figure(figsize=(12, 8))  # Start a new figure for each SZA and irradiance type

        for i, b in enumerate(b_list):
            ratios = sza_list[i][column_name]  # Get the ratios for the selected irradiance type
            color = colors[i % len(colors)]  # Cycle colors for each b value

            # Plot the selected irradiance ratio for this SZA and b
            plt.plot(wavelength, ratios, label=f'{irradiance_type.capitalize()} b={b}', color=color, linestyle='-', linewidth=2)

        # Set plot labels and title
        plt.title(f"{irradiance_type.capitalize()} Ratios for {sza_title}")
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Irradiance Ratio')

        # Display the legend inside the plot area at the upper right with smaller font size
        plt.legend(loc='upper left', title="Radiative Quantities", fontsize=6, bbox_to_anchor=(1.05, 1), borderaxespad=0.)

        # Make sure the plot has tight layout
        plt.tight_layout()

        # Save the figure as a PNG file
        plt.savefig(f"{sza_title}_{irradiance_type}_values.png")
        plt.show()  # Show the plot for each SZA and irradiance type
