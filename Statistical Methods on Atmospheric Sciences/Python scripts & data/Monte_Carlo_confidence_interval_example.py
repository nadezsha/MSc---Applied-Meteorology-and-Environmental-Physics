'''Έχουμε ιστορικά δεδομένα 30 ετών της μέσης θερμοκρασίας (°C) του Ιουλίου. Θέλουμε να υπολογίσουμε το διάστημα εμπιστοσύνης 95% της πραγματικής
μέσης θερμοκρασίας με προσομοίωση Carlo simulation (bootstrap). Προσομοιώνουμε τα 30 έτη θερμοκρασιών, θεωρώντας ότι αυτές κυμαίνονται περί τους 27 °C.'''

import numpy as np
np.random.seed(42)

# Προσομοίωση 30 ετών μέσης μηνιαίας θερμοκρασίας (°C) Ιουλίου 
july_temps = np.random.normal(loc=27, scale=1.5, size=30)

# Υπολογισμός του διαστήματος εμπιστοσύνης με τη μέθοδο t-Student
from scipy import stats


mean = np.mean(july_temps)
std = np.std(july_temps, ddof=1)  # use ddof=1 for sample std
n = len(july_temps)

alpha = 0.05
t_crit = stats.t.ppf(1 - alpha/2, df=n - 1)

margin_of_error = t_crit * (std / np.sqrt(n))
lower_boundt = mean - margin_of_error
upper_boundt = mean + margin_of_error

print(f"95% Confidence Interval using t-Student method: ({lower_boundt:.2f}, {upper_boundt:.2f}) °C")

# Μέθοδος Monte Carlo: Επαναδειγματοληψία με αντικατάσταση από τις 30 τιμές 10 000 φορές και υπολογισμός, κάθε φορά της μέσης θερμοκρασίας.

bootstrap_means = []

for _ in range(10000):
    resample = np.random.choice(july_temps, size=30, replace=True)
    resample_mean = np.mean(resample)
    bootstrap_means.append(resample_mean)

# Υπολογισμός του 95% διαστήματος εμπιστοσύνης
lower_bound = np.percentile(bootstrap_means, 2.5)
upper_bound = np.percentile(bootstrap_means, 97.5)

print(f"95% Confidence Interval for the true mean temperature: ({lower_bound:.2f}, {upper_bound:.2f}) °C")

