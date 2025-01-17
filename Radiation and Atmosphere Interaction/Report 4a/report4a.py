import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

# Read the files
ten_sza = []
thirty_sza = []
seventy_sza = []

spline_list = ['320_320', '440_440', '550_550', '675_675', '936_936']

filename_ten = [f'sza10_spline{spline}_10.out' for spline in spline_list]
filename_thirty = [f'sza30_spline{spline}_10.out' for spline in spline_list]
filename_seventy = [f'sza70_spline{spline}_10.out' for spline in spline_list]

col_names = ['theta', 'no_phi', '0', '10', '20', '30', '40', '50', '60', '70',
             '80', '90', '100', '110', '120', '130', '140', '150', '160', '170', '180']

# Function to add symmetric columns (mirror columns from 0-180 to 190-360)
def add_symmetric_columns(df):
    # Loop over the columns from 0 to 180 and mirror them to 190 to 360
    for i in range(0, 181, 10):  # Loop through columns from 0 to 180
        symmetric_col = 360 - i  # Calculate the symmetric column index (360 - i)
        df[symmetric_col] = df[str(i)]  # Assign the value of column 'i' to its symmetric counterpart
    return df

# Function to create polar plots with color scale for a specific SZA
def create_polar_plot_for_sza(sza_df, sza_value, spline_value):
    # Create a subplot for polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))

    # Get theta (in radians) and the values for the SZA
    theta = np.radians(sza_df['theta'])
    radii = sza_df.drop(columns=['theta', 'no_phi'])  # Drop non-relevant columns
    
    # Interpolate the data to get a smooth transition from 0° to 360°
    theta_full = np.linspace(0, 360, 37)  # 37 values from 0° to 360° (including symmetry)
    radii_full = np.zeros((len(theta_full), len(radii.columns)))

    # For each SZA column, interpolate the data and map to the full range
    for i, column in enumerate(radii.columns):
        f = interpolate.interp1d(np.radians(sza_df['theta']), radii[column], kind='linear', fill_value="extrapolate")
        radii_full[:, i] = f(np.radians(theta_full))

    # Plot using pcolormesh (with color scale)
    c = ax.pcolormesh(np.radians(theta_full), np.arange(len(radii.columns)), radii_full.T, cmap='viridis', shading='auto')

    # Add color bar
    fig.colorbar(c, ax=ax, label='Radiance Intensity')

    # Set plot title and labels
    ax.set_title(f'Polar Plot for Spline {spline_value}, SZA {sza_value}')
    ax.set_xlabel('Theta (Degrees)')
    ax.set_ylabel('Radiance')

    # Set theta ticks (every 30 degrees), starting from the top
    ax.set_xticks(np.radians(np.arange(0, 360, 30)))
    ax.set_xticklabels([f'{i}°' for i in range(0, 360, 30)])

    # Rotate the plot to make 0° at the top and angles increasing clockwise
    ax.set_theta_zero_location('N')  # Move 0° to the top
    ax.set_theta_direction(-1)  # Set angles to increase clockwise

    # Show the plot
    plt.tight_layout()
    plt.show()

# Read the files and add symmetric columns
for filename in filename_ten:
    try:
        file = pd.read_csv(filename, delimiter=r"\s+", names=col_names, skiprows=10)
        file = add_symmetric_columns(file)  # Add mirrored columns
        ten_sza.append(file)
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

for filename in filename_thirty:
    try:
        file = pd.read_csv(filename, delimiter=r"\s+", names=col_names, skiprows=10)
        file = add_symmetric_columns(file)  # Add mirrored columns
        thirty_sza.append(file)
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

for filename in filename_seventy:
    try:
        file = pd.read_csv(filename, delimiter=r"\s+", names=col_names, skiprows=10)
        file = add_symmetric_columns(file)  # Add mirrored columns
        seventy_sza.append(file)
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

# Combine SZA data for each spline (10, 30, and 70) into a dictionary for each SZA
for idx, spline_value in enumerate(spline_list):
    # Each SZA gets a separate plot
    sza_data = {
        "10": ten_sza[idx],
        "30": thirty_sza[idx],
        "70": seventy_sza[idx]
    }

    # Create separate polar plots for each SZA
    for sza_value, sza_df in sza_data.items():
        create_polar_plot_for_sza(sza_df, sza_value, spline_value)
