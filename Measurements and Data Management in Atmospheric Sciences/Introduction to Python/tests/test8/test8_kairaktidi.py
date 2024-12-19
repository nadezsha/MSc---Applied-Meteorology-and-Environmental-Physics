import pandas as pd
import matplotlib.pyplot as plt

# TASK a) reads concentration values of each particle category as a timeseries on a dataframe 
columns = ['Date/time', 'PM-10', 'PM-2.5', 'PM-1.0']
df = pd.read_csv("grimmnewpatrasport_overall_2013.csv", sep=';',usecols=columns, encoding='unicode_escape', index_col=[0], parse_dates=True, skiprows = 1)
df.head()

# TASK b) saves each one of the three timeseries on a seperate file
df['PM-10'].to_csv("PM10.csv", sep=";", float_format = '%.1f')
df['PM-2.5'].to_csv("PM2.5.csv", sep=";", float_format = '%.1f')
df['PM-1.0'].to_csv("PM1.0.csv", sep=";", float_format = '%.1f')

# TASK c) calculates and prints the mean and std of each timeseries for the whole period (with appropriate significant digits)

# μπορούμε να δουλέψουμε κατευθείαν με τις στήλες του αρχικού πλασίου δεδομένων αλλά επειδή η εκφώνηση
# δηλώνει να γίνει η επεξεργασία για κάθε χρονοσειρά, κάνουμε ξάνα import τα δεδομένα

# η τυπική απόκλιση εκφράζεται με 1 μόνο σημαντικό ψηφίο
# στον κώδικα έχω θέσει όχι ένα σημαντικό αλλά ένα δεκαδικό καθώς δεν μπορούσα να σκεφτώ κάτι καλύτερο

df10 = pd.read_csv("PM10.csv", sep=';', encoding='unicode_escape', index_col=[0], parse_dates=True)
df2 = pd.read_csv("PM2.5.csv", sep=';', encoding='unicode_escape', index_col=[0], parse_dates=True)
df1 = pd.read_csv("PM1.0.csv", sep=';', encoding='unicode_escape', index_col=[0], parse_dates=True)

df10['PM-10'].mean().round(1)
df10['PM-10'].std().round(1)

df2['PM-2.5'].mean().round(1)
df2['PM-2.5'].std().round(1)

df1['PM-1.0'].mean().round(1)
df1['PM-1.0'].std().round(1)

# παρατήρηση : τα δεδομένα από το grimm περιέχουν και ακραίες τιμές, γι αυτό η τυπική απόκλιση βγαίνει τόσο μεγάλη

# TASK d) shows the time where each timeseries gets its max and min value for the whole period
df10['PM-10'][df10['PM-10'] == df10['PM-10'].max()].index
df10['PM-10'][df10['PM-10'] == df10['PM-10'].min()].index

df2['PM-2.5'][df2['PM-2.5'] == df2['PM-2.5'].max()].index
df2['PM-2.5'][df2['PM-2.5'] == df2['PM-2.5'].min()].index

df1['PM-1.0'][df1['PM-1.0'] == df1['PM-1.0'].max()].index
df1['PM-1.0'][df1['PM-1.0'] == df1['PM-1.0'].min()].index

# TASK e) creates the boxplot of each timeseries in one figure
fig, ax = plt.subplots()
labels = ['','PM10', 'PM2.5', 'PM1.0']
df.boxplot(column='PM-10', ax=ax, positions=[1], notch=True, bootstrap=100)
df.boxplot(column='PM-2.5', ax=ax, positions=[2], notch=True, bootstrap=100)
df.boxplot(column='PM-1.0', ax=ax, positions=[3], notch=True, bootstrap=100)
ax.set_title("Grouped boxplot of all PM concentrations")
ax.set_xlabel('PM concentrations')
ax.set_ylabel('Concentration $\mu m%g/m ^{3}')
ax.set_xticks(range(4))
ax.set_xticklabels(labels)
plt.show()