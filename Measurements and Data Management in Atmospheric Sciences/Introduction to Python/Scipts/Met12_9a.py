"""Manipulating NETCDF4 binaries using xarray
Installation: > pip install xarray or
conda install -c conda-forge xarray dask netCDF4 bottleneck"""
import xarray as xr
import matplotlib.pyplot as plt

df = xr.open_dataset('T_1000_Patras.nc')
print(df.variables)

df['t'].sel(longitude=21.75, latitude=38.25).plot() 
plt.show()

