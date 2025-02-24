import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter
import imageio
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import pearsonr


# TASK 1


# read SLP data (era5 single level)
ds_slp = xr.open_dataset("data\\single_levels.nc")
slp = ds_slp['msl'] / 100  # convert from Pa to hPa

# read wind data (era5 pressure levels)
ds_wind = xr.open_dataset("data\\wind_levels.nc")
u_wind = ds_wind['u'].sel(pressure_level=1000) 
v_wind = ds_wind['v'].sel(pressure_level=1000)

# dimensions
lats = ds_slp.latitude
lons = ds_slp.longitude
valid_times = ds_slp['valid_time'].values  

# list to hold the filenames of the saved plots for GIF creation later on
output_folder = "figures"
os.makedirs(output_folder, exist_ok=True)
image_files = []

# loop through the available valid times (6-hour intervals)
for valid_time_index in range(0, len(valid_times), 6): 
    current_time = valid_times[valid_time_index]

    formatted_time = np.datetime64(current_time).astype('datetime64[s]').astype(str).replace(":", "-")

    # get the SLP and wind data for the current time index
    slp_smooth = gaussian_filter(slp[valid_time_index], sigma=2)
    
    # plotting
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([-10, 40, 25, 45], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, edgecolor='dimgray')  
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='slategray') 
    ax.add_feature(cfeature.LAND, facecolor='wheat')  
    ax.add_feature(cfeature.OCEAN, facecolor='lightsteelblue') 

    # plot SLP contours (isobars) with color 
    contour = ax.contour(lons, lats, slp_smooth, levels=np.arange(980, 1020, 2), colors='purple', linewidths=2)
    ax.clabel(contour, inline=True, fontsize=10, fmt ='%d')

    # plot wind barbs, skipping a few for better visualisation
    ax.barbs(lons[::5], lats[::5], u_wind[valid_time_index, ::5, ::5], v_wind[valid_time_index, ::5, ::5], length=6, color='black')

    formatted_display_time = np.datetime_as_string(current_time, unit='m')
    plt.title(f"Medicane Zorbas - {formatted_display_time}")

    plot_filename = os.path.join(output_folder, f"medicane_{formatted_time}.png")
    plt.savefig(plot_filename)

    # add the image filename to the list for GIF creation
    image_files.append(plot_filename)
    plt.close()

# create a GIF using the saved images
gif_filename = os.path.join(output_folder, "medicane_zorbas.gif")
with imageio.get_writer(gif_filename, mode='I', duration=6) as writer:  # duration in seconds per frame
    for filename in image_files:
        image = imageio.imread(filename)
        writer.append_data(image)

# using "print" as a way to check on the codes' progress
print(f"GIF created and saved as {gif_filename}")


# TASK 2


# picking a date and time according to the first tasks' figures
selected_time_index = np.where(valid_times == np.datetime64('2018-09-29T06:00:00'))[0][0]  # Example index, modify as needed
current_time = valid_times[selected_time_index]

# gradient is in degrees and i wanna represent it in meters on the map, so we multiply by
# 111000 (m) because 1° is equal to 111km
du_dy, du_dx = np.gradient(u_wind[selected_time_index], lats * 111000, lons * 111000) 
dv_dy, dv_dx = np.gradient(v_wind[selected_time_index], lats * 111000, lons * 111000)

relative_vorticity = dv_dx - du_dy

# calculating the max value to print on the figures' title
max_vorticity = np.max(relative_vorticity)
max_location = np.unravel_index(np.argmax(relative_vorticity), relative_vorticity.shape)
max_lat, max_lon = lats[max_location[0]], lons[max_location[1]]

# plotting
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent([10, 30, 32, 42], crs=ccrs.PlateCarree())

ax.add_feature(cfeature.COASTLINE)  
ax.add_feature(cfeature.BORDERS, linestyle=':') 
ax.add_feature(cfeature.LAND)  
ax.add_feature(cfeature.OCEAN) 

c = ax.contourf(lons, lats, relative_vorticity, cmap='coolwarm', levels=20)
plt.colorbar(c, ax=ax, orientation='horizontal', label='Relative Vorticity (1/s)')
plt.title(f"Relative Vorticity at 1000hPa - {str(np.datetime_as_string(current_time, unit='m'))}, Max Vorticity: {max_vorticity:.2e} 1/s at ({max_lat:.2f}, {max_lon:.2f})")

formatted_time = str(current_time).replace(':', '-')
plot_filename = os.path.join(output_folder, f"relative_vorticity_{formatted_time}.png")
plt.savefig(plot_filename)
plt.close()

# again, using printing to check on the codes' progress
print(f"Relative vorticity plot saved as {plot_filename}")


# TASK 3 


# cds = climate data store
cds_vorticity = ds_wind['vo'].sel(pressure_level=1000) 
cds_vorticity_at_time = cds_vorticity.sel(valid_time=current_time) 

# calculate the difference between the two vorticities
vorticity_difference = cds_vorticity_at_time - relative_vorticity

# plotting the difference
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent([10, 30, 32, 42], crs=ccrs.PlateCarree())

ax.add_feature(cfeature.COASTLINE)  
ax.add_feature(cfeature.BORDERS, linestyle=':') 
ax.add_feature(cfeature.LAND)  
ax.add_feature(cfeature.OCEAN)

c = ax.contourf(lons, lats, vorticity_difference, cmap='coolwarm', levels=20, alpha=0.6)
plt.colorbar(c, ax=ax, orientation='horizontal', label='Vorticity Difference (1/s)')

plt.title(f"Vorticity Difference at 1000hPa - {str(np.datetime_as_string(current_time, unit='m'))}")
formatted_time = str(current_time).replace(':', '-')
plot_filename = os.path.join(output_folder, f"vorticity_difference_{formatted_time}.png")
plt.savefig(plot_filename)
plt.close()

# check on codes progress
print(f"Vorticity difference plot saved as {plot_filename}")

# adding statistical analysis
# calculate MAE (Mean Absolute Error)
mae = mean_absolute_error(cds_vorticity_at_time.values.flatten(), relative_vorticity.flatten())

# calculate RMSE (Root Mean Squared Error)
rmse = np.sqrt(mean_squared_error(cds_vorticity_at_time.values.flatten(), relative_vorticity.flatten()))

# calculate Pearson correlation coefficient
pearson_corr, _ = pearsonr(cds_vorticity_at_time.values.flatten(), relative_vorticity.flatten())

# print out the results
print(f"Mean Absolute Error (MAE): {mae:.6f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
print(f"Pearson's Correlation Coefficient: {pearson_corr:.4f}")