import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# sza and spline values
spline_values = ['320_320', '440_440', '550_550', '675_675', '936_936']
col_names = ['umu', 'irradiance'] + [str(i) for i in range(0, 181, 10)]
angles_list = ['10', '30', '70']

# saving min and max irradiances for each spline
limits_by_SZA = {angle: {'vmin': None, 'vmax': None} for angle in angles_list}

# calculation of the limits of the color scale for each spline
for angle in angles_list:
    all_radiations = []

    for spline in spline_values:
        df = pd.read_csv(f'sza{angle}_spline{spline}_10.out', skiprows=10, 
                         delim_whitespace=True, names=col_names)
        
        # symmetric rows for 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        # all irradiance values
        radiations = df.iloc[:, 2:].values.flatten()
        all_radiations.extend(radiations)

    # saving min and max values for each spline
    limits_by_SZA[angle]['vmin'] = min(all_radiations)
    limits_by_SZA[angle]['vmax'] = max(all_radiations)

# figures with the same limits for each sza
for spline in spline_values:
    print(f"Processing for Spline = {spline}")

    df_10 = pd.read_csv(f'sza10_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)
    df_30 = pd.read_csv(f'sza30_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)
    df_70 = pd.read_csv(f'sza70_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

    data_frames = [(df_10, '10'), (df_30, '30'), (df_70, '70')]

    for df, angle in data_frames:
        # calculating sza
        df['SZA'] = np.arccos(-df['umu']) * (180 / np.pi)

        # creating symmetric columns 190°–360°
        for col in range(0, 181, 10):
            symmetric_col = str(360 - col)
            df[symmetric_col] = df[str(col)]

        ordered_columns = ['umu', 'irradiance', 'SZA'] + [str(i) for i in range(0, 361, 10)]
        df = df[ordered_columns]

        # Get min and max irradiance for the current spline
        vmin = limits_by_SZA[angle]['vmin']
        vmax = limits_by_SZA[angle]['vmax']

    # **ADDITION FOR SZA = 30° ONLY:**
    df_30 = pd.read_csv(f'sza30_spline{spline}_10.out', skiprows=10, delim_whitespace=True, names=col_names)

    # creating sza column
    df_30['SZA'] = np.arccos(-df_30['umu']) * (180 / np.pi)

    # symmetric columns for 190°–360°
    for col in range(0, 181, 10):
        symmetric_col = str(360 - col)
        df_30[symmetric_col] = df_30[str(col)]

    ordered_columns = ['umu', 'irradiance', 'SZA'] + [str(i) for i in range(0, 361, 10)]
    df_30 = df_30[ordered_columns]

    # irradiance values for SZA = 30°
    radiations_30 = df_30.iloc[:, 3:].values

    # maximum irradiance for SZA = 30°
    max_radiation_30 = np.max(radiations_30)

    # normalized irradiance
    radiation_ratios_30 = radiations_30 / max_radiation_30

    # polar graph
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
    angles = np.linspace(0, 2 * np.pi, len(df_30.columns) - 3, endpoint=False)
    cmap = plt.get_cmap("jet")
    c = ax.pcolormesh(angles, df_30['SZA'], radiation_ratios_30, cmap=cmap, shading='auto')
    fig.colorbar(c, ax=ax, label='Radiation Ratio')
    ax.set_title(f'Normalized irradiance for sza = 30° (Wavelength = {spline})')
    ax.set_theta_zero_location('N')  
    ax.set_theta_direction(-1) 
    ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False))
    ax.set_xticklabels(['0°', '30°', '60°', '90°', '120°', '150°', '180°', 
                        '210°', '240°', '270°', '300°', '330°'])
    ax.set_ylabel("SZA (Degrees)")
    plt.tight_layout()
    plt.savefig(f'normalized_irradiance_{spline}.png')
    plt.show()