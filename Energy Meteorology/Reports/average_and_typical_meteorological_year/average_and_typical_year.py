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
            ax.set_xlabel(f'{variable} [Wh/m²]')
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
        ax_avg.set_xlabel(f'{variable} [Wh/m²]')
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

    # Overview of monthly fits
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
        ax.set_xlabel(f'{variable} [Wh/m²]')
        ax.set_ylabel('CDF')
        ax.grid(True)
        ax.legend(fontsize=8)

    fig_final.suptitle(f'{variable} - Representative Months Overview', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f'{output_folder}/{variable}_Representative_Months_Overview.png')
    plt.close(fig_final)

calculate_tmy(df_ghi, 'GHI')
calculate_tmy(df_bni, 'BNI')

# -----------------------------
# Part 3: Load and Compare AY vs TMY
# -----------------------------

def load_tmy_csvs(variable, folder='typical_year_figures'):
    all_months_df = []

    for month in range(1, 13):
        month_name = pd.to_datetime(f'2021-{month:02d}-01').strftime('%B')
        matching_files = [f for f in os.listdir(folder) if f.startswith(f"{variable}_TMY_{month_name}_")]
        if not matching_files:
            print(f"Warning: No file found for {month_name}. Skipping.")
            continue
        
        df = pd.read_csv(os.path.join(folder, matching_files[0]), parse_dates=['time'])
        all_months_df.append(df)

    if all_months_df:
        return pd.concat(all_months_df, ignore_index=True)
    else:
        print("Error: No TMY files found.")
        return pd.DataFrame()

ay_ghi = pd.read_csv('average_year_GHI.csv')
ay_ghi['GHI'] = ay_ghi[[f'{h:02d}:00' for h in range(24)]].sum(axis=1)

ay_bni = pd.read_csv('average_year_BNI.csv')
ay_bni['BNI'] = ay_bni[[f'{h:02d}:00' for h in range(24)]].sum(axis=1)

tmy_ghi = load_tmy_csvs('GHI')
tmy_ghi = tmy_ghi.groupby(tmy_ghi['time'].dt.date)['GHI'].sum().reset_index()
tmy_ghi['time'] = pd.to_datetime(tmy_ghi['time'])

tmy_bni = load_tmy_csvs('BNI')
tmy_bni = tmy_bni.groupby(tmy_bni['time'].dt.date)['BNI'].sum().reset_index()
tmy_bni['time'] = pd.to_datetime(tmy_bni['time'])


# ---- Monthly Means and Sums for AY and TMY ----
def compare_monthly_means(variable, ay_df, tmy_df, output_dir='typical_year_figures'):
    ay_df['month'] = ay_df['DayOfYear'].apply(lambda d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d - 1)).month)
    tmy_df['month'] = tmy_df['time'].dt.month

    ay_monthly_mean = ay_df.groupby('month')[variable].mean()
    tmy_monthly_mean = tmy_df.groupby('month')[variable].mean()

    df_mean = pd.DataFrame({
        'Month': range(1, 13),
        'AY_Mean': ay_monthly_mean.values,
        'TMY_Mean': tmy_monthly_mean.values
    })
    df_mean['Difference'] = df_mean['TMY_Mean'] - df_mean['AY_Mean']

    print(f"\n📈 Monthly Mean Comparison for {variable} (Daily mean in Wh/m²):")
    print(df_mean)

    plt.figure(figsize=(10, 6))
    plt.plot(df_mean['Month'], df_mean['AY_Mean'], label='AY Mean')
    plt.plot(df_mean['Month'], df_mean['TMY_Mean'], label='TMY Mean')
    plt.fill_between(df_mean['Month'], df_mean['AY_Mean'], df_mean['TMY_Mean'], alpha=0.3)
    plt.title(f'{variable} Monthly Mean Comparison (Wh/m²)')
    plt.xlabel('Month')
    plt.ylabel('Daily Mean [Wh/m²]')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_AY_vs_TMY_Monthly_Mean.png')
    plt.close()

def compare_monthly(variable, ay_df, tmy_df, output_dir='typical_year_figures'):
    ay_df['month'] = ay_df['DayOfYear'].apply(lambda d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d - 1)).month)
    tmy_df['month'] = tmy_df['time'].dt.month

    ay_monthly = ay_df.groupby('month')[variable].sum() / 1000  # kWh/m²
    tmy_monthly = tmy_df.groupby('month')[variable].sum() / 1000  # kWh/m²

    df_comp = pd.DataFrame({
        'Month': range(1, 13),
        'AY_Sum_kWh': ay_monthly.values,
        'TMY_Sum_kWh': tmy_monthly.values
    })
    df_comp['Difference_kWh'] = df_comp['TMY_Sum_kWh'] - df_comp['AY_Sum_kWh']
    df_comp['Percent_Diff'] = 100 * df_comp['Difference_kWh'] / df_comp['AY_Sum_kWh']

    print(f"\n📊 Monthly Sum Comparison for {variable} (kWh/m²):")
    print(df_comp)

    # Energy Sum Plot
    plt.figure(figsize=(10, 6))
    plt.plot(df_comp['Month'], df_comp['AY_Sum_kWh'], label='AY Sum')
    plt.plot(df_comp['Month'], df_comp['TMY_Sum_kWh'], label='TMY Sum')
    plt.fill_between(df_comp['Month'], df_comp['AY_Sum_kWh'], df_comp['TMY_Sum_kWh'], alpha=0.3)
    plt.title(f'{variable} Monthly Energy Comparison (kWh/m²)')
    plt.xlabel('Month')
    plt.ylabel('Energy [kWh/m²]')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_AY_vs_TMY_Monthly_Sum_kWh.png')
    plt.close()

    # Percent Difference Plot
    plt.figure(figsize=(10, 6))
    plt.bar(df_comp['Month'], df_comp['Percent_Diff'], color='skyblue', edgecolor='black')
    plt.axhline(0, color='gray', linestyle='--')
    plt.title(f'{variable} TMY vs AY Monthly Percent Difference')
    plt.xlabel('Month')
    plt.ylabel('Difference [%]')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_TMY_vs_AY_Percent_Diff.png')
    plt.close()

    # Totals
    total_ay = ay_df[variable].sum() / 1000
    total_tmy = tmy_df[variable].sum() / 1000
    print(f"\n🔢 Annual Totals for {variable}:")
    print(f"AY Total:  {total_ay:.2f} kWh/m²")
    print(f"TMY Total: {total_tmy:.2f} kWh/m²")
    print(f"Difference: {(total_tmy - total_ay):.2f} kWh/m²")


compare_monthly('GHI', ay_ghi, tmy_ghi)
compare_monthly_means('GHI', ay_ghi, tmy_ghi)

compare_monthly('BNI', ay_bni, tmy_bni)
compare_monthly_means('BNI', ay_bni, tmy_bni)


# ---- Compare Yearly Sums ----
def compare_yearly_sum(variable, ay_df, tmy_df, output_dir='typical_year_figures'):
    total_ay = ay_df[variable].sum() / 1000  # kWh/m²
    total_tmy = tmy_df[variable].sum() / 1000  # kWh/m²

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(['Average Year (AY)', 'Typical Meteorological Year (TMY)'],
                  [total_ay, total_tmy],
                  color=['orange', 'blue'],
                  edgecolor='black')

    ax.set_ylabel('Total Energy [kWh/m²]')
    ax.set_title(f'Yearly Total {variable} Comparison')
    ax.grid(axis='y')

    # Add data labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f} kWh/m²',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10,
                    fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{variable}_Yearly_Sum_Comparison.png')
    plt.close()

    print(f"\n📊 Yearly Sum Comparison for {variable} (kWh/m²):")
    print(f"AY Total:  {total_ay:.2f} kWh/m²")
    print(f"TMY Total: {total_tmy:.2f} kWh/m²")
    print(f"Difference: {(total_tmy - total_ay):.2f} kWh/m²")

compare_yearly_sum('GHI', ay_ghi, tmy_ghi)
compare_yearly_sum('BNI', ay_bni, tmy_bni)


# ---- Compare Daily Sums ----
def plot_daily_sums_ay_vs_tmy(variable, ay_df, tmy_df, output_dir='typical_year_figures'):
    # Prepare daily sums for AY
    ay_daily = ay_df.copy()
    ay_daily['month'] = ay_daily['DayOfYear'].apply(lambda d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d - 1)).month)
    ay_daily_sums = ay_daily[[variable, 'month', 'DayOfYear']].copy()

    # Prepare daily sums for TMY
    tmy_daily = tmy_df.copy()
    tmy_daily['month'] = tmy_daily['time'].dt.month
    tmy_daily['day'] = tmy_daily['time'].dt.day
    tmy_daily_daily_sums = tmy_daily[[variable, 'month', 'time']].copy()

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    fig, axes = plt.subplots(3, 4, figsize=(20, 12), sharey=True)
    axes = axes.flatten()

    for month in range(1, 13):
        ax = axes[month-1]

        # AY daily sums for month
        ay_month = ay_daily_sums[ay_daily_sums['month'] == month]
        ax.plot(ay_month['DayOfYear'], ay_month[variable], label='AY', color='orange', marker='o', markersize=3)

        # TMY daily sums for month
        tmy_month = tmy_daily_daily_sums[tmy_daily_daily_sums['month'] == month]
        # Align TMY time to day of year to plot on same x-axis scale as AY
        tmy_month_days = tmy_month['time'].dt.dayofyear
        ax.plot(tmy_month_days, tmy_month[variable], label='TMY', color='blue', marker='x', markersize=3)

        ax.set_title(month_names[month-1])
        ax.set_xlabel('Day of Year')
        if month % 4 == 1:
            ax.set_ylabel(f'Daily Sum {variable} [Wh/m²]')
        ax.grid(True)
        ax.legend(fontsize=8)

    plt.suptitle(f'Daily Sum Comparison AY vs TMY for {variable}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f'{output_dir}/{variable}_Daily_Sum_AY_vs_TMY_12Months.png')
    plt.close()

plot_daily_sums_ay_vs_tmy('GHI', ay_ghi, tmy_ghi)
plot_daily_sums_ay_vs_tmy('BNI', ay_bni, tmy_bni)


# ---- Compare Monthly Sums ----
def plot_monthly_sums_combined(ay_df_ghi, ay_df_bni, tmy_df_ghi, tmy_df_bni, output_dir='typical_year_figures'):
    # Compute month columns
    ay_df_ghi['month'] = ay_df_ghi['DayOfYear'].apply(lambda d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d - 1)).month)
    ay_df_bni['month'] = ay_df_bni['DayOfYear'].apply(lambda d: (pd.Timestamp('2021-01-01') + pd.Timedelta(days=d - 1)).month)
    tmy_df_ghi['month'] = tmy_df_ghi['time'].dt.month
    tmy_df_bni['month'] = tmy_df_bni['time'].dt.month

    # Monthly sums
    ay_monthly_ghi = ay_df_ghi.groupby('month')['GHI'].sum() / 1000  # kWh/m²
    ay_monthly_bni = ay_df_bni.groupby('month')['BNI'].sum() / 1000
    tmy_monthly_ghi = tmy_df_ghi.groupby('month')['GHI'].sum() / 1000
    tmy_monthly_bni = tmy_df_bni.groupby('month')['BNI'].sum() / 1000

    months = range(1, 13)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # --- AY Plot ---
    plt.figure(figsize=(10, 6))
    plt.plot(months, ay_monthly_ghi, label='GHI - AY', marker='o', color='orange')
    plt.plot(months, ay_monthly_bni, label='BNI - AY', marker='s', color='blue')
    plt.xticks(months, month_names)
    plt.title("Monthly Energy Sum (AY) - GHI & BNI")
    plt.xlabel("Month")
    plt.ylabel("Monthly Sum [kWh/m²]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/AY_GHI_BNI_Monthly_Sum.png")
    plt.close()

    # --- TMY Plot ---
    plt.figure(figsize=(10, 6))
    plt.plot(months, tmy_monthly_ghi, label='GHI - TMY', marker='o', color='orange')
    plt.plot(months, tmy_monthly_bni, label='BNI - TMY', marker='s', color='blue')
    plt.xticks(months, month_names)
    plt.title("Monthly Energy Sum (TMY) - GHI & BNI")
    plt.xlabel("Month")
    plt.ylabel("Monthly Sum [kWh/m²]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/TMY_GHI_BNI_Monthly_Sum.png")
    plt.close()

plot_monthly_sums_combined(ay_ghi, ay_bni, tmy_ghi, tmy_bni)


# ---- Compare Yearly Sums ----
def plot_combined_yearly_sums(ay_df_ghi, ay_df_bni, tmy_df_ghi, tmy_df_bni, output_dir='typical_year_figures'):
    total_ay_ghi = ay_df_ghi['GHI'].sum() / 1000  # kWh/m²
    total_tmy_ghi = tmy_df_ghi['GHI'].sum() / 1000

    total_ay_bni = ay_df_bni['BNI'].sum() / 1000
    total_tmy_bni = tmy_df_bni['BNI'].sum() / 1000

    variables = ['GHI', 'BNI']
    ay_totals = [total_ay_ghi, total_ay_bni]
    tmy_totals = [total_tmy_ghi, total_tmy_bni]

    x = np.arange(len(variables))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar(x - width / 2, ay_totals, width, label='AY', color='orange', edgecolor='black')
    bars2 = ax.bar(x + width / 2, tmy_totals, width, label='TMY', color='blue', edgecolor='black')

    ax.set_ylabel('Total Energy [kWh/m²]')
    ax.set_title('Yearly Total GHI and BNI Comparison (AY vs TMY)')
    ax.set_xticks(x)
    ax.set_xticklabels(variables)
    ax.legend()
    ax.grid(axis='y')

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Combined_Yearly_Sum_GHI_BNI.png'))
    plt.close()

    print("\n📊 Combined Yearly Total Comparison for GHI and BNI saved.")

plot_combined_yearly_sums(ay_ghi, ay_bni, tmy_ghi, tmy_bni)