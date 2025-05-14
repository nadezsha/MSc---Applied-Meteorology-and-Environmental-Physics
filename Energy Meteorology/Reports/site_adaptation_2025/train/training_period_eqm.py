import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

# Reading the data file
data = pd.read_csv('Train_Kiruna.txt', sep=" ")
#print(data)

# Defining percentiles
num = list(np.arange(0, 100, 0.5))

##### Functions #####

def initial_graph(obs, mod, radiation_type):
    output_dir = "training_period_eqm_figures"
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(10, 10))
    plt.plot(obs, num, color='red', label=f'Observed Data [W/m²]')
    plt.plot(mod, num, color='blue', label=f'Modeled Data [W/m²]')

    plt.ylabel("Cumulative Probability [%]")
    plt.xlabel('f{radiation_type} [W/m²]')
    plt.title(f'Initial Plotting of the Training Dataset - {radiation_type}')
    plt.grid()
    plt.legend()

    plot_filename = os.path.join(output_dir, f"training_plot_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()


def calculate_metrics(mod, obs):
    # Ensure inputs are numpy arrays
    mod = np.array(mod)
    obs = np.array(obs)

    # Mean Bias Error
    mbe = np.mean(mod - obs)

    # Root Mean Square Error
    rmse = np.sqrt(mean_squared_error(obs, mod))

    # Pearson correlation coefficient (R)
    r, _ = pearsonr(obs, mod)
    r2 = r**2

    return mbe, rmse, r2


def interpolation(modper, obsper, mod, radiation_type):
    output_dir = "training_period_eqm_figures"
    os.makedirs(output_dir, exist_ok=True)

    # Ensure modper is strictly increasing
    modper_fixed, unique_indices = np.unique(modper, return_index=True)
    obsper_fixed_interp = obsper[unique_indices]

    interpolation = interp1d(modper_fixed, obsper_fixed_interp, kind='linear', fill_value="extrapolate", bounds_error=False)
    corrected = interpolation(mod)

    # Remove any NaNs before plotting/metrics
    valid_idx = ~np.isnan(corrected)
    corrected_valid = corrected[valid_idx]
    mod_valid = mod[valid_idx]
    obs_valid = np.array(data[f'{radiation_type}obs'])[valid_idx]  

    plt.figure(figsize=(10, 10))
    interper = np.percentile(corrected_valid, num)
    modper = np.percentile(mod, num)
    plt.plot(obsper, num, label="Observed Data [W/m²]", color='red')
    plt.plot(interper, num, label="Modeled-Corrected Data [W/m²]", color='green')
    plt.plot(modper, num, label='Modeled', color='blue')


    plt.xlabel(f'{radiation_type}  [W/m²]')
    plt.ylabel("Cumulative Probability [%]")
    plt.title(f'Corrected Modeled values vs Original Modeled values - {radiation_type}')
    plt.grid()
    plt.legend()

    plot_filename = os.path.join(output_dir, f"modcor_vs_mod_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()

    return corrected


##### Main Code #####

# step 1 : initial visualisation 
obsGHI = np.percentile(data['GHIobs'], num)
modGHI = np.percentile(data['GHImod'], num)
initial_graph(obsGHI, modGHI, 'GHI')
mbe_ghi, rmse_ghi, r_ghi = calculate_metrics(data['GHImod'], data['GHIobs'])
print(f"GHI → MBE: {mbe_ghi:.2f}, RMSE: {rmse_ghi:.2f}, R²: {r_ghi:.3f}")

obsDNI = np.percentile(data['DNIobs'], num)
modDNI = np.percentile(data['DNImod'], num)
initial_graph(obsDNI, modDNI, 'DNI')
mbe_dni, rmse_dni, r_dni = calculate_metrics(data['DNImod'], data['DNIobs'])
print(f"DNI → MBE: {mbe_dni:.2f}, RMSE: {rmse_dni:.2f}, R²: {r_dni:.3f}")

# step 2 : linear interpolation
print(" ")
ghi_cor = interpolation(modGHI, obsGHI, data['GHImod'], 'GHI')
mbe_ghi_new, rmse_ghi_new, r_ghi_new = calculate_metrics(ghi_cor, data['GHIobs'])
print(f"GHI → MBE new: {mbe_ghi_new:.2f}, RMSE new: {rmse_ghi_new:.2f}, R² new: {r_ghi_new:.3f}")

dni_cor = interpolation(modDNI, obsDNI, data['DNImod'], 'DNI')
mbe_dni_new, rmse_dni_new, r_dni_new = calculate_metrics(dni_cor, data['DNIobs'])
print(f"DNI → MBE new: {mbe_dni_new:.2f}, RMSE new: {rmse_dni_new:.2f}, R² new: {r_dni_new:.3f}")

# Save percentiles from training (modGHI, obsGHI, etc.)
np.savez('eqm_mapping_training_data.npz',
         modGHI=modGHI, obsGHI=obsGHI,
         modDNI=modDNI, obsDNI=obsDNI)
