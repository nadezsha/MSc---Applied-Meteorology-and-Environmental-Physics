import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------
# Part 1: Average Year Generator
# -----------------------------

def process_variable(variable_name, input_file='out.nc', output_file=None):
    data = xr.open_dataset(input_file)
    
    if variable_name not in data:
        print(f"Error: {variable_name} not found in the dataset.")
        return
    
    var = data[variable_name]
    
    # drop February 29 to handle leap years
    is_feb_29 = (var['time'].dt.month == 2) & (var['time'].dt.day == 29)
    var = var.sel(time=~is_feb_29)

    var.coords['day'] = var['time'].dt.dayofyear
    var.coords['day'] = var.coords['day'].where(var.coords['day'] < 60, var.coords['day'] - 1)
    var.coords['hour'] = var['time'].dt.hour

    ay = var.groupby(['day', 'hour']).mean(dim='time')

    df_ay = ay.to_dataframe(name=variable_name).unstack(level='hour')
    df_ay.columns = [f'{col:02d}:00' for col in df_ay.columns.get_level_values('hour')]
    df_ay.reset_index(inplace=True)
    df_ay.rename(columns={'day': 'DayOfYear'}, inplace=True)
    df_ay = df_ay[['DayOfYear'] + [f'{h:02d}:00' for h in range(24)]]

    if not output_file:
        output_file = f'average_year_{variable_name}.csv'
    df_ay.to_csv(output_file, index=False)

    print(f"Average Year for {variable_name} saved as '{output_file}'")

process_variable('GHI', input_file='out.nc', output_file='average_year_GHI.csv')
process_variable('BNI', input_file='out.nc', output_file='average_year_BNI.csv')

# -----------------------------
# Part 2: Typical Meteorological Year (TMY)
# -----------------------------

# load NetCDF and convert to DataFrame
ds = xr.open_dataset("out.nc")
ghi = ds["GHI"]
bni = ds["BNI"]

df_ghi = ghi.to_dataframe().reset_index()
df_bni = bni.to_dataframe().reset_index()

for df in [df_ghi, df_bni]:
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['day'] = df['time'].dt.day

df_ghi = df_ghi[~((df_ghi['month'] == 2) & (df_ghi['day'] == 29))]
df_bni = df_bni[~((df_bni['month'] == 2) & (df_bni['day'] == 29))]

def calculate_tmy(df, variable):
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    output_folder = 'typical_year_figures'
    os.makedirs(output_folder, exist_ok=True)

    representative_years = []

    for month in range(1, 13):
        df_month = df[df['month'] == month].copy()
        years = df_month['year'].unique()

        fig, axes = plt.subplots((len(years) + 4) // 5, 5, figsize=(15, 3 * ((len(years) + 4) // 5)))
        axes = axes.flatten()
        cdf_matrix = []

        for i, year in enumerate(years):
            df_year = df_month[df_month['year'] == year]
            values = df_year[variable].dropna().values
            sorted_vals = np.sort(values)
            cdf = np.linspace(0, 1, len(sorted_vals))

            cdf_matrix.append(sorted_vals)

            ax = axes[i]
            ax.plot(sorted_vals, cdf, label=f'Year {year}')
            ax.set_title(f'{variable} - {month_names[month-1]} {year}')
            ax.set_xlabel(f'{variable} [W/m²]')
            ax.set_ylabel('CDF')
            ax.grid(True)

        target_len = min(len(c) for c in cdf_matrix)
        cdf_matrix_interp = [
            np.interp(np.linspace(0, 1, target_len), np.linspace(0, 1, len(c)), c)
            for c in cdf_matrix
        ]
        cdf_matrix_interp = np.array(cdf_matrix_interp)
        avg_cdf = np.mean(cdf_matrix_interp, axis=0)

        fig_avg, ax_avg = plt.subplots(figsize=(10, 6))
        all_values = np.sort(np.concatenate(cdf_matrix))
        ax_avg.plot(all_values, np.linspace(0, 1, len(all_values)), label='All Years Average', color='black', linewidth=2)
        ax_avg.set_title(f'Average {variable} CDF for {month_names[month-1]}')
        ax_avg.set_xlabel(f'{variable} [W/m²]')
        ax_avg.set_ylabel('CDF')
        ax_avg.grid(True)
        plt.tight_layout()
        plt.savefig(f'{output_folder}/{variable}_Average_CDF_{month_names[month-1]}.png')
        plt.close(fig_avg)

        diffs = np.abs(cdf_matrix_interp - avg_cdf)
        mean_diffs = np.mean(diffs, axis=1)

        best_index = np.argmin(mean_diffs)
        best_year = years[best_index]
        representative_years.append(best_year)

        representative_df = df_month[df_month['year'] == best_year]
        representative_df[['time', variable]].to_csv(
            f'{output_folder}/{variable}_TMY_{month_names[month-1]}_{best_year}.csv', index=False
        )

        plt.tight_layout()
        plt.suptitle(f'{variable} CDFs for {month_names[month-1]}', fontsize=16)
        plt.subplots_adjust(top=0.9)
        plt.savefig(f'{output_folder}/{variable}_CDF_{month_names[month-1]}.png')
        plt.close(fig)

        print(f"📅 Representative Year for {month_names[month-1]}: {best_year}")

    # final overview
    fig_final, axes_final = plt.subplots(3, 4, figsize=(18, 12))
    axes_final = axes_final.flatten()

    for month in range(1, 13):
        df_month = df[(df['month'] == month) & (df['year'] == representative_years[month-1])].copy()
        values = df_month[variable].dropna().values
        sorted_vals = np.sort(values)
        cdf = np.linspace(0, 1, len(sorted_vals))

        all_df = df[df['month'] == month]
        all_values = np.sort(all_df[variable].dropna().values)
        avg_cdf = np.linspace(0, 1, len(all_values))

        ax = axes_final[month - 1]
        ax.plot(all_values, avg_cdf, label='Average', color='black')
        ax.plot(sorted_vals, cdf, label=f'{representative_years[month - 1]}', color='red')
        ax.set_title(f'{month_names[month - 1]} - {representative_years[month - 1]}')
        ax.set_xlabel(f'{variable} [W/m²]')
        ax.set_ylabel('CDF')
        ax.grid(True)
        ax.legend(fontsize=8)

    fig_final.suptitle(f'{variable} - Representative Months Overview', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f'{output_folder}/{variable}_Representative_Months_Overview.png')
    plt.close(fig_final)

# calculate TMYs
calculate_tmy(df_ghi, 'GHI')
calculate_tmy(df_bni, 'BNI')

print("All figures and representative year data saved in 'typical_year_figures' folder.")

def compare_monthly_means(ay_df, tmy_df, variable, save_csv=False, output_dir='typical_year_figures'):
    """
    Compare monthly means of AY (Average Year) and TMY (Typical Meteorological Year).
    
    Parameters:
    - ay_df (DataFrame): DataFrame containing AY values with 'DayOfYear' and hourly data.
    - tmy_df (DataFrame): DataFrame containing TMY values with a 'time' column and specified variable.
    - variable (str): The variable to compare (e.g., 'GHI', 'BNI').
    - save_csv (bool): Whether to save the comparison result as CSV. Default is False.
    - output_dir (str): Directory to save output CSV and plot. Default is 'typical_year_figures'.
    
    Returns:
    - df_comp (DataFrame): DataFrame containing the monthly comparison of AY and TMY means.
    """

    # ensure AY DataFrame has the correct column and map DayOfYear to Month
    if 'DayOfYear' not in ay_df.columns:
        print("Error: 'DayOfYear' column not found in AY DataFrame.")
        return

    # Map DayOfYear to Month for AY
    day_map = {d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d-1)).month for d in ay_df['DayOfYear']}
    ay_df['month'] = ay_df['DayOfYear'].map(day_map)

    # drop missing values in AY DataFrame
    ay_df.dropna(subset=[variable], inplace=True)

    # group by Month and calculate the mean for each month (over all days in the year)
    ay_monthly = ay_df.groupby('month')[variable].mean()

    # ensure TMY DataFrame is ready and calculate monthly averages for TMY
    tmy_df['month'] = tmy_df['time'].dt.month  

    # drop missing values in TMY DataFrame
    tmy_df.dropna(subset=[variable], inplace=True)

    tmy_monthly = tmy_df.groupby('month')[variable].mean()

    # combine AY and TMY Monthly Averages
    df_comp = pd.DataFrame({
        'Month': range(1, 13),
        'AY_Mean': ay_monthly.values,
        'TMY_Mean': tmy_monthly.values
    })
    df_comp['Difference (TMY - AY)'] = df_comp['TMY_Mean'] - df_comp['AY_Mean']

    # display the comparison for each month
    print("\n📈 Monthly Mean Comparison for", variable)
    print(df_comp)

    # -plot Monthly Mean Comparison
    plt.figure(figsize=(10, 6))
    plt.plot(df_comp['Month'], df_comp['AY_Mean'], marker='o', label='AY Mean')
    plt.plot(df_comp['Month'], df_comp['TMY_Mean'], marker='s', label='TMY Mean')
    plt.fill_between(df_comp['Month'], df_comp['AY_Mean'], df_comp['TMY_Mean'], color='gray', alpha=0.2)
    plt.title(f'{variable} Monthly Mean Comparison')
    plt.xlabel('Month')
    plt.ylabel(f'{variable} [W/m²]')
    plt.xticks(range(1, 13))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_AY_vs_TMY_Monthly.png')
    plt.close()
    print(f"Saved monthly comparison plot for {variable}.")

    # monthly Difference Bar Plot
    plt.figure(figsize=(10, 6))
    plt.bar(df_comp['Month'], df_comp['Difference (TMY - AY)'], color='b', alpha=0.7)
    plt.title(f'{variable} Monthly Difference (TMY - AY)')
    plt.xlabel('Month')
    plt.ylabel(f'Difference [W/m²]')
    plt.xticks(range(1, 13))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_Monthly_Difference.png')
    plt.close()
    print(f"Saved monthly difference bar plot for {variable}.")

    # calculate Yearly Mean Difference
    ay_yearly = ay_df[variable].mean()  # Average over the entire year for AY
    tmy_yearly = tmy_df[variable].mean()  # Average over the entire year for TMY

    # Yearly Difference
    yearly_diff = tmy_yearly - ay_yearly

    # return the DataFrame for further analysis if needed
    return df_comp

# load AY CSVs and compute daily means
ay_ghi = pd.read_csv('average_year_GHI.csv')
ay_ghi['GHI'] = ay_ghi[[f'{h:02d}:00' for h in range(24)]].mean(axis=1)

ay_bni = pd.read_csv('average_year_BNI.csv')
ay_bni['BNI'] = ay_bni[[f'{h:02d}:00' for h in range(24)]].mean(axis=1)

def load_tmy_csvs(variable, folder='typical_year_figures'):
    """
    Load and combine TMY CSV files for each month into a single DataFrame.
    
    Parameters:
    - variable (str): Name of the variable (e.g., 'GHI', 'BNI').
    - folder (str): Directory where TMY CSV files are saved.
    
    Returns:
    - DataFrame with concatenated TMY data for all months.
    """
    all_months_df = []

    for month in range(1, 13):
        month_name = pd.to_datetime(f'2021-{month:02d}-01').strftime('%B')
        file_path = os.path.join(folder, f"{variable}_TMY_{month_name}_*.csv")

        # if the filename includes a wildcard for the year (as saved by the original script)
        matching_files = [f for f in os.listdir(folder) if f.startswith(f"{variable}_TMY_{month_name}_")]
        if not matching_files:
            print(f"Warning: No file found for {month_name}. Skipping.")
            continue
        
        # load the first matching file (should be only one per month)
        df = pd.read_csv(os.path.join(folder, matching_files[0]), parse_dates=['time'])
        all_months_df.append(df)

    if all_months_df:
        combined_df = pd.concat(all_months_df, ignore_index=True)
        return combined_df
    else:
        print("Error: No TMY files found.")
        return pd.DataFrame()

# load TMY data
tmy_ghi = load_tmy_csvs('GHI')
tmy_bni = load_tmy_csvs('BNI')

# compare
compare_monthly_means(ay_ghi, tmy_ghi, variable='GHI', save_csv=True)
compare_monthly_means(ay_bni, tmy_bni, variable='BNI', save_csv=True)