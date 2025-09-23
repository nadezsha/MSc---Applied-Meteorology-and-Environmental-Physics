import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# list of szas and spline values
spline_values = ['320_320', '440_440', '550_550', '675_675', '936_936']
col_names = ['umu', 'irradiance'] + [str(i) for i in range(0, 181, 10)]
angles_list = ['10', '30', '70']

# saving min and max irradiances for each sza
limits_by_SZA = {angle: {'vmin': None, 'vmax': None} for angle in angles_list}

# calculation of the limits of the color scale for each sza
for angle in angles_list:
    all_radiations = []

    for spline in spline_values:
        df = pd.read_csv(f'sza{angle}_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

        # symmetric rows for 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        # all irradiance values
        radiations = df.iloc[:, 2:].values.flatten()
        all_radiations.extend(radiations)

    # saving min and max values
    limits_by_SZA[angle]['vmin'] = min(all_radiations)
    limits_by_SZA[angle]['vmax'] = max(all_radiations)

# figures with same limits for each sza
for spline in spline_values:
    print(f"Processing for Spline = {spline}")

    df_10 = pd.read_csv(f'sza10_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)
    df_30 = pd.read_csv(f'sza30_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)
    df_70 = pd.read_csv(f'sza70_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

    data_frames = [(df_10, '10'), (df_30, '30'), (df_70, '70')]

    for df, angle in data_frames:
        # tranforming -cosine(theta) to theta
        df['SZA'] = np.arccos(-df['umu']) * (180 / np.pi)

        # cretaion of symmetric columns for 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        ordered_columns = ['umu', 'irradiance', 'SZA'] + [str(i) for i in range(0, 361, 10)]
        df = df[ordered_columns]

        vmin = limits_by_SZA[angle]['vmin']
        vmax = limits_by_SZA[angle]['vmax']

        # polar graph
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
        angles = np.linspace(0, 2 * np.pi, len(df.columns) - 3, endpoint=False)
        radiations = df.iloc[:, 3:].values
        cmap = plt.get_cmap("jet")  # blue to red
        c = ax.pcolormesh(angles, df['SZA'], radiations, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)
        fig.colorbar(c, ax=ax, label='Irradiance')
        ax.set_title(f'Polar grapg for sza = {angle}° and wavelength = {spline} nm')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)  
        ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False)) 
        ax.set_xticklabels(['0°', '30°', '60°', '90°', '120°', '150°', '180°', '210°', '240°', '270°', '300°', '330°'])
        ax.set_ylabel("sza (°)")
        plt.tight_layout()
        plt.savefig(f'{angle}_{spline}.png')
        plt.show()