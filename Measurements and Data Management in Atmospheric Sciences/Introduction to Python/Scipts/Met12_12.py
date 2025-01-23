"""Manipulating GRIB binaries using xarray
Installation: > conda install xarray dask netCDF4 bottleneck"""

import cfgrib
import xarray as xr

df = xr.open_dataset('T_1000_Patras.grib', engine='cfgrib')
print(df.variables)

print(df.variables['t'][:])
print(df.variables['time'][:])

df1 = df.to_dataframe()
print(df1.head())

df1 = df.to_dataframe().droplevel('latitude').droplevel('longitude')
