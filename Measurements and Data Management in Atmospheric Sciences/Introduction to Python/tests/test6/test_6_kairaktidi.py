import numpy as np
import pandas as pd

# TASK a) read file and create dataframe
df = pd.read_csv("uv_15_18_425_135.csv", sep=',', parse_dates=True)
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time') 
df.head()

# TASK b) calculate mean montlhy values (4 years * 12 months = 48 values)
df.resample("M").mean().round(2)

# TASK c) calculate mean yearly values (4 years = 43 values)
df.resample("Y").mean().round(2)

# TASK d) calculate mean monthly values for the whole dataframe (12 months total)
months=df.index.month
monthly_avg=df.groupby(months).uvb.mean()
print(round(monthly_avg,2))