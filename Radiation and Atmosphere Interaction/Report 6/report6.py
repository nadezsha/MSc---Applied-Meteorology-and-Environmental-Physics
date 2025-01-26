import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

# Data containers for part 1, part 2, and part zero
sza_20_part1 = [] # τ = 2
sza_70_part1 = []
sza_20_part2 = [] # τ = 5
sza_70_part2 = []
sza_20_part_zero = []  # τ = 0
sza_70_part_zero = []

zout_values = range(9)  
sza_values = [20, 70]

col_names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance',
             'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward',
             'uavgdiffuse upward']

# Wavelength ranges for different regions
ranges = {
    'UVB': (300, 320),
    'UVA': (320, 400),
    'VIS': (400, 700),
    'IR': (700, 1100)
}

# Read files for SZA 20 and SZA 70
for zout in zout_values:
    for sza in sza_values:
        # Read part 1 file
        filename_part1 = f'input_zout{zout}_sza{sza}.out'
        file_part1 = pd.read_csv(filename_part1, delimiter=r"\s+", names=col_names)
        
        # Calculate actinic flux 2π for part 1
        file_part1['actinic_flux'] = (file_part1['uavgdirect'] + file_part1['uavgdiffuse downward']) * 4 * np.pi
        file_part1['global_irradiance'] = file_part1['direct horizontal irradiance'] + file_part1['diffuse downward horizontal irradiance']
        
        if sza == 20:
            sza_20_part1.append(file_part1)
        elif sza == 70:
            sza_70_part1.append(file_part1)
        
        # Process part 2
        filename_part2 = f'input_zout{zout}_sza{sza}_part2.out'
        file_part2 = pd.read_csv(filename_part2, delimiter=r"\s+", names=col_names)
        
        # Calculate actinic flux 2π for part 2
        file_part2['actinic_flux'] = (file_part2['uavgdirect'] + file_part2['uavgdiffuse downward']) * 4 * np.pi
        file_part2['global_irradiance'] = file_part2['direct horizontal irradiance'] + file_part2['diffuse downward horizontal irradiance']
        
        if sza == 20:
            sza_20_part2.append(file_part2)
        elif sza == 70:
            sza_70_part2.append(file_part2)

        # Process part_zero
        filename_part_zero = f'input_zout{zout}_sza{sza}_part_zero.out'
        file_part_zero = pd.read_csv(filename_part_zero, delimiter=r"\s+", names=col_names)
        
        # Calculate actinic flux 2π for part_zero
        file_part_zero['actinic_flux'] = (file_part_zero['uavgdirect'] + file_part_zero['uavgdiffuse downward']) * 4 * np.pi
        file_part_zero['global_irradiance'] = file_part_zero['direct horizontal irradiance'] + file_part_zero['diffuse downward horizontal irradiance']
        
        if sza == 20:
            sza_20_part_zero.append(file_part_zero)
        elif sza == 70:
            sza_70_part_zero.append(file_part_zero)

# Calculate the integration 
region_integrals = {}

# Function to calculate integrals for a given data set
def calculate_integrals(sza_data):
    region_integrals = {}
    for region, (min_wavelength, max_wavelength) in ranges.items():
        # Filter the data for the current region
        region_data = sza_data[(sza_data['wavelength'] >= min_wavelength) & (sza_data['wavelength'] <= max_wavelength)]
        
        # Integrate the relevant columns for each region
        region_integrals[region] = {
            'direct_irradiance': np.trapz(region_data['direct horizontal irradiance'], region_data['wavelength']),
            'diffuse_downward_irradiance': np.trapz(region_data['diffuse downward horizontal irradiance'], region_data['wavelength']),
            'actinic_flux': np.trapz(region_data['actinic_flux'], region_data['wavelength']),
            'global_irradiance': np.trapz(region_data['global_irradiance'], region_data['wavelength'])
        }
    return region_integrals

# Calculate integrals 
integrals_part1_sza20 = []
integrals_part1_sza70 = []
integrals_part2_sza20 = []
integrals_part2_sza70 = []
integrals_part_zero_sza20 = [] 
integrals_part_zero_sza70 = []  

# Calculate integrals for part 1 (SZA 20 and SZA 70)
for file in sza_20_part1:
    integrals_part1_sza20.append(calculate_integrals(file))
for file in sza_70_part1:
    integrals_part1_sza70.append(calculate_integrals(file))

# Calculate integrals for part 2 (SZA 20 and SZA 70)
for file in sza_20_part2:
    integrals_part2_sza20.append(calculate_integrals(file))
for file in sza_70_part2:
    integrals_part2_sza70.append(calculate_integrals(file))

# Calculate integrals for part_zero (SZA 20 and SZA 70)
for file in sza_20_part_zero:
    integrals_part_zero_sza20.append(calculate_integrals(file))
for file in sza_70_part_zero:
    integrals_part_zero_sza70.append(calculate_integrals(file))

# Radiative quantities to plot
radiative_quantities = ['direct_irradiance', 'diffuse_downward_irradiance', 'actinic_flux', 'global_irradiance']
regions = ['UVB', 'UVA', 'VIS', 'IR']

# Function to plot integrals for a specific quantity, SZA, and region
def plot_integrals_for_region_and_sza(region, sza, part1_integrals, part2_integrals, part_zero_integrals, radiative_quantity):
    plt.figure(figsize=(10, 6))
    
    # Plot for part 1
    part1_values = [integrals[region][radiative_quantity] for integrals in part1_integrals]
    plt.plot(range(len(part1_values)), part1_values, label=f'τ = 5.0', color='green', marker='o')
    
    # Plot for part 2
    part2_values = [integrals[region][radiative_quantity] for integrals in part2_integrals]
    plt.plot(range(len(part2_values)), part2_values, label=f'τ = 2.0', color='red', marker='o')

    # Plot for part_zero
    part_zero_values = [integrals[region][radiative_quantity] for integrals in part_zero_integrals]
    plt.plot(range(len(part_zero_values)), part_zero_values, label=f'τ = 0.0', color='blue', marker='o')
    
    # Adding labels and title (same style as before)
    plt.title(f'{radiative_quantity.replace("_", " ").title()} for {region} - sza {sza}')
    plt.xlabel('Altitude (km)')
    plt.ylabel(f'{radiative_quantity.replace("_", " ").title()} (W/m²)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{radiative_quantity}_{region}_SZA{sza}.png')
    plt.show()

# Loop through each SZA, region, and radiative quantity to create the plots
for sza in sza_values:
    for region in regions:
        for radiative_quantity in radiative_quantities:
            # Get part 1, part 2, and part_zero integrals for the current SZA and region
            if sza == 20:
                part1_integrals = integrals_part1_sza20
                part2_integrals = integrals_part2_sza20
                part_zero_integrals = integrals_part_zero_sza20 
            elif sza == 70:
                part1_integrals = integrals_part1_sza70
                part2_integrals = integrals_part2_sza70
                part_zero_integrals = integrals_part_zero_sza70  
                
            # Plot the integrals for the current combination
            plot_integrals_for_region_and_sza(region, sza, part1_integrals, part2_integrals, part_zero_integrals, radiative_quantity)
