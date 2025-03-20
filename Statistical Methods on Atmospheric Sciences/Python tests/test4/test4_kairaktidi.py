import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

''''
1) Αν σε ένα θηκόγραμμα, οι τιμές των άνω (q0,75) και κάτω (q0,25) τεταρτημορίων
είναι συμμετρικές ως προς την τιμή της διαμέσου, τι συμπεραίνετε ως προς την συνάρ-
τηση κατανομής των δεδομένων;

Αν οι τιμές των άνω (q0,75) και κάτω (q0,25) τεταρτημορίων είναι συμμετρικές
ως προς την τιμή της διαμέσου, δηλαδή η απόστασή τους είναι ίση από την διάμεσο,
αυτό υποδεικνύει ότι η κατανομή των δεδομένων είναι συμμετρική ως προς τη διάμεσο.
'''

# TASK 2) Χρησιμοποιώντας τα δεδομένα της μέγιστης ημερήσιας θερμοκρασίας του Ελληνικού,
# υπολογίστε το ποσοστό των θερμοκρασιών οι οποίες 
# α) υπερβαίνουν τους 20 ◦C και 

# reading the data
data = pd.read_csv('Hellenicon_data.csv', sep=';', usecols=[0, 2, 3], index_col=0, parse_dates=True).dropna()
max_temp = data['Tmax']  

# calculating the percentage of days with max temp > 20°C
above_20 = (max_temp > 20).sum()
total_days = len(max_temp)
percentage_above_20 = (above_20 / total_days) * 100
print(f"Percentage of days with max temperature > 20°C: {percentage_above_20:.2f}%")

# computing empirical cummulative distribution function
x = np.sort(max_temp)
y = np.arange(1, len(x) + 1) / len(x)

# plotting ECDF
plt.figure(figsize=(8, 5))
plt.plot(x, y, marker='.', linestyle='none', label='ECDF')
plt.axvline(x=20, color='red', linestyle='dashed', linewidth=2, label='20°C threshold')
plt.xlabel('Maximum Daily Temperature (°C)')
plt.ylabel('Cummulative Probability')
plt.title('Empirical Cumulative Distribution Function (ECDF)')
plt.legend()
plt.grid(True)
plt.show()


# β) βρίσκονται στο εύρος από 25 έως 35 ◦C.

# again, calculating the percentage
total_days = len(max_temp)
within_range = ((max_temp >= 25) & (max_temp <= 35)).sum()
percentage_within_range = (within_range / total_days) * 100
print(f"Percentage of days with max temperature between 25°C and 35°C: {percentage_within_range:.2f}%")

# plotting ECDF with the new region
plt.figure(figsize=(8, 5))
plt.plot(x, y, marker='.', linestyle='none', label='ECDF')
plt.fill_between(x, y, where=(x >= 25) & (x <= 35), color='gray', alpha=0.3, label='25°C - 35°C')
plt.axvline(x=25, color='green', linestyle='dashed', linewidth=2, label='25°C threshold')
plt.axvline(x=35, color='green', linestyle='dashed', linewidth=2, label='35°C threshold')
plt.xlabel('Maximum Daily Temperature (°C)')
plt.ylabel('Cummulative Probability')
plt.title('Empirical Cumulative Distribution Function (ECDF) (with Temp Range 25°C - 35°C highlighted)')
plt.legend()
plt.grid(True)
plt.show()