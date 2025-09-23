import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Load NetCDF and convert to DataFrame
ds = xr.open_dataset("out.nc")
ghi = ds["GHI"]
bni = ds["BNI"]

# Create time-based features
df_ghi = ghi.to_dataframe().reset_index()
df_bni = bni.to_dataframe().reset_index()

df_ghi['year'] = df_ghi['time'].dt.year
df_ghi['month'] = df_ghi['time'].dt.month
df_ghi['day'] = df_ghi['time'].dt.day

df_bni['year'] = df_bni['time'].dt.year
df_bni['month'] = df_bni['time'].dt.month
df_bni['day'] = df_bni['time'].dt.day

# Remove all February 29ths 
df_ghi = df_ghi[~((df_ghi['month'] == 2) & (df_ghi['day'] == 29))]
df_bni = df_bni[~((df_bni['month'] == 2) & (df_bni['day'] == 29))]

# Function to calculate TMY and plots
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

    # Combined Plot for Representative Months 
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

# Calculate for GHI and BNI 
calculate_tmy(df_ghi, 'GHI')
calculate_tmy(df_bni, 'BNI')

print("All figures and representative year data saved in 'typical_year_figures' folder.")