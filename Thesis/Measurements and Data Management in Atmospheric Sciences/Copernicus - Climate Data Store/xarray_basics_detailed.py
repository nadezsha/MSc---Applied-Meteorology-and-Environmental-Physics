import xarray as xr
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')

"""
For xarray installation check: https://docs.xarray.dev/en/latest/getting-started-guide/installing.html
Specifically run the following command in a terminal window:

    pip install xarray
    
If there are any errors regarding the libraries, please install optional dependencies with:

    pip install netCDF4 scipy pydap h5netcdf zarr cftime iris bottleneck numbagg
"""

# Reading and writing files (https://docs.xarray.dev/en/stable/user-guide/io.html)
folder_path = ('C:\\Users\\nefel\\Downloads\\nadia\\copernicus_first_lecture\\')

filename = 'tp_1960-2022_Greece.nc'

file = folder_path + filename

data = xr.open_dataset(file)  # Reads and stores dataset in 'data' variable
""" 
Alternative way to read files. We can specify the file type to open with the 'engine' argument.

    data = xr.open_dataset(file, engine='netCDF4') or data = xr.open_dataset(file, engine='h5netcdf')
    
Sometimes engine='h5netcdf' can quicker than the default engine='netCDF4'
"""
data  # To check basic information of the dataset (size, variables, etc.)
data.to_netcdf('name_of_file_to_save')  # Saves the netcdf file

# Indexing, selecting and subseting data (https://docs.xarray.dev/en/latest/user-guide/indexing.html)
"""
There are 2 ways to index a Dataset:
-> Dataset
    1) By integer: data.isel(coordinate_name=0) or data[dict(coordinate_name=0)]
    2) By label: data.sel(coordinate_name='label') or data.loc[dict(coordinate_name='label')]
    
coordinate_name: Can be any coordinate such as 'time', 'latitude', 'longitude', etc.
"""
# By integer
dataset1 = data.isel(valid_time=0)  # Picks the Dataset referring to the first time (0) of the time coordinate
# By label
dataset2 = data.sel(valid_time='2014-05-13')  # Picks the Dataset containing information of the specified date

# To select specific DataArray the refers to a single variable the following can be used:
# data.variable_name or data['variable_name']
data.tp
data['tp']
"""
-> DataArray
    1) By integer: 
        i) Positional: data.variable_name[:, 0]
        ii) By name: data.variable_name.isel(coordinate_name=0) or data.variable_name[dict(coordinate_name=0)]
    2) By label:
        i) Positional: data.variable_name.loc[:, 'label']
        ii) By name: data.variable_name.sel(coordinate_name='label') or
                     data.variable_name.loc[dict(coordinate_name='label')]
        
variable_name: Can be any of the variables of the Dataset, such as 'tp'.
coordinate_name: Can be any coordinate such as 'time', 'latitude', 'longitude', etc.
"""
# By integer - Positional
data_array_ip = data.tp[1000, :, :]  # [valid_time, Latitude, Longitude]
# By integer - by name
data_array_in = data.tp.isel(valid_time=1000)
# By label - Positional
data_array_lp = data.tp.loc['2004-09-23', :, :]  # [valid_time, Latitude, Longitude]
# By label - by name
data_array_ln = data.tp.sel(valid_time='2004-09-23')

# Indexing in multiple coordinates
data_array_multiple1 = data.tp.loc['2004-09-23', 36.5, 23.5]  # [valid_time, Latitude, Longitude]
data_array_multiple2 = data.tp.sel(valid_time='2004-09-23', latitude=36.5, longitude=23.5)

# Plotting (https://docs.xarray.dev/en/latest/user-guide/plotting.html)
# One Dimension Plots - Timeseries and Histogram
plot_1d = data.tp.isel(latitude=15, longitude=20)
plot_1d.plot()  # Generic plot
plot_1d.plot.line(color='red', marker='o')  # Line plot with specific color and marker_style
plot_1d.plot.hist()  # Histogram
plt.show()

# Multiple timeseries plot
data.tp.isel(longitude=10, latitude=[19, 21, 22]).plot.line(x='valid_time')

# Two Dimension Plots
plt_2d = data.tp.sel(valid_time='2022-03-20')
plt_2d.plot()
plt_2d.plot.contour()  # Contour plot
plt_2d.plot.contourf()  # Filled contour plot
plt.show()

# Three dimensions plot
plt_2d.plot.surface()
plt.show()

