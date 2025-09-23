import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

data1 = xr.open_dataset('C:\\Users\\nefel\\Downloads\\nadia\\kiouts_task03\\1995_2005.nc') 
data2 = xr.open_dataset('C:\\Users\\nefel\\Downloads\\nadia\\kiouts_task03\\2006_2016.nc')
data3 = xr.open_dataset('C:\\Users\\nefel\\Downloads\\nadia\\kiouts_task03\\2017_2025.nc')

combined_data = xr.concat([data1, data2, data3], dim='valid_time') - 273.15
combined_data

# TASK 1 : calculate daily mean temperature (TAVG) and also daily max (TMAX) and min (TMIN)
daily_avg = combined_data['t2m'].sel(latitude = 38.25, longitude = 21.75).resample(valid_time='1D').mean()
daily_max = combined_data['t2m'].sel(latitude = 38.25, longitude = 21.75).resample(valid_time='1D').max() 
daily_min = combined_data['t2m'].sel(latitude = 38.25, longitude = 21.75).resample(valid_time='1D').min()

# Plot daily average temperature (TAVG)
plt.plot(daily_avg.valid_time, daily_avg, label='avg', color='g')
plt.title('Daily Average Temperature (TAVG)')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.savefig('average_temp.png')
plt.show()

# Plot daily max temperature (TMAX)
plt.plot(daily_avg.valid_time, daily_max, color='red')
plt.title('Daily Maximun Temperature (TMAX)')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.savefig('maximum_temp.png')
plt.show()

# Plot daily minimum temperature (TMIN)
plt.plot(daily_avg.valid_time, daily_min, color='b')
plt.title('Daily Minimum Temperature (TMIN)')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.savefig('minimum_temp.png')
plt.show()

# Plot daily max and mean temperature together
plt.plot(daily_avg.valid_time, daily_max, label='max', color='red')
plt.plot(daily_avg.valid_time, daily_min, label='min', color='b')
plt.title('Daily Maximum and Minimum Temperature')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.savefig('max_min_temp.png')
plt.show()


# TASK 2 : calculate the number of days with TMAX > 30°C and plot the timeseries.
# Is the trend is statistically significant?
days_above_30 = daily_max > 30  
days_above_30_count = days_above_30.resample(valid_time='Y').sum()
days_above_30_count = days_above_30_count.to_series()

# plot the count of days with TMAX > 30°C for each year
fig, ax = plt.subplots(figsize=(10, 6))
days_above_30_count.plot.bar(ax=ax, color='purple') 
plt.title('Number of days with TMAX > 30°C per Year')
plt.xlabel('Year')
plt.ylabel('Number of days')
ax.set_xticklabels([str(date.year) for date in days_above_30_count.index], rotation=45)
plt.tight_layout() 
plt.savefig('days_above_30.png')
plt.show()

# statistical test to check if there's a significant trend (typically p-value < 0.05 is considered significant)
years = np.array([date.year for date in days_above_30_count.index])
slope, intercept, r_value, p_value, std_err = stats.linregress(years, days_above_30_count)
print(f"P-value: {p_value}")


# TASK 3 : calculate the number of days with TMAX > 30°C and plot the timeseries. 
# Is the trend is statistically significant?
days_above_20 = daily_min > 20  
days_above_20_count = days_above_20.resample(valid_time='Y').sum()
days_above_20_count = days_above_20_count.to_series()

# plot the count of days with TMIN > 20°C for each year
fig, ax = plt.subplots(figsize=(10, 6))
days_above_20_count.plot.bar(ax=ax, color='purple') 
plt.title('Number of days with TMIN > 20°C per Year')
plt.xlabel('Year')
plt.ylabel('Number of days')
ax.set_xticklabels([str(date.year) for date in days_above_20_count.index], rotation=45)
plt.tight_layout() 
plt.savefig('days_above_20.png')
plt.show()

# statistical test to check if there's a significant trend
years = np.array([date.year for date in days_above_20_count.index])
slope, intercept, r_value, p_value, std_err = stats.linregress(years, days_above_20_count)
print(f"P-value: {p_value}")