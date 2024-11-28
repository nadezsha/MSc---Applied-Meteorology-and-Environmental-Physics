# Basic pandas aggregations and statistics
import pandas as pd

df = pd.read_csv("Hellenicon_data.csv", sep=';')
print(df.head())

# It is necessary to define the index
df = pd.read_csv("Hellenicon_data.csv", sep=';', index_col=[0], parse_dates=True)
print(df.head())

# Now the dataframe has become a time series and we can do general statistics

print(df.describe())
print(df["Tmax"].describe())

print(df['Tmax'][df['Tmax'] == df['Tmax'].max()])
print(df['Tmax'][df['Tmax'] == df['Tmax'].min()])
print(df['Tmin'][df['Tmin'] == df['Tmin'].max()])
print(df['Tmin'][df['Tmin'] == df['Tmin'].min()])
print(df['r'][df['r'] == df['r'].max()])
print(df.Tmax[(df.Tmax >20) & (df.Tmax < 25)])

# Various aggregations

df.resample("M").mean()
df["Tmax"].resample("M").mean()
df["Tmin"].resample("M").mean()
df["r"].resample("M").sum()

df["Tmax"].resample("Y").mean()
df["Tmin"].resample("Y").mean()
df["r"].resample("Y").sum()

months=df.index.month
monthly_avg=df.groupby(months).Tmax.mean()

week=df.index.weekday
weekly_avg=df.groupby(week).Tmax.mean()