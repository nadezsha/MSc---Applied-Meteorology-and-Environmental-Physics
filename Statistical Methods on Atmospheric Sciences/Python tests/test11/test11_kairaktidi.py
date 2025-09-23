import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import os 
from scipy import stats 

# folder to save the figures
os.makedirs('./figures', exist_ok=True)


# 1. Θα φορτώνει και θα διαβάζει τη χρονοσειρά των θερμοκρασιών.
data = pd.read_csv("Meteo_1d_2021_qc.csv", usecols=['Time', 'T'], index_col="Time")
data.index = pd.to_datetime(data.index)
print(data)


# 2. Θα δημιουργεί γράφημα της χρονοσειράς.
plt.figure(figsize=(10, 5))
plt.plot(data['T'])
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.title("Temperature Timeseries 2021")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig('./figures/timeseries.png')
plt.show()


# 3. Θα υπολογίζει και θα εκτυπώνει τη μέση τιμή και την τυπική απόκλιση της χρονοσειράς.
mean = np.mean(data['T'])
std = np.std(data['T'], ddof=1)  # ddof=1 για το δείγμα
print(f"The mean temperature is {mean:.2f} °C and the standard deviation is {std:.2f} °C")


# 4. Θα υπολογίζει το διάστημα εμπιστοσύνης 95% χρησιμοποιώντας το κατάλληλο στατιστικό.
n = len(data['T'])
confidence = 0.95
stderr = std / np.sqrt(n)
t_critical = stats.t.ppf((1 + confidence) / 2, df=n-1)

margin_of_error = t_critical * stderr
ci_lower = mean - margin_of_error
ci_upper = mean + margin_of_error

print(f"95% confidence interval for the mean: [{ci_lower:.2f} °C, {ci_upper:.2f} °C]")


# 5. Θα υπολογίζει το διάστημα εμπιστοσύνης 95% με μέθοδο Monte Carlo 
# δέκα χιλιάδων (10.000) επαναδειγματοληψιών με επανατοποθέτηση.
bootstrap_means = []
T_values = data['T'].dropna().values
n = len(T_values)

for _ in range(10000):
    resample = np.random.choice(T_values, size=n, replace=True)
    resample_mean = np.mean(resample)
    bootstrap_means.append(resample_mean)

lower_bound = np.percentile(bootstrap_means, 2.5)
upper_bound = np.percentile(bootstrap_means, 97.5)

print(f"95% Confidence Interval for the true mean temperature: ({lower_bound:.2f}, {upper_bound:.2f}) °C")


# 6. Θα συγκρίνει τα δύο διαστήματα εμπιστοσύνης.
print(f"Parametric CI (Student t): [{ci_lower:.2f}, {ci_upper:.2f}] °C")
print(f"Bootstrap CI:              [{lower_bound:.2f}, {upper_bound:.2f}] °C")

print(f"lower bound difference is equal to {ci_lower-lower_bound} °C")
print(f"upper bound difference is equal to {ci_upper-upper_bound} °C")

'''
We notice that both CIs are small and contain the mean value
There's a slight difference in the upper and lower bound, 
which may be due to deviation from normality or outliers.
The bootstrap interval is more flexible and safe when the distribution of the data 
is not known or is not normal.
'''

# 7. Θα δημιουργεί ιστόγραμμα των μέσων τιμών που υπολογίζονται σε κάθε επαναδειγματοληψία. 
# Στο γράφημα αυτό θα εμφανίζονται επίσης η πραγματική μέση τιμή, 
# καθώς και τα διαστήματα εμπιστοσύνης.
plt.figure(figsize=(10, 5))
plt.hist(bootstrap_means, bins=50, color='skyblue', edgecolor='black', alpha=0.7)

# real mean value
plt.axvline(mean, color='blue', linestyle='-', linewidth=2, label='Sample Mean')

# parametric CI (student t)
plt.axvline(ci_lower, color='red', linestyle='--', linewidth=2, label='Parametric CI Lower')
plt.axvline(ci_upper, color='red', linestyle='--', linewidth=2, label='Parametric CI Upper')

# bootstrap CI
plt.axvline(lower_bound, color='green', linestyle='-.', linewidth=2, label='Bootstrap CI Lower')
plt.axvline(upper_bound, color='green', linestyle='-.', linewidth=2, label='Bootstrap CI Upper')

plt.title("Histogram of Bootstrap Sample Means with Confidence Intervals")
plt.xlabel("Mean Temperature (°C)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('./figures/bootstrap_histogram_with_CIs.png')
plt.show()