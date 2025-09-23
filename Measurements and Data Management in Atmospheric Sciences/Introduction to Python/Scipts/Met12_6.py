import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# generate random floating point values

from random import seed
from random import gauss

# Quick and dirty plots

df = pd.read_csv("Hellenicon_data.csv", sep=';', index_col=[0], parse_dates=True)
print(df.head())

df.plot()
plt.show()

df["r"].plot()
df.r.plot()
plt.show()

#df["Tmax"].plot()
#df["Tmax"].plot().set_ylabel("Tmax ($^\circ C$)")
df["Tmax"].plot().set_xlabel("Years")
plt.show()

# More elaborated plots

plt.plot(df["Tmax"])
plt.xlabel("Date")
plt.ylabel("Tmax ($^\circ$C)")
plt.show()

plt.plot(df["Tmax"], "+g")
#plt.xlabel("Date")
#plt.ylabel("Tmax ($^\circ$C)")
plt.show()

plt.plot(df["Tmax"], label="Tmax")
plt.plot(df["Tmin"], label="Tmin")
#plt.xlabel("Date")
#plt.ylabel("T ($^\circ$C)")
plt.legend()
plt.show()

plt.plot(df["Tmax"], label="Tmax")
plt.plot(df["Tmin"], label="Tmin")
#plt.xlabel("Date")
#plt.ylabel("T ($^\circ$C)")
plt.legend(loc='best')
plt.show()

plt.plot(df["Tmax"] - df["Tmax"].mean(), label="$\Delta$Tmax")
#plt.xlabel("Date")
#plt.ylabel("$\Delta Tmax_{max}\ (K)$")
#plt.title("Tmax anomaly over the whole period")
plt.legend(loc='best')
plt.show()

# Double axis graphs

fig, ax1 = plt.subplots()
ax1.plot(df["Tmin"], color='b')
ax1.set_xlabel('Date')
#plt.show()

# Make the y-axis label, ticks and tick labels match the line color.
#ax1.set_ylabel("Tmin ($^\circ C$)", color='b')
ax1.tick_params('y', colors='b')
#plt.show()

ax2 = ax1.twinx()
ax2.plot(df['r'], color='r')
#ax2.set_ylabel('Precipitation (mm)', color='r')
#ax2.tick_params('y', colors='r')

plt.show()

fig.tight_layout()

plt.title("A double y-axis graph example")
#plt.savefig('Tmin-Precipitation' + '.pdf')
plt.savefig('Tmin-Precipitation.pdf' , format = 'pdf')
plt.show()

# Scatter plots
x = [5, 7, 8, 7, 2, 17, 2, 9, 4, 11, 12, 9, 6]
y = [99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86]

#plt.plot(x, y)
plt.scatter(x,y)
plt.show()

plt.scatter(df['Tmin'], df['r'])
plt.show()

x = np.random.normal(5.0, 1.0, 1000)
y = np.random.normal(10.0, 2.0, 1000)

plt.scatter(x, y)
plt.xlabel('x variable')
plt.ylabel('y variable')
plt.legend('Example of scatter plot', loc='best')
plt.show()

# Saving plots to file
plt.savefig('my_figure.jpg')

# Bar charts

df = pd.DataFrame(np.random.rand(6, 4), index=['one', 'two', 'three', 'four', 'five', 'six'],
                columns=pd.Index(['A', 'B', 'C', 'D'], name='Genus'))

df.head()

df.plot(kind='bar')
plt.show()

df.plot(kind='bar', stacked=True)
plt.show()

df.plot(kind='barh', stacked=True, alpha=0.8)  # alpha (0, 1]: defines the RGB color intensity
plt.show()

# Histograms
df = pd.read_csv("Hellenicon_data.csv", sep=';', index_col=[0], parse_dates=True)

df['Tmax'].hist(bins=100)
plt.show()

# Kernel density estimate (KDE) plots

df['Tmax'].plot(kind='kde')
plt.show()


# KDE with pseudo normalized data

# seed random number generator
seed(1)  # Initializes the random number generator

# generate random numbers between 0-1
my_random_numbers = []
for _ in range(17167):
    value = gauss(0, 1)
    #my_random_numbers.append(value)

df_random = pd.DataFrame(my_random_numbers)
df_random.plot(kind='kde')
plt.show()


# Plot boxplots

df.boxplot(column='Tmax')

fig, ax = plt.subplots()
df.boxplot(ax=ax, positions=[1, 2, 3], notch=True, bootstrap=5000)
#ax.set_xticks(range(4))
#ax.set_xticklabels(range(4))
plt.show()

fig, ax = plt.subplots()
df.boxplot(column='Tmax', ax=ax, positions=[1], notch=True, bootstrap=5000)
#ax.set_xticks(range(4))
#ax.set_xticklabels(range(4))
plt.show()
