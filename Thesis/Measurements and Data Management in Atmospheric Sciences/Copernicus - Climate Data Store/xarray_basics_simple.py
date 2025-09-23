import xarray as xr
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')

filename ='tp_1960-2022_Greece.nc'
data = xr.open_dataset(filename)  # Open filename

# Plot histogram of total precipitation near Kalavryta from 1960 to 2022
plt_data = data.tp.sel(latitude=38, longitude=22) * 1000  # Subset dataset and convert meters to mm

plt_data.plot.hist(edgecolor='k', zorder=10)  # Histogram plot
plt.xlabel('Total Precipitation (mm)', fontweight='bold', fontsize=16)
plt.ylabel('Frequency', fontweight='bold', fontsize=16)
plt.title('Kalavryta (1960-2022)', fontweight='bold', fontsize=18)
plt.grid()
plt.tight_layout()

plt.savefig('save_path')
plt.close()

# Plot 2d plot of 2015-01-12
plt_2d = data.tp.sel(valid_time='2015-01-12')

plot = plt_2d.plot(cmap='jet', cbar_kwargs={'label': 'Total Precipitation (mm)'})
plt.xlabel('Longitude (°)', fontweight='bold', fontsize=16)
plt.ylabel('Latitude (°)', fontweight='bold', fontsize=16)
plt.title('2015-01-12', fontweight='bold', fontsize=18)
plt.grid()
plt.tight_layout()

plt.savefig('save_path2')
plt.close()
