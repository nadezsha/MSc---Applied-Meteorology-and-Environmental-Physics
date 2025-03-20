import statistics
from scipy import stats
import stemgraphic
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
import seaborn as sn

# Robustness - Resistance
data_set1= [11, 12, 13, 14, 19, 16, 17, 18, 15]
data_set3= [11, 12, 13, 14, 19, 16, 17, 18, 51]
data_set2= [11, 12, 13, 14, 91, 16, 17, 18, 15]

data_set1.sort()

print(data_set1)

# Mean 
my_mean1 = statistics.mean(data_set1)  
my_mean2 = statistics.mean(data_set2)
print(my_mean1)
print(my_mean2)

# Alternative package trimmed mean
my_mean = stats.tmean(data_set1)
print(my_mean)

my_mean = stats.tmean(data_set1, (11,15)) # Ignores values outside the interval in parenthesis
print(my_mean)

# Median
my_median1 = statistics.median(data_set1)
my_median2 = statistics.median(data_set2)

print(my_median1)
print(my_median2)

# Quantiles
my_quantiles1 = statistics.quantiles(data_set1)
my_quantiles2 = statistics.quantiles(data_set2)
print(my_quantiles1)
print(my_quantiles2)

print(statistics.quantiles(data_set3, method='inclusive'))
print(statistics.quantiles(data_set3, method='exclusive'))

# Interquantile range
my_IQR1 = my_quantiles1[2]-my_quantiles1[0]
my_IQR2 = my_quantiles2[2]-my_quantiles2[0]
print(my_IQR1)
print(my_IQR2)

my_stddev1 = statistics.stdev(data_set1)
my_stddev2 = statistics.stdev(data_set2)
print(my_stddev1)
print(my_stddev2)

# Skewness - Kyrtosis
stats.skew(data_set1)
stats.kurtosis(data_set1)
hellenicon = pd.read_csv('Hellenicon_data.csv', sep=';', index_col=0, parse_dates=True)
hellenicon = hellenicon.dropna()

# Histograms
plt.hist(hellenicon.Tmin)
plt.show()
plt.hist(hellenicon.Tmax)
plt.show()
stats.skew(hellenicon['Tmin'])
stats.kurtosis(hellenicon.Tmin)
plt.hist(hellenicon.r)
plt.show()
stats.skew(hellenicon.r)
stats.kurtosis(hellenicon.r)


# Stem - leaf display
s = [0.1,0.2,0.4,1.5,1.9,2.1,2.2,2.6,2.7,2.9,3.3,3.2,3.1]
fig, ax = stemgraphic.stem_graphic(s)
plt.show()
Temperature = pd.read_csv("uhi_temperatures.csv")
fig, ax = stemgraphic.stem_graphic(hellenicon.Tmin)
plt.show()
RH = pd.read_csv("uhi_rh.csv")
fig, ax = stemgraphic.stem_graphic(RH)
plt.show()

# Boxplots
plt.boxplot(hellenicon.Tmax)
plt.show()
plt.boxplot(RH)
plt.show()

# Histograms
plt.hist(Temperature)
plt.show()
plt.hist(RH)
plt.show()

# Cummulative frequency distribution
T_cumfreq = stats.cumfreq(hellenicon['Tmax'])
x = T_cumfreq.lowerlimit + np.linspace(0, T_cumfreq.binsize*T_cumfreq.cumcount.size, 
                                       T_cumfreq.cumcount.size)
plt.bar(x, T_cumfreq.cumcount, width=T_cumfreq.binsize)
plt.show()

# Empirical Cummulative Distribution Function
plt.figure(figsize=(8,6))
sns.ecdfplot(hellenicon, x="Tmax")
plt.show()

plt.figure(figsize=(8,6))
sns.ecdfplot(hellenicon, x="r")
plt.show()

# Anomaly
Temperature - Temperature.mean()
(Temperature - Temperature.mean()).plot()
plt.show()

RH - RH.mean()
(RH - RH.mean()).plot()
plt.show()

# Normalised residual
(Temperature - Temperature.mean())/Temperature.std()
((Temperature - Temperature.mean())/Temperature.std()).plot()
plt.show()

# Normalisation effect
print((Temperature - Temperature.mean()).describe())
print(((Temperature - Temperature.mean())/Temperature.std()).describe())

# Scater plot
plt.scatter(Temperature, RH)
plt.show()

# Pearson
print(stats.pearsonr([1, 2, 3, 4, 5], [10, 9, 2.5, 6, 4]))
plt.scatter([1, 2, 3, 4, 5], [10, 9, 2.5, 6, 4])
plt.show()

print(stats.pearsonr([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]))

# Spearman
print(stats.spearmanr([1, 2, 3, 4, 5], [10, 9, 2.5, 6, 4]))

print(stats.spearmanr([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]))

# Kendall
print(stats.kendalltau([1, 2, 3, 4, 5], [10, 9, 2.5, 6, 4]))

print(stats.kendalltau([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]))

# Example 3.6 Wilks
x1 = [0, 1, 2, 3, 5, 7, 9, 12, 16, 20]
y1 = [0, 3, 6, 8, 11, 13, 14, 15, 16, 16]
x2 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20]
y2 = [8, 4, 9, 2, 5, 6, 3, 1, 7, 17]

plt.scatter(x1, y1)
plt.show()
print(stats.pearsonr(x1, y1))
print(stats.spearmanr(x1, y1))
print(stats.kendalltau(x1, y1))

plt.scatter(x2, y2)
plt.show()
print(stats.pearsonr(x2, y2))
print(stats.spearmanr(x2, y2))
print(stats.kendalltau(x2, y2))

# Autocorrelation

df = pd.read_csv('SMAS_Ithaka_Jan1987.csv')

plt.xlabel('Day')
plt.ylabel('T_max_Ithaka (°C)')
plt.plot(df['Day'], df['MaxTem_Ith'])
plt.show()

df.index = pd.to_datetime(df['Day'], format = '%d')
plt.xlabel('Date')
plt.ylabel('T_max_Ithaka (°C)')
plt.plot(df['MaxTem_Ith'])
plt.show()

print(df['MaxTem_Ith'].autocorr(lag=1))

plot_acf(df['MaxTem_Ith'])
plt.show()

# Correlation matrix

corr_matr = df.corr(method='pearson')
print(corr_matr)
sn.heatmap(corr_matr, annot=True)
plt.show()

corr_matr = df.corr(method='spearman')
print(corr_matr)
sn.heatmap(corr_matr, annot=True)
plt.show()

corr_matr = df.corr(method='kendall')
print(corr_matr)
sn.heatmap(corr_matr, annot=True)
plt.show()