import pandas as pd
import matplotlib.pyplot as plt

#TASK a) Read only max temp (ΤΧ) and min temp (ΤΝ) and create datetime dataframe
columns = ['Date', 'Tmax', 'Tmin']
df = pd.read_csv("Hellenicon_data.csv", sep=';', usecols=columns, index_col=[0], parse_dates=True)
df.head()

# TASK b) calculate and print Tmax_mean and Tmin_mean for the reference period 1961-1990.
new_df = df.loc[(df.index >= '1961-01-01') & (df.index < '1990-12-31')]
new_df.head()
print(new_df.Tmax.mean())
print(new_df.Tmin.mean())
      
# TASK c) calculate and save in a file the timeseries anomalies of Tmax and Tmin for the reference period
new_df['Tmax_anomaly'] = new_df["Tmax"] - new_df["Tmax"].mean()
new_df['Tmin_anomaly'] = new_df["Tmin"] - new_df["Tmin"].mean()
new_df = new_df.drop(['Tmax','Tmin'], axis = 1)
new_df.head()
new_df.to_csv("Anomalies.csv", sep=";", float_format = '%.1f')

# TASK d) create and save the anomalies plot of step c) (one figure per parameter)
plt.plot(new_df['Tmax_anomaly'], label="$\Delta$Tmax")
plt.xlabel("Date")
plt.ylabel("$\Delta T_{max}\ (K)$")
plt.title("Tmax anomaly")
plt.legend(loc='best')
plt.savefig('Tmax_Anomaly' + '.jpeg')
plt.show()

plt.plot(new_df['Tmin_anomaly'], label="$\Delta$Tmin")
plt.xlabel("Date")
plt.ylabel("$\Delta T_{min}\ (K)$")
plt.title("Tmin anomaly")
plt.legend(loc='best')
plt.savefig('Tmin_Anomaly' + '.jpeg')
plt.show()


# TASK e) create and save the anomalies boxplot in one figure for all parameters
fig, ax = plt.subplots()
labels = ['','Tmax_anomaly', 'Tmin_anomaly']
df.boxplot(ax=ax, notch=True, bootstrap=100)
ax.set_xticks(range(3))
ax.set_xticklabels(labels)
ax.set_title('Anomalies Boxplot')
plt.savefig('Anomalies_Boxplot' + '.jpeg')
plt.show()
