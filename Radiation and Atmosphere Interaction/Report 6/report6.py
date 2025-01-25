import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  

sza_20 = []
sza_70 = []

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
        filename = f'input_zout{zout}_sza{sza}_part2.out'
        file = pd.read_csv(filename, delimiter=r"\s+", names=col_names)
        
        # Calculate actinic flux 2π
        file['actinic_flux'] = (file['uavgdirect'] + file['uavgdiffuse downward']) * 4 * np.pi
        
        # Calculate global irradiance (direct + diffuse downward)
        file['global_irradiance'] = file['direct horizontal irradiance'] + file['diffuse downward horizontal irradiance']
        
        # Store the DataFrame based on SZA value
        if sza == 20:
            sza_20.append(file)
        elif sza == 70:
            sza_70.append(file)
        
        # Calculate sums for each region (UVB, UVA, VIS, IR)
        region_sums = {}
        for region, (min_wavelength, max_wavelength) in ranges.items():
            # Filter the file for the current wavelength range
            region_data = file[(file['wavelength'] >= min_wavelength) & (file['wavelength'] <= max_wavelength)]
            
            # Sum the relevant columns for each region
            region_sums[region] = {
                'direct_sum': region_data['direct horizontal irradiance'].sum(),
                'diffuse_downward_sum': region_data['diffuse downward horizontal irradiance'].sum(),
                'actinic_flux_sum': region_data['actinic_flux'].sum(),
                'global_irradiance_sum': region_data['global_irradiance'].sum()
            }
        
# Plotting the results for each SZA and Region
regions = ['UVB', 'UVA', 'VIS', 'IR']
radiative_quantities = ['direct_sum', 'diffuse_downward_sum', 'actinic_flux_sum', 'global_irradiance_sum']

# Iterate over each region and each SZA, and plot the corresponding values
for region in regions:
    for sza in sza_values:
        if sza == 20:
            sza_data = sza_20
        else:
            sza_data = sza_70
        
        # Collect sums for the current region and SZA
        direct_sums = []
        diffuse_sums = []
        flux_sums = []
        global_sums = []
        
        for file in sza_data:
            # Filter the file for the current region
            region_data = file[(file['wavelength'] >= ranges[region][0]) & (file['wavelength'] <= ranges[region][1])]
            
            # Append the calculated sums for each radiative quantity
            direct_sums.append(region_data['direct horizontal irradiance'].sum())
            diffuse_sums.append(region_data['diffuse downward horizontal irradiance'].sum())
            flux_sums.append(region_data['actinic_flux'].sum())
            global_sums.append(region_data['global_irradiance'].sum())
        
        # Create a figure for each plot
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(sza_data)), direct_sums, label='Direct Irradiance', color='blue')
        plt.plot(range(len(sza_data)), diffuse_sums, label='Diffuse Downward Irradiance', color='green')
        plt.plot(range(len(sza_data)), flux_sums, label='Actinic Flux', color='red')
        plt.plot(range(len(sza_data)), global_sums, label='Global Irradiance', color='orange')
        plt.title(f'{region} - SZA {sza}')
        plt.xlabel('zout')
        plt.ylabel('Radiative Quantities (W/m²)')
        plt.legend()
        plt.grid(True)  
        plt.savefig(f'part2_{region}_{sza}.png')
        plt.show()
