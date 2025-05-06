import xarray as xr
import pandas as pd
import numpy as np

# Function to process a variable and output its average year
def process_variable(variable_name, input_file='out.nc', output_file=None):
    # Read the data
    data = xr.open_dataset(input_file)
    
    # Check if the variable exists
    if variable_name not in data:
        print(f"Error: {variable_name} not found in the dataset.")
        return
    
    # Extract the variable (e.g., GHI or BNI)
    var = data[variable_name]
    
    # Drop February 29 
    is_feb_29 = (var['time'].dt.month == 2) & (var['time'].dt.day == 29)
    var = var.sel(time=~is_feb_29)

    # Remove February 29 and recalculate day correctly for non-leap year
    var.coords['day'] = var['time'].dt.dayofyear
    var.coords['day'] = var.coords['day'].where(var.coords['day'] < 60, var.coords['day'] - 1)

    # Add hour as coordinates
    var.coords['hour'] = var['time'].dt.hour

    # Group by (day, hour) and average across years
    ay = var.groupby(['day', 'hour']).mean(dim='time')

    # Convert to DataFrame and pivot (365 days × 24 hours)
    df_ay = ay.to_dataframe(name=variable_name).unstack(level='hour')

    # Fix the column names to be the correct hour format
    df_ay.columns = [f'{col:02d}:00' for col in df_ay.columns.get_level_values('hour')]

    # Reset the index to include 'day' as a column
    df_ay.reset_index(inplace=True)

    # Rename the 'day' column to 'DayOfYear'
    df_ay.rename(columns={'day': 'DayOfYear'}, inplace=True)

    # Select only the 'DayOfYear' and the hourly columns (no unwanted columns)
    df_ay = df_ay[['DayOfYear'] + [f'{h:02d}:00' for h in range(24)]]

    # Define the output file name if not provided
    if not output_file:
        output_file = f'average_year_{variable_name}.csv'

    # Save to CSV, ensuring only the relevant columns are included
    df_ay.to_csv(output_file, index=False)

    print(f"Average Year for {variable_name} saved as '{output_file}'")

# Example usage for both variables:
process_variable('GHI', input_file='out.nc', output_file='average_year_GHI.csv')
process_variable('BNI', input_file='out.nc', output_file='average_year_BNI.csv')