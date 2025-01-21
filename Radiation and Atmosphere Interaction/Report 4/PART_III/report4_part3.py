import pandas as pd
import matplotlib.pyplot as plt

# read the files
ten_sza = []
forty_sza = []
seventy_sza = []
eighty_five_sza = []

gg_list = ['0.50', '0.70', '0.90']

filename_ten = [f'4_10_{gg}.out' for gg in gg_list]
filename_forty = [f'4_40_{gg}.out' for gg in gg_list]
filename_seventy = [f'4_70_{gg}.out' for gg in gg_list]
filename_eighty_five = [f'4_85_{gg}.out' for gg in gg_list]

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
	
	
''' Each list contains 3 DataFrames where each DataFrame contains values for a different gg.'''
# adding the 'global irradiance' column on all DataFrames
for i in range(0,3):
	ten_sza[i]['global'] = ten_sza[i]['direct horizontal irradiance'] + ten_sza[i]['diffuse downward horizontal irradiance']
	forty_sza[i]['global'] = forty_sza[i]['direct horizontal irradiance'] + forty_sza[i]['diffuse downward horizontal irradiance']
	seventy_sza[i]['global'] = seventy_sza[i]['direct horizontal irradiance'] + seventy_sza[i]['diffuse downward horizontal irradiance']
	eighty_five_sza[i]['global'] = eighty_five_sza[i]['direct horizontal irradiance'] + eighty_five_sza[i]['diffuse downward horizontal irradiance']

# calculate ratios relative to gg 0.90 for each gg 
index_0_70 = gg_list.index('0.70')

ten_ref_direct = ten_sza[index_0_70]['direct horizontal irradiance']
forty_ref_direct = forty_sza[index_0_70]['direct horizontal irradiance']
seventy_ref_direct = seventy_sza[index_0_70]['direct horizontal irradiance']
eighty_five_ref_direct = eighty_five_sza[index_0_70]['direct horizontal irradiance']

ten_ref_diffuse = ten_sza[index_0_70]['diffuse downward horizontal irradiance']
forty_ref_diffuse = forty_sza[index_0_70]['diffuse downward horizontal irradiance']
seventy_ref_diffuse = seventy_sza[index_0_70]['diffuse downward horizontal irradiance']
eighty_five_ref_diffuse = eighty_five_sza[index_0_70]['diffuse downward horizontal irradiance']

ten_ref_global = ten_sza[index_0_70]['global']
forty_ref_global = forty_sza[index_0_70]['global']
seventy_ref_global = seventy_sza[index_0_70]['global']
eighty_five_ref_global = eighty_five_sza[index_0_70]['global']

# calculate the ratios for direct, diffuse downward and global irradiance relative to gg 0.70
for i in range(0, 3):
    # Direct irradiance ratio
    ten_sza[i]['direct_ratio'] = ten_sza[i]['direct horizontal irradiance'] / ten_ref_direct
    forty_sza[i]['direct_ratio'] = forty_sza[i]['direct horizontal irradiance'] / forty_ref_direct
    seventy_sza[i]['direct_ratio'] = seventy_sza[i]['direct horizontal irradiance'] / seventy_ref_direct
    eighty_five_sza[i]['direct_ratio'] = eighty_five_sza[i]['direct horizontal irradiance'] / eighty_five_ref_direct
    
    # Diffuse downward irradiance ratio
    ten_sza[i]['diffuse_ratio'] = ten_sza[i]['diffuse downward horizontal irradiance'] / ten_ref_diffuse
    forty_sza[i]['diffuse_ratio'] = forty_sza[i]['diffuse downward horizontal irradiance'] / forty_ref_diffuse
    seventy_sza[i]['diffuse_ratio'] = seventy_sza[i]['diffuse downward horizontal irradiance'] / seventy_ref_diffuse
    eighty_five_sza[i]['diffuse_ratio'] = eighty_five_sza[i]['diffuse downward horizontal irradiance'] / eighty_five_ref_diffuse
    
    # Global irradiance ratio
    ten_sza[i]['global_ratio'] = ten_sza[i]['global'] / ten_ref_global
    forty_sza[i]['global_ratio'] = forty_sza[i]['global'] / forty_ref_global
    seventy_sza[i]['global_ratio'] = seventy_sza[i]['global'] / seventy_ref_global
    eighty_five_sza[i]['global_ratio'] = eighty_five_sza[i]['global'] / eighty_five_ref_global
	
# Function to generate and save plots for a single sza and gg combination
def plot_and_save_irradiance_ratios(sza_data, sza_angle, gg, gg_index):
    plt.figure(figsize=(10, 6))

    # Plot Direct Irradiance Ratio
    plt.plot(sza_data[gg_index]['wavelength'], sza_data[gg_index]['direct_ratio'], label='Direct Irradiance', linestyle='-', color='blue')

    # Plot Diffuse Downward Irradiance Ratio
    plt.plot(sza_data[gg_index]['wavelength'], sza_data[gg_index]['diffuse_ratio'], label='Diffuse Downward Irradiance', linestyle='-', color='green')

    # Plot Global Irradiance Ratio
    plt.plot(sza_data[gg_index]['wavelength'], sza_data[gg_index]['global_ratio'], label='Global Irradiance', linestyle='-', color='red')

    # Title and Labels
    plt.title(f'{sza_angle}° SZA and (gg = {gg})')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Irradiance Ratio')
    plt.legend(loc='upper left', fontsize=8)
    plt.grid(True)
    
    # Save the figure with a unique filename based on sza and gg
    plt.tight_layout()
    plt.savefig(f'irradiance_ratios_{sza_angle}deg_gg_{gg}.png')
    plt.close()

# Create and save plots for each SZA and SSA combination
for i, sza_angle in enumerate([10, 40, 70, 85]):
    for j, gg in enumerate(gg_list):
        if sza_angle == 10:
            plot_and_save_irradiance_ratios(ten_sza, sza_angle, gg, j)
        elif sza_angle == 40:
            plot_and_save_irradiance_ratios(forty_sza, sza_angle, gg, j)
        elif sza_angle == 70:
            plot_and_save_irradiance_ratios(seventy_sza, sza_angle, gg, j)
        elif sza_angle == 85:
            plot_and_save_irradiance_ratios(eighty_five_sza, sza_angle, gg, j)

# Combined Plot for Each SZA Angle
def combined_plot_for_sza(sza_data, sza_angle, gg_list):
    plt.figure(figsize=(12, 8))

    # Loop over GG list to plot the data
    for j, gg in enumerate(gg_list):
        # Plot Direct Irradiance Ratio (blue solid line)
        plt.plot(sza_data[j]['wavelength'], sza_data[j]['direct_ratio'], label=f'gg={gg} (Direct)', color='blue', linestyle='-', alpha=0.7)
        
        # Plot Diffuse Downward Irradiance Ratio (green solid line)
        plt.plot(sza_data[j]['wavelength'], sza_data[j]['diffuse_ratio'], label=f'gg={gg} (Diffuse)', color='green', linestyle='-', alpha=0.7)
        
        # Plot Global Irradiance Ratio (red solid line)
        plt.plot(sza_data[j]['wavelength'], sza_data[j]['global_ratio'], label=f'gg={gg} (Global)', color='red', linestyle='-', alpha=0.7)

    # Title and Labels
    plt.title(f'Irradiance Ratios for {sza_angle}° SZA')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Irradiance Ratio')

    # Display the legend
    plt.legend(loc='upper right', fontsize=8, bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.grid(True)

    # Save the combined plot for this SZA angle
    plt.tight_layout()
    plt.savefig(f'combined_irradiance_ratios_{sza_angle}deg.png')
    plt.show()

# Create and save combined plots for each SZA angle
for i, sza_angle in enumerate([10, 40, 70, 85]):
    if sza_angle == 10:
        combined_plot_for_sza(ten_sza, sza_angle, gg_list)
    elif sza_angle == 40:
        combined_plot_for_sza(forty_sza, sza_angle, gg_list)
    elif sza_angle == 70:
        combined_plot_for_sza(seventy_sza, sza_angle, gg_list)
    elif sza_angle == 85:
        combined_plot_for_sza(eighty_five_sza, sza_angle, gg_list)
