import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

data = pd.read_csv('Test_Boulder.txt', sep = " ")
data['GHImodcor'] = 1.068503*data['GHImod'] - 14.374397
data['DNImodcor'] = 1.152686*data['DNImod'] - 14.268841
#print(data)

##### Functions #####
def plot_mod_vs_obs(mod, obs, radiation_type):
    # Create the output folder if it doesn't exist
    output_dir = "testing_period_linear_figures"
    os.makedirs(output_dir, exist_ok=True)

    # Linear regression: y = ax + b
    a, b = np.polyfit(obs, mod, 1)

    # Create points for regression line
    x_vals = np.linspace(min(obs), max(obs), 100)
    y_vals = a * x_vals + b

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(obs, mod, label=f'{radiation_type} data points')
    plt.plot(x_vals, y_vals, color='red', label=f'Regression: mod = {a:.2f}obs + {b:.2f}')
    plt.plot(x_vals, x_vals, color='black', linestyle='--', label='1:1 Line (y = x)')

    plt.xlabel('Observed Data [W/m²]')
    plt.ylabel('Modeled Data [W/m²]')
    plt.title(f'Initial Plotting of the Testing Dataset - {radiation_type}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_filename = os.path.join(output_dir, f"testing_plot_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()

    return a, b

def plot_cormod_vs_obs(cormod, obs, radiation_type):
    # Create the output folder if it doesn't exist
    output_dir = "testing_period_linear_figures"
    os.makedirs(output_dir, exist_ok=True)

    # Linear regression: y = ax + b
    a, b = np.polyfit(obs, cormod, 1)

    # Create points for regression line
    x_vals = np.linspace(min(obs), max(obs), 100)
    y_vals = a * x_vals + b

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(obs, cormod, label=f'{radiation_type} data points')
    plt.plot(x_vals, y_vals, color='red', label=f'Regression: mod = {a:.2f}obs + {b:.2f}')
    plt.plot(x_vals, x_vals, color='black', linestyle='--', label='1:1 Line (y = x)')

    plt.xlabel('Observed Data [W/m²]')
    plt.ylabel('Corrected Modeled Data [W/m²]')
    plt.title(f'Plotting of the Training dataset after correction - {radiation_type}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_filename = os.path.join(output_dir, f"testing_plot_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()

    return a, b

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

    return mbe, rmse, r


##### Main Code #####

# step 1
a_ghi, b_ghi = plot_mod_vs_obs(data['GHImod'], data['GHIobs'], 'GHI')
mbe_ghi, rmse_ghi, r_ghi = calculate_metrics(data['GHImod'], data['GHIobs'])
print(f"GHI → MBE: {mbe_ghi:.2f}, RMSE: {rmse_ghi:.2f}, R: {r_ghi:.3f}")

a_dni, b_dni = plot_mod_vs_obs(data['DNImod'], data['DNIobs'], 'DNI')
mbe_dni, rmse_dni, r_dni = calculate_metrics(data['DNImod'], data['DNIobs'])
print(f"DNI → MBE: {mbe_dni:.2f}, RMSE: {rmse_dni:.2f}, R: {r_dni:.3f}")

# step 3
print(" ")
a_ghi_new, b_ghi_new = plot_cormod_vs_obs(data['GHImodcor'], data['GHIobs'], 'GHI')
mbe_ghi_new, rmse_ghi_new, r_ghi_new = calculate_metrics(data['GHImodcor'], data['GHIobs'])
print(f"GHI → MBE new: {mbe_ghi_new:.2f}, RMSE new: {rmse_ghi_new:.2f}, R new: {r_ghi_new:.3f}")

a_dni_new, b_dni_new = plot_cormod_vs_obs(data['DNImodcor'], data['DNIobs'], 'DNI')
mbe_dni_new, rmse_dni_new, r_dni_new = calculate_metrics(data['DNImodcor'], data['DNIobs'])
print(f"DNI → MBE new: {mbe_dni_new:.2f}, RMSE new: {rmse_dni_new:.2f}, R new: {r_dni_new:.3f}")