import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

# data containers for all tau values for each SZA
sza_20_tau0 = []  # τ = 0 for SZA = 20
sza_70_tau0 = []  # τ = 0 for SZA = 70
sza_20_tau2 = []  # τ = 2 for SZA = 20
sza_70_tau2 = []  # τ = 2 for SZA = 70
sza_20_tau5 = []  # τ = 5 for SZA = 20
sza_70_tau5 = []  # τ = 5 for SZA = 70

zout_values = range(21)  
sza_values = [20, 70]

col_names = ['altitude', 'heating rates']

# Reading files for each SZA and each tau value
for sza in sza_values:
    file_tau0 = pd.read_csv(f'sza{sza}_tau0.out', delimiter=r"\s+", names=col_names)
    file_tau2 = pd.read_csv(f'sza{sza}_tau2.out', delimiter=r"\s+", names=col_names)
    file_tau5 = pd.read_csv(f'sza{sza}_tau5.out', delimiter=r"\s+", names=col_names)

    # Store the data in respective containers
    if sza == 20:
        sza_20_tau0 = file_tau0
        sza_20_tau2 = file_tau2
        sza_20_tau5 = file_tau5
    elif sza == 70:
        sza_70_tau0 = file_tau0
        sza_70_tau2 = file_tau2
        sza_70_tau5 = file_tau5

# Plotting for SZA = 20
plt.figure(figsize=(8, 6))
plt.plot(sza_20_tau0['heating rates'], sza_20_tau0['altitude'], label=r'$\tau$ = 0', color='blue', marker='o')
plt.plot(sza_20_tau2['heating rates'], sza_20_tau2['altitude'], label=r'$\tau$ = 2', color='red', marker='o')
plt.plot(sza_20_tau5['heating rates'], sza_20_tau5['altitude'], label=r'$\tau$ = 5', color='green', marker='o')
plt.ylabel('Altitude (km)')
plt.xlabel('Heating Rates (K/day)')
plt.title('sza = 20°')
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.savefig(f'SZA20.png')
plt.show()

# Plotting for SZA = 70
plt.figure(figsize=(8, 6))
plt.plot(sza_70_tau0['heating rates'], sza_70_tau0['altitude'], label=r'$\tau$ = 0', color='blue', marker='o')
plt.plot(sza_70_tau2['heating rates'], sza_70_tau2['altitude'], label=r'$\tau$ = 2', color='red', marker='o')
plt.plot(sza_70_tau5['heating rates'], sza_70_tau5['altitude'], label=r'$\tau$ = 5', color='green', marker='o')
plt.ylabel('Altitude (km)')
plt.xlabel('Heating Rates (K/day)')
plt.title('sza = 70°')
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.savefig(f'SZA_70.png')
plt.show()

# Plotting all curves together
plt.figure(figsize=(8, 6))
plt.plot(sza_20_tau0['heating rates'], sza_20_tau0['altitude'], label=r'SZA = 20°, $\tau$ = 0', color='blue', marker='o')
plt.plot(sza_20_tau2['heating rates'], sza_20_tau2['altitude'], label=r'SZA = 20°, $\tau$ = 2', color='red', marker='o')
plt.plot(sza_20_tau5['heating rates'], sza_20_tau5['altitude'], label=r'SZA = 20°, $\tau$ = 5', color='green', marker='o')

plt.plot(sza_70_tau0['heating rates'], sza_70_tau0['altitude'], label=r'SZA = 70°, $\tau$ = 0', color='blue', marker='o')
plt.plot(sza_70_tau2['heating rates'], sza_70_tau2['altitude'], label=r'SZA = 70°, $\tau$ = 2', color='red', marker='o')
plt.plot(sza_70_tau5['heating rates'], sza_70_tau5['altitude'], label=r'SZA = 70°, $\tau$ = 5', color='green', marker='o')

plt.ylabel('Altitude (km)')
plt.xlabel('Heating Rates (K/day)')
plt.title('All Curves Together')
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.savefig(f'All_Curves_Together.png')
plt.show()