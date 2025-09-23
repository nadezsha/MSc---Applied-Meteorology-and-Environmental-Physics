# Import data from files - Conversion to dataframe - Storing a dataframe to a csv file

import pandas as pd

filename = "Hellenicon_data.txt"

df = pd.read_csv(filename)

print(df.head())

#print(df['Year'].head()) -> Unable to read the content as a data frame

# Use the appropriate separators
df = pd.read_csv(filename, sep=r'\s+')

print(df.head())
print(df['Year'].head())  # Now it works

# Reading a single column
df = pd.read_csv(filename, sep=r'\s+', usecols=[0])
print(df.head())

# Indexing - Time stamping
df = pd.read_csv(filename, sep=r'\s+')

df["Date"] = df["Year"].astype(str).str.cat(df[["Month", "Day"]].astype(str), sep="-")

print(df["Date"].head())
print(df["Date"].tail())

print(df.head())

# Removing the useless columns

df.drop(columns=["Year", "Month", "Day"], axis=1, inplace=True)
print(df.head())

# Convert column "Date" to datetime
df["Date"] = pd.to_datetime(df["Date"])
print(df["Date"].head())

# Finally, assign the datetime column as index
df = df.set_index("Date")
print(df.head())

# Store the dataframe to a csv file

df.to_csv("Hellenicon_data.csv", sep=";")

df1 = pd.read_csv("Hellenicon_data.csv", sep=';', index_col=[0], parse_dates=True)

# Block reading

with open('Hellenicon_data.csv', 'r') as file2read:
    print(file2read.read())

with open('Hellenicon_data.csv', 'r') as file2read:
    print(file2read.readline(10))

with open('Hellenicon_data.csv', 'r') as file2read:
    print(file2read.readline())

another_file2read = open('Hellenicon_data.csv')
print(another_file2read.readlines())

# Read and print the entire file line by line

with open('Hellenicon_data.csv', 'r') as file2read:
    for line in file2read:
        print(line, end='')

# Write to a file

f = open("demofile2.txt", "a")
f.write("This is a new line")
f.close()

line_1 = "Stratocumulus"
line_2 = "Cumulonimbus"
line_3 = "Cirrostratus"

f = open("demofile2.txt", "w")
f.write(line_1)
f.write(line_2)
f.write(line_3)
f.close()

f = open("demofile2.txt", "a")
f.write(line_1 + '\n')
f.write(line_2 + '\n')
f.write(line_3 + '\n')
f.close()

# Dataframe structure
df = pd.read_csv("Hellenicon_data.csv", sep=';', index_col=[0], parse_dates=True)

df.columns # Get the columns names
column_name_list = list(df.columns)
print(column_name_list)
print(column_name_list[0])

df.shape # Number of rows and columns of a dataframe (attn. index is not accounted for)
nb_rows = df.shape[0]
nb_cols = df.shape[1]
print(nb_rows, nb_cols)

len(df.columns) # Get the number of columns

# Conditional selection
# Column condition filter
# Example: Get the values of a column exceeding a specified value
df['Tmax'] > 38 # Gives a boolean output
df[df['Tmax'] > 38] # Gives the complete rows for which Tmax satisfies the condition set
df['Tmax'][df['Tmax'] > 38] # Gives only the Tmax column values satisfying the condition set

df['Tmax'][(df['Tmax'] > 35) & (df['Tmax'] <= 38)] # Combined selection of rows with criteria on both colums
df[(df['Tmax'] > 38) & (df['Tmin'] > 25)] # Combined selection of rows with criteria on both colums

# Conditional selection of rows with criteria on more than two colums
df[(df['Tmax'] < 10) & (df['Tmin'] < 5) & (df['r'] > 10)] 

df[(df.index >= '1960-12-1') & (df.index <= '1960-12-31')] # Conditional selection on time index
df['Tmax'][(df.index >= '1960-12-1') & (df.index <= '1960-12-31')] # Conditional selection on time index

# Select data for a specific day, month, year
df[df.index.day == 29]
df[df.index.month == 7]
df[df.index.year == 1960]

# Example: select only February 29 data
df[(df.index.day == 29) & (df.index.month == 2)]

# Get the maximum value of a column
df['Tmax'].max()
df['Tmax'][df['Tmax'] == df['Tmax'].max()]
df['Tmax'][df['Tmax'] == df['Tmax'].max()].index
df['Tmax'][df['Tmax'] == df['Tmax'].max()].index.format()

# Creating multiple dataframes

df = pd.read_csv("40beta00.out", delim_whitespace = 'True', header=None)
Names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance', 
         'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward', 
         'uavgdiffuse upward']

new_dataframe = {}

for i in Names:
    new_dataframe[i] = pd.DataFrame()

new_dataframe['direct horizontal irradiance'][0] = df[0]
new_dataframe['direct horizontal irradiance'][1] = df[1]

# Automatic assignment of all column values
df1 = {}

k = 0

Names1 = ['direct horizontal irradiance', 'diffuse downward horizontal irradiance', 
         'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward', 
         'uavgdiffuse upward']

for i in Names1:
    df1[i] = pd.DataFrame()
    k = k + 1
    df1[i][0] = df[0]
    df1[i][1] = df[k]


    
