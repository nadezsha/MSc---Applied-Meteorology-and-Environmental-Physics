import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# list of szas and spline values
spline_values = ['320_320', '440_440', '550_550', '675_675', '936_936']
col_names = ['umu', 'irradiance'] + [str(i) for i in range(0, 181, 10)]
angles_list = ['10', '30', '70']

# saving min and max irradiances for each spline
limits_by_spline = {spline: {'vmin': None, 'vmax': None} for spline in spline_values}

# calculation of the limits of the color scale for each spline
for spline in spline_values:
    all_radiations = []

    for angle in angles_list:
        df = pd.read_csv(f'sza{angle}_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

        # symmetric rows for 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        # all irradiance values
        radiations = df.iloc[:, 2:].values.flatten()
        all_radiations.extend(radiations)

    # saving min and max values for each spline
    limits_by_spline[spline]['vmin'] = min(all_radiations)
    limits_by_spline[spline]['vmax'] = max(all_radiations)

# figures with the same limits for each spline
for angle in angles_list:
    print(f"Processing for SZA = {angle}")

    # For each SZA, we will iterate over all splines
    for spline in spline_values:
        df = pd.read_csv(f'sza{angle}_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

        # Transforming -cosine(theta) to theta
        df['SZA'] = np.arccos(-df['umu']) * (180 / np.pi)

        # Creation of symmetric columns for 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        ordered_columns = ['umu', 'irradiance', 'SZA'] + [str(i) for i in range(0, 361, 10)]
        df = df[ordered_columns]

        # Get min and max irradiance for the current spline
        vmin = limits_by_spline[spline]['vmin']
        vmax = limits_by_spline[spline]['vmax']

        # Polar graph
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
        angles = np.linspace(0, 2 * np.pi, len(df.columns) - 3, endpoint=False)
        radiations = df.iloc[:, 3:].values
        cmap = plt.get_cmap("jet")  # blue to red
        c = ax.pcolormesh(angles, df['SZA'], radiations, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)
        fig.colorbar(c, ax=ax, label='Irradiance')
        ax.set_title(f'Polar graph for SZA = {angle}° and wavelength = {spline} nm')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)  
        ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False)) 
        ax.set_xticklabels(['0°', '30°', '60°', '90°', '120°', '150°', '180°', '210°', '240°', '270°', '300°', '330°'])
        ax.set_ylabel("SZA (°)")
        plt.tight_layout()
        plt.savefig(f'const_wavelength_{angle}_{spline}.png')
        plt.show()

