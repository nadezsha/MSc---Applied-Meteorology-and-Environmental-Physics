import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read the files
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
	
''' Each list contains 6 DataFrames. Every DataFrame contains values for a different b.'''
#print(ten_sza)

# adding the 'global irradiance' column on all DataFrames
for i in range(0,6):
	ten_sza[i]['global'] = ten_sza[i]['direct horizontal irradiance'] + ten_sza[i]['diffuse downward horizontal irradiance']
	forty_sza[i]['global'] = forty_sza[i]['direct horizontal irradiance'] + forty_sza[i]['diffuse downward horizontal irradiance']
	seventy_sza[i]['global'] = seventy_sza[i]['direct horizontal irradiance'] + seventy_sza[i]['diffuse downward horizontal irradiance']
	eighty_five_sza[i]['global'] = eighty_five_sza[i]['direct horizontal irradiance'] + eighty_five_sza[i]['diffuse downward horizontal irradiance']
	
# create a function to calculate the ratios for each DataFrame in the list
def calculate_ratios(reference_df, target_list):
    reference_global = reference_df['global']  # extract the global irradiance for b = 0.0
    ratios = []
    
    for df in target_list:
        ratio = df['global'] / reference_global  # calculate the ratio
        ratios.append(ratio)
    
    return ratios

# calculate ratios for each list, using the DataFrame with b = 0.0 (index 0)
def calculate_ratios(reference_df, target_list):
    reference_global = reference_df['global'] 
    reference_dhi = reference_df['direct horizontal irradiance']
    reference_diffuse = reference_df['diffuse downward horizontal irradiance']  
    
    global_ratios = []
    dhi_ratios = []
    diffuse_ratios = []

    # iterate through each DataFrame in the target list and calculate the ratios
    for df in target_list:
        global_ratio = df['global'] / reference_global
        dhi_ratio = df['direct horizontal irradiance'] / reference_dhi
        diffuse_ratio = df['diffuse downward horizontal irradiance'] / reference_diffuse
        
        global_ratios.append(global_ratio)
        dhi_ratios.append(dhi_ratio)
        diffuse_ratios.append(diffuse_ratio)
    
    return global_ratios, dhi_ratios, diffuse_ratios

# calculate ratios for each list, using the DataFrame with b=0.0 (index 0)
ten_sza_global_ratios, ten_sza_dhi_ratios, ten_sza_diffuse_ratios = calculate_ratios(ten_sza[0], ten_sza)
forty_sza_global_ratios, forty_sza_dhi_ratios, forty_sza_diffuse_ratios = calculate_ratios(forty_sza[0], forty_sza)
seventy_sza_global_ratios, seventy_sza_dhi_ratios, seventy_sza_diffuse_ratios = calculate_ratios(seventy_sza[0], seventy_sza)
eighty_five_sza_global_ratios, eighty_five_sza_dhi_ratios, eighty_five_sza_diffuse_ratios = calculate_ratios(eighty_five_sza[0], eighty_five_sza)

# store these ratios in new columns in the DataFrames
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

# print the results to check the output
#for i in range(6):
#    print(f"Ten SZA - b = {b_list[i]}:\n", ten_sza[i].head())

# define the wavelengths 
wavelength = ten_sza[0]['wavelength']  

# list of sza data (for different solar zenith angles)
sza_data = [ten_sza, forty_sza, seventy_sza, eighty_five_sza]
sza_titles = ['10° SZA', '40° SZA', '70° SZA', '85° SZA']

# iterate through each sza
for sza_list, sza_title in zip(sza_data, sza_titles):
    # iterate over each b value (b = 0.0, 0.2, 0.4, 0.6, 0.8)
    for i, b in enumerate(b_list):
        # create a new plot for each b value
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # extract the ratios for global, direct, and diffused for the given sza and b value
        global_ratios = sza_list[i]['global_ratio']
        dhi_ratios = sza_list[i]['dhi_ratio']
        diffuse_ratios = sza_list[i]['diffuse_ratio']
        
        # plot the three radiative quantities for this b value
        ax.plot(wavelength, global_ratios, label=f'Global Irradiance (b={b})', linestyle='-', color='blue')
        ax.plot(wavelength, dhi_ratios, label=f'Direct Horizontal Irradiance (b={b})', linestyle='-', color='red')
        ax.plot(wavelength, diffuse_ratios, label=f'Diffuse Downward Irradiance (b={b})', linestyle='-', color='green')

        ax.set_title(f'{sza_title} , b = {b}')
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Irradiance Ratio')
        ax.legend(loc='upper left', title="Radiative Quantities")
        ax.grid(True)

        # Adjust layout to ensure no clipping of labels
        fig.tight_layout()

        # Save the plot to a file
        plt.savefig(f"{sza_title.replace('°', '').replace(' ', '_')}_b_{b}.png")

        # Display the plot 
        # plt.show()