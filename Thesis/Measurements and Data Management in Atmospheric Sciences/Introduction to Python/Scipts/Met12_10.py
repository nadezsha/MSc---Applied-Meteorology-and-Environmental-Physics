"""Storing and reading NETCDF4 binaries using xarray
Installation: > conda install xarray dask netCDF4 bottleneck"""

import pandas as pd

df=pd.read_csv('Meteo_1min_2018_qc.csv', index_col=[0], parse_dates=True)

df1 = df.to_xarray() # Πρώτα μετατρέπουμε το πλαίσιο δεδομένων pandas σε xarray
print(df1.head())

df1.to_netcdf('Meteo_1min_2018_qc.nc') # Το πλαίσιο δεδομένων xarray σώζεται σε netcdf