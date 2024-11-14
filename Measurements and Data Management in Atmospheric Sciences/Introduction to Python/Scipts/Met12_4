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
