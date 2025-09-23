import pandas as pd
import numpy as np
import pymannkendall
from scipy.stats import pearsonr
import seaborn as sns
import matplotlib.pyplot as plt

# TASK 1 : create a dataframe that consists of
# (a) daily precipitation sum, 
# (b) daily mean temperatures,
# (c) daily max temperatures,
# (d) daily min temperatures and
# (e) daily wind speed values.
# save this file "Meteo_1d_2024_qc.csv"

columns = ['Time', 'T', 'phi', 'ws', 'wd', 'wg', 'precip', 'pres', 'bat']
df = pd.read_csv('Meteo_1min_2024_qc.csv', sep=',', index_col=[0], parse_dates=True,
                  usecols=columns)
df = df.drop(['wd', 'wg', 'pres', 'bat'], axis=1)

df_daily = df.resample('D').agg({
    'precip': 'sum',
    'T': 'mean',
    'ws': 'mean'
})

df_daily = df_daily.rename(columns={'T': 'T_mean'})
df_daily['T_max'] = df['T'].resample('D').max()
df_daily['T_min'] = df['T'].resample('D').min()

print(df_daily.head())
df_daily.to_csv("Meteo_1d_2024_qc.csv")


# TASK 2 : from the daily dataset, calculate the range (anomaly) between the
#  maximum and minimum daily temperature for the summer season. Then, 
# check whether a statistically significant trend is observed at a 95% confidence level 
# by applying the simple Mann-Kendall statistical test to the variables, 
# as well as to precipitation during the summer season.
# Provide a commentary on the results.

df_summer = df_daily[df_daily.index.to_series().dt.month.isin([6, 7, 8])].dropna()
df_summer['T_anomaly'] = df_summer['T_max'] - df_summer['T_min']

mk_Tmax = pymannkendall.original_test(df_summer['T_max'])
mk_Tmin = pymannkendall.original_test(df_summer['T_min'])
mk_precip = pymannkendall.original_test(df_summer['precip'])
mk_Tanomaly = pymannkendall.original_test(df_summer['T_anomaly'])

print("Mann-Kendall Test Results:")
print(f"T_max Trend: {mk_Tmax.trend}, p-value: {mk_Tmax.p}")
print(f"T_min Trend: {mk_Tmin.trend}, p-value: {mk_Tmin.p}")
print(f"T_range Trend: {mk_Tanomaly.trend}, p-value: {mk_Tanomaly.p}")
print(f"Precip Trend: {mk_precip.trend}, p-value: {mk_precip.p}")

# Results
def interpret_result(mk_result, variable):
    if mk_result.p < 0.05:
        print(f"Statistically significant correlation for: {variable} ({mk_result.trend})")
    else:
        print(f"No statistically significant correlation for: {variable}")

'''
commentary about the results
* No trend is observed for any variable except for the minimum temperature. 
  This also applies to statistical significance, as indicated by the p-values.
* The minimum temperature exhibits a statistically significant increasing trend over time.
'''


# TASK 3: Check whether there is a correlation between the variable(s) that showed 
# a statistically significant trend and the wind speed variable during the summer season
# using the Pearson correlation coefficient and the Pandas library.

significant_vars = []
if mk_Tmax.p < 0.05:
    significant_vars.append('T_max')
if mk_Tmin.p < 0.05:
    significant_vars.append('T_min')
if mk_Tanomaly.p < 0.05:
    significant_vars.append('T_anomaly')
if mk_precip.p < 0.05:
    significant_vars.append('precip')

for var in significant_vars:
    df_corr = df_summer[[var, 'ws']].dropna() 
    corr_coeff, p_value = pearsonr(df_corr[var], df_corr['ws'])

    if p_value < 0.05:
        print(f" Statistically significant correlation for {var} (r = {corr_coeff:.3f})")
    else:
        print(f" No statistically significant correlation for {var}")


# TASK 4 : create a Pearson correlation matrix using seaborn, save the graph and comment
# on the results
correlation_matrix = df_summer.corr(method='pearson')

fig = plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.3f', linewidth=0.5, cbar_kws={'label': 'Pearson Correlation Coefficient'})
plt.title("Pearson Correlation matrix for summer data (LAPUP)")
plt.savefig("correlation_matrix.png")
plt.show()

'''
Commentary on the Results:
* A strong correlation is observed among temperature variables, 
  particularly between maximum and minimum temperatures with the mean temperature, 
  as well as between the max and min temperatures themselves.
* Precipitation exhibits the weakest correlation with the other variables.
* Wind speed also shows relatively low correlation, 
  with its strongest relationship being with mean temperature (0.231).
* Some variables display a slight negative correlation, indicating that as one increases,
  the other tends to decrease.
'''