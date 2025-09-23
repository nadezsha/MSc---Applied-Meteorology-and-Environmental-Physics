import cdsapi

# Link to search datasets: https://cds.climate.copernicus.eu/datasets
# A Typical download script (API request).

# ----------------------------------------- Single files downloads -------------------------------------------------- 
savename = 'path_to_save_the_file'

dataset = 'reanalysis-era5-land'  # The name of the dataset from which we will download the data
# Below we can see the chosen parameters for each variable available on the dataset.
request = {
    'variable': ['2m_temperature', '10m_u_component_of_wind', '10m_v_component_of_wind', 'total_precipitation'],
    'year': '2023',
    'month': '09',
    'day': ['03', '04', '05'],
    'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00',
             '23:00'],
    'data_format': 'netcdf',
    'download_format': 'unarchived',
    'area': [42, 20, 34, 27]}  # [Upper limit of lat, Left limit of lon, lower limit of lat, right limit of lon]

client = cdsapi.Client()
client.retrieve(dataset, request).download(savename)

# ---------------------------------------- Multiple files downloads -------------------------------------------------- 
for year in range(1990, 2024):  # To download data from 1990 to 2023
    for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        
        # Create a specific filename for each file to avoid overwriting issues
        folder_path = 'path_of_the_folder_to_save_the_files'
        filename = str(year) + '-' + month + '.nc'
        savename = folder_path + filename
        
        dataset = 'reanalysis-era5-land'
        request = {
            'variable': ['2m_temperature', '10m_u_component_of_wind', '10m_v_component_of_wind', 'total_precipitation'],
            'year': str(year),
            'month': month,
            'day': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                    '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'],
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                     '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00',
                     '22:00', '23:00'],
            'data_format': 'netcdf',
            'download_format': 'unarchived',
            'area': [42, 20, 34, 27]}  # [Upper limit of lat, Left limit of lon, lower limit of lat, right limit of lon]
        
        client = cdsapi.Client()
        client.retrieve(dataset, request).download(savename)

