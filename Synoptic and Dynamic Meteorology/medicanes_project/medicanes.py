import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter
import imageio
import os

# read SLP data (era5 single level)
ds_slp = xr.open_dataset("data\\single_levels.nc")
slp = ds_slp['msl'] / 100  # convert from Pa to hPa

# read wind data (pressure levels)
ds_wind = xr.open_dataset("data\\wind_levels.nc")
u_wind = ds_wind['u'].sel(pressure_level=1000) 
v_wind = ds_wind['v'].sel(pressure_level=1000)

# dimensions
lats = ds_slp.latitude
lons = ds_slp.longitude
valid_times = ds_slp['valid_time'].values  

# list to hold the filenames of the saved plots for GIF creation
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

    # plot wind barbs
    ax.barbs(lons[::5], lats[::5], u_wind[valid_time_index, ::5, ::5], v_wind[valid_time_index, ::5, ::5], length=6, color='black')

    plt.title(f"Medicane Zorbas - {str(current_time)}")

    plot_filename = os.path.join(output_folder, f"medicane_{formatted_time}.png")
    plt.savefig(plot_filename)

    # add the image filename to the list for GIF creation
    image_files.append(plot_filename)

    plt.close()

# Create a GIF using the saved images
gif_filename = os.path.join(output_folder, "medicane_zorbas.gif")
with imageio.get_writer(gif_filename, mode='I', duration=1.5) as writer:  # Duration in seconds per frame
    for filename in image_files:
        image = imageio.imread(filename)
        writer.append_data(image)

print(f"GIF created and saved as {gif_filename}")