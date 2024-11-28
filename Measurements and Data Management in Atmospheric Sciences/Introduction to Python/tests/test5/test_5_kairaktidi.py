import pandas as pd
import numpy as np

#TASK 1
df = pd.read_csv("Meteo_1h_2022_qc.csv", sep=',')
df = df.set_index("Time")

#TASK 2
n_df = pd.DataFrame()
n_df['ws'] = df['ws']
n_df['wd'] = df['wd']
n_df['zon'] = -(df['ws']*np.sin(np.deg2rad(df['wd'])))
n_df['mes'] = -(df['ws']*np.cos(np.deg2rad(df['wd'])))

#TASK 3
n_df.to_csv("results.csv", sep=";")
print(n_df)
