import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

# TASK 1 : Reads the file using xarray.
data = xr.open_dataset('C:\\Users\\nefel\\Downloads\\nadia\\copernicus_first_lecture\\tx_1960-2022_Greece.nc') 
data

# TASK 2 : Selects the time series for the grid point corresponding to Patras (38.25° S - 21.5° E) 
# and transforms it into a Pandas dataframe (I also converted the temperature to °C).
data_array = data.mx2t.sel(latitude=38.25, longitude=21.5).to_dataframe() - 273.15
data_array

# TASK 3 : calculates the anomaly values timeseries, with a reference period of 1961 - 1990
# and saves it in a seperate csv file
reference_period = data_array.loc['1961-01-01':'1990-12-31']
data_array['anomaly'] = data_array['mx2t'] - reference_period['mx2t'].mean()
data_array[['anomaly']].to_csv("anomaly_timeseries", sep =";")

# TASK 4 : creates the figure of the previous tasks timeseries and saves it in a file of your choosing.
# The plot should have titles and units of measurements on both axes. 
# The graph should also show the average value of the anomaly, calculated on the entire time series.
plt.figure(figsize=(10, 6))
plt.plot(data_array.index, data_array['anomaly'], label='Anomaly', color='b')

mean_anomaly = data_array['anomaly'].mean()
plt.axhline(y=mean_anomaly, color='r', label=f'Mean Anomaly: {mean_anomaly:.2f}$^\circ$C')

plt.title('Anomaly Timeseries (1960-2022) for Patras', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Anomaly ($^\circ$C)', fontsize=14)
plt.legend()
plt.savefig('anomaly_timeseries_plot.png')
plt.show()