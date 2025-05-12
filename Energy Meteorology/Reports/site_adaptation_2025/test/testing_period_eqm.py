import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import os

##### Setup Output Directory #####
output_dir = "testing_period_eqm"
os.makedirs(output_dir, exist_ok=True)

##### Utility Functions #####

def calculate_metrics(mod, obs):
    mod = np.array(mod)
    obs = np.array(obs)
    mbe = np.mean(mod - obs)
    rmse = np.sqrt(mean_squared_error(obs, mod))
    r, _ = pearsonr(obs, mod)
    return mbe, rmse, r

def report_metrics(label, modeled, observed):
    mbe, rmse, r = calculate_metrics(modeled, observed)
    print(f"{label} → MBE: {mbe:.2f}, RMSE: {rmse:.2f}, R: {r:.3f}")
    return mbe, rmse, r

def initial_graph(obs, mod, radiation_type):
    plt.figure(figsize=(10, 10))

    obs_sorted = np.sort(obs)
    mod_sorted = np.sort(mod)
    num = np.linspace(0, 100, len(obs_sorted))

    plt.plot(obs_sorted, num, color='red', label='Observed Data [W/m²]')
    plt.plot(mod_sorted, num, color='blue', label='Modeled Data [W/m²]')

    plt.ylabel("Cumulative Probability [%]")
    plt.xlabel(f'{radiation_type} [W/m²]')
    plt.title(f'Initial Plotting of the Testing Dataset - {radiation_type}')
    plt.grid()
    plt.legend()

    plot_filename = os.path.join(output_dir, f"initial_plot_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()
    plt.close()

def interpolation(modper, obsper, mod):
    modper_fixed, unique_indices = np.unique(modper, return_index=True)
    obsper_fixed_interp = obsper[unique_indices]
    interpolation = interp1d(modper_fixed, obsper_fixed_interp, kind='linear', fill_value="extrapolate", bounds_error=False)
    corrected = interpolation(mod)
    return corrected

def plot_cdf_comparison(obs_data, mod_data, corrected_data, variable_name):
    percentiles = np.arange(0, 100.5, 0.5)

    obs_cdf = np.percentile(obs_data, percentiles)
    mod_cdf = np.percentile(mod_data, percentiles)
    cor_cdf = np.percentile(corrected_data, percentiles)

    plt.figure(figsize=(10, 6))
    plt.plot(obs_cdf, percentiles, label='Observed', color='red')
    plt.plot(mod_cdf, percentiles, label='Modeled', color='blue')
    plt.plot(cor_cdf, percentiles, label='Corrected', color='green')
    plt.xlabel(f'{variable_name} [W/m²]')
    plt.ylabel('Cumulative Probability [%]')
    plt.title(f'CDF Comparison - {variable_name}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plot_filename = os.path.join(output_dir, f'CDF_comparison_{variable_name}.png')
    plt.savefig(plot_filename)
    plt.show()
    plt.close()

##### Main Processing #####

# Load testing data
data = pd.read_csv('Test_Boulder.txt', sep=" ")

# Load EQM mappings from training
loaded = np.load('eqm_mapping_training_data.npz')
modGHI = loaded['modGHI']
obsGHI = loaded['obsGHI']
modDNI = loaded['modDNI']
obsDNI = loaded['obsDNI']

# Apply EQM correction
test_ghi_cor = interpolation(modGHI, obsGHI, data['GHImod'])
test_dni_cor = interpolation(modDNI, obsDNI, data['DNImod'])

# Evaluate original modeled data
print("Original Modeled vs Observed Metrics:")
report_metrics("GHI", data['GHImod'], data['GHIobs'])
report_metrics("DNI", data['DNImod'], data['DNIobs'])

# Evaluate corrected data
print("\nCorrected Modeled vs Observed Metrics:")
report_metrics("GHI", test_ghi_cor, data['GHIobs'])
report_metrics("DNI", test_dni_cor, data['DNIobs'])

# Generate Initial CDF Graphs
initial_graph(data['GHIobs'], data['GHImod'], "GHI")
initial_graph(data['DNIobs'], data['DNImod'], "DNI")

# Generate CDF Comparison Plots
plot_cdf_comparison(data['GHIobs'], data['GHImod'], test_ghi_cor, "GHI")
plot_cdf_comparison(data['DNIobs'], data['DNImod'], test_dni_cor, "DNI")