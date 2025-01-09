import xarray as xr
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('Qt5Agg')

# TASK 1 : Reads the file using xarray.
data = xr.open_dataset('C:\\Users\\nefel\\Downloads\\nadia\\copernicus_first_lecture\\tx_1960-2022_Greece.nc') 
data

# TASK 2 : Selects the time series for the grid point corresponding to Patras (38.25° S - 21.5° E) 
# while simultaneously converting the temperature to °C.
data_array = data.mx2t.sel(latitude=38.25, longitude=21.5) - 273.15

# TASK 3 : Creates a timeseries plot only for the year 2020 and saves it.
plot_max = data_array.sel(valid_time = slice("2020-01-01", "2020-12-31"))
plot_max.plot.line(color='blue', marker='o') 
plt.savefig('2020_figure' + '.jpeg')
plt.show()

# TASK 4 : Creates a plot (histogram) of 2020 monthly mean temperatures and saves it.
monthly_avg_temp = plot_max.groupby('valid_time.month').mean()
monthly_avg_temp.plot.line(color='blue', marker='o')    
plt.savefig('2020_monthly_figure.jpeg')
plt.show()

# a histogram does not show up correctly
monthly_avg_temp.plot.hist()
plt.show()