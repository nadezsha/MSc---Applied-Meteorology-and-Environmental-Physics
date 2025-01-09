'''Saving files in binary formats'''
import pandas as pd

df=pd.read_csv('Meteo_1min_2018_qc.csv', index_col=[0], parse_dates=True)

df.to_hdf('Meteo_1min_2018_qc.h5', key='df')

df.to_parquet('Meteo_1min_2018_qc.gzip', compression='gzip')

df1=pd.read_parquet('Meteo_1min_2018_qc.gzip')

df1.to_csv("Meteo_test.csv")