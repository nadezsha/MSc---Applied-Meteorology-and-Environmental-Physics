'''
According to the World Meteorological Organisation, the "first
tropopause" is conventionally defined as the lowest level at which the
lapse rate decreases to 2°C/km or less, provided also that the average
lapse rate between this level and all higher levels within 2 km does not
exceed 2°C/km.
'''

import pandas as pd

# import data (only kept the temp and hght for the dataframe)
df = pd.read_csv("LGAT12Z2712.txt", sep='\s+', usecols =['HGHT', 'TEMP'])
#print(df.head())

# calculate the temp and hght differences usind .diff() and then calculate the laspe rate for each row
df['dT (°C)'] = df['TEMP'].diff()
df['dZ (m)'] = df['HGHT'].diff()
df['Lapse Rate (°C/km)'] = df['dT (°C)'] / df['dZ (m)'] * 1000

# drop the first row since it has NaN values for dT and dZ (no ground/previous data)
df = df.dropna().reset_index(drop=True)

# define function that finds the lowest level where the lapse rate decreases to 2°C/km or less
def find_lowest_height(df, max_lapse_rate=2.0, upper_layer=2000):
    for i in range(len(df)):
        if abs(df.loc[i, 'Lapse Rate (°C/km)']) <= max_lapse_rate:
            target_height = df.loc[i, 'HGHT']
            higher_levels = df[(df['HGHT'] >= target_height) & (df['HGHT'] <= target_height + upper_layer)]
            avg_lapse_rate = higher_levels['Lapse Rate (°C/km)'].abs().mean()
            
            if avg_lapse_rate <= max_lapse_rate:
                return target_height, avg_lapse_rate
            
    return None, None

# call the function to find the lowest height meeting both conditions
lowest_height, avg_lapse_rate_in_upper_levels = find_lowest_height(df)

# print the result
if lowest_height is not None:
    print(f"The lowest level where the absolute lapse rate is <= 2°C/km and the average absolute lapse rate in the next 2 km is <= 2°C/km is {lowest_height} meters.")
    print(f"The average absolute lapse rate in this 2 km window is {avg_lapse_rate_in_upper_levels:.2f} °C/km.")
else:
    print("No such height, where both conditions are satisfied, was found.")
