import xarray as xr
import matplotlib.pyplot as plt

# List of filenames
file_names = ['download1.nc', 'download2.nc', 'download3.nc', 'download4.nc',
              'download5.nc', 'download6.nc', 'download7.nc', 'download8.nc']

# Create a dictionary to store datasets
datasets = {}

# Load each dataset and store in the dictionary
for idx, file in enumerate(file_names, start=1):
    try:
        datasets[f'df{idx}'] = xr.open_dataset(file)
    except Exception as e:
        print(f"Error loading {file}: {e}")
        continue

# TASK 1: Print the coordinates of the grid point 
print("TASK 1:")
if 'df1' in datasets:
    df1 = datasets['df1']
    print(f"The coordinates are: latitude {df1.latitude.item()} and longitude {df1.longitude.item()}")
else:
    print("Dataset df1 is missing.")

# TASK 2: Print the number of variables and their names for each file
print("TASK 2:")
for idx, df in datasets.items():
    print(f"Dataset {idx}:")
    print(f"  Number of variables: {len(df.variables)}")
    print(f"  Variable names: {list(df.variables)}\n")
print("All files have the same number of variables")
print("Three of these variables are the coordinates (or dimensions): (lon, lat, time).")
print("There are 2 more variables, the temp at 2m and the total precipitation.")

# TASK 3: Combine the datasets into a single timeseries
print("TASK 3:")
combined_dataset = xr.concat(list(datasets.values()), dim='time')
print(combined_dataset)

# TASK 4: Calculate the data's timestep
print("TASK 4: ")
time_sorted = combined_dataset.time.sortby('time')
time_diff = time_sorted.diff('time')
mean_time_diff_minutes = time_diff.mean().values.astype('timedelta64[m]').item()
mean_time_diff_hours = mean_time_diff_minutes / 60  
print(f"Time step: {mean_time_diff_hours} hours")

# TASK 5: Print the max and min values for each parameter for the whole timeseries
print("TASK 5:")
for var in combined_dataset.variables:
    print(f"Variable: {var}")
    print(f"  Max value: {combined_dataset[var].max().item()}")
    print(f"  Min value: {combined_dataset[var].min().item()}")

# TASK 6: Create a monthly climatology (mean) for each parameter
print("TASK 6: ")
monthly_means = combined_dataset[['tp', 't2m']].groupby('time.month').mean()
for var in monthly_means.variables:
    print(f"Monthly mean for {var}:")
    print(monthly_means[var])
    print()

# TASK 7: Plot the monthly climatology for t2m and tp and save each plot
variables_to_plot = ['t2m', 'tp']
for var in variables_to_plot:
    if var in monthly_means.variables:
        climatology = monthly_means[var]
        units = climatology.attrs.get('units', 'units not found') 
        plt.figure(figsize=(10, 6))
        climatology.plot()
        plt.title(f"Monthly Mean of {var}")
        plt.xlabel("Month")
        plt.ylabel(f"{var} ({units})")  
        plt.grid()
        plot_filename = f"{var}_monthly_mean_new.png"
        plt.savefig(plot_filename)
        plt.close()