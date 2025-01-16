"""Manipulating NETCDF4 binaries using xarray
Installation: > pip install xarray or
conda install -c conda-forge xarray dask netCDF4 bottleneck"""
import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('netcdf_manipulation_test.nc')

"""A data structure has dimensions, coordinates, variables and attributes
- the dimensions specify the number of elements of each data coordinate, their names should be understandable 
and specific
- the attributes provide some information about the file (metadata)
- the variables contain the actual data. In our file there are five variables. All have the dimensions 
[time, latitude, longitude], so we can expect an array of size [17544, 3, 3]
the coordinates locate the data in space and time"""

print(ds)

# Check a specific coordinate e.g. longitude
print(ds.longitude)

# Variables can also be accessed directly from the dataset:
ds.t
ds.r

# Simple analysis - averages

t_mean_temporal = ds.t.mean(dim='time')
print(t_mean_temporal)
t_mean_temporal.plot()
plt.show()

t_mean_spatial = ds.t.mean(dim='longitude')
print(t_mean_spatial)
t_mean_spatial.plot()
plt.show()

print(ds.t.mean())
ds.t.mean().item()

# Producing 1d plots
ds.t.mean(dim='longitude').plot()
plt.show()