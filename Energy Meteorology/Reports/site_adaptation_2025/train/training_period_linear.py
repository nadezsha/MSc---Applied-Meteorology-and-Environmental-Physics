import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

data = pd.read_csv('Train_Boulder.txt', sep = " ")
#print(data)

##### Functions #####

def plot_mod_vs_obs(mod, obs, radiation_type):
    # Create the output folder if it doesn't exist
    output_dir = "training_period_linear_figures"
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
    plt.title(f'Initial Plotting of the Training Dataset - {radiation_type}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_filename = os.path.join(output_dir, f"training_plot_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()

    return a, b

def plot_modcor_vs_mod(modcor, mod, radiation_type):
    # Create the output folder if it doesn't exist
    output_dir = "training_period_linear_figures"
    os.makedirs(output_dir, exist_ok=True)

    # Linear regression: y = a* x + b*
    a_star, b_star = np.polyfit(mod, modcor, 1)

    # Create points for regression line
    x_vals = np.linspace(min(mod), max(mod), 100)
    y_vals = a_star * x_vals + b_star

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(mod, modcor, label=f'{radiation_type} corrected data points')
    plt.plot(x_vals, y_vals, color='red', label=f'Regression: mod,cor = {a_star:.2f}mod + {b_star:.2f}')
    plt.plot(x_vals, x_vals, color='black', linestyle='--', label='1:1 Line (y = x)')

    plt.xlabel('Original Modeled Data [W/m²]')
    plt.ylabel('Corrected Modeled Data [W/m²]')
    plt.title(f'Corrected Modeled values vs Original Modeled values - {radiation_type}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_filename = os.path.join(output_dir, f"modcor_vs_mod_{radiation_type}.png")
    plt.savefig(plot_filename)
    plt.show()

    return a_star, b_star

def plot_cormod_vs_obs(cormod, obs, radiation_type):
    # Create the output folder if it doesn't exist
    output_dir = "training_period_linear_figures"
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
    plot_filename = os.path.join(output_dir, f"training_plot_{radiation_type}.png")
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
data['GHImodcor'] = data['GHImod'] - ((a_ghi - 1) * data['GHIobs'] + b_ghi)


a_dni, b_dni = plot_mod_vs_obs(data['DNImod'], data['DNIobs'], 'DNI')
mbe_dni, rmse_dni, r_dni = calculate_metrics(data['DNImod'], data['DNIobs'])
print(f"DNI → MBE: {mbe_dni:.2f}, RMSE: {rmse_dni:.2f}, R: {r_dni:.3f}")
data['DNImodcor'] = data['DNImod'] - ((a_dni - 1) * data['DNIobs'] + b_dni)

# step 2
a_ghi_star, b_ghi_star = plot_modcor_vs_mod(data['GHImodcor'], data['GHImod'], 'GHI')
a_dni_star, b_dni_star = plot_modcor_vs_mod(data['DNImodcor'], data['DNImod'], 'DNI')

# save star values on a txt file
output_path = "modcor_regression_parameters.txt"
with open(output_path, "w") as f:
    f.write("Regression Parameters for ModCor vs Mod\n")
    f.write(f"GHI: a* = {a_ghi_star:.6f}, b* = {b_ghi_star:.6f}\n")
    f.write(f"DNI: a* = {a_dni_star:.6f}, b* = {b_dni_star:.6f}\n")

# step 3
print(" ")
a_ghio, b_ghio = plot_cormod_vs_obs(data['GHImodcor'], data['GHIobs'], 'GHI')
mbe_ghi_new, rmse_ghi_new, r_ghi_new = calculate_metrics(data['GHImodcor'], data['GHIobs'])
print(f"GHI → MBE new: {mbe_ghi_new:.2f}, RMSE new: {rmse_ghi_new:.2f}, R new: {r_ghi_new:.3f}")

a_dnio, b_dnio = plot_cormod_vs_obs(data['DNImodcor'], data['DNIobs'], 'DHI')
mbe_dni_new, rmse_dni_new, r_dni_new = calculate_metrics(data['DNImodcor'], data['DNIobs'])
print(f"DNI → MBE new: {mbe_dni_new:.2f}, RMSE new: {rmse_dni_new:.2f}, R new: {r_dni_new:.3f}")