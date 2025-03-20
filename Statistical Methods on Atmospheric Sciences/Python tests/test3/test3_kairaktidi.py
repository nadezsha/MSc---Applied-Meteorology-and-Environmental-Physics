import statistics
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# EXERCISE 1
# task a) Θα υπολογίζετε και θα εκτυπώνετε τα βασικά ποσοστημόρια
data = [33.19, 29.88, 24.4, 24.77, 30.53, 33.23, 26.06, 34.12, 30.45, 29.04, 38.8,
         40.34, 38.03, 27.28, 25.35, 29.81, 29.57, 39.63, 29.06, 39.95, 22.57, 
         34.26, 32.17, 38.43, 37.05, 42.4, 35.98, 32.71, 33.28, 49.54, 27.71, 34.98, 
         45.03, 35.97, 36.39, 25.77, 27.98, 35.01, 38.72, 32.79, 33.77, 26.38, 37.15, 
         30.5, 38.56, 28.47, 32.08, 10.0, 12.0, 14.0]
quantiles = statistics.quantiles(data)
print(quantiles)

# task b) Θα υπολογίζετε και θα εκτυπώνετε το ενδοποσοστημοριακό εύρος.
IQR = quantiles[2]-quantiles[0]
print("Interquartile Range (IQR):", IQR)

# task c) Θα διερευνάτε την ύπαρξη και θα εκτυπώνετε παράτυπες τιμές.
lower_bound = quantiles[0] - 1.5*IQR
upper_bound = quantiles[2] + 1.5*IQR
outliers = [x for x in data if x < lower_bound or x > upper_bound]
print("Outliers in data:", outliers)

#task d) Θα υπολογίζετε και θα εκτυπώνετε τον συντελεστή και το είδος της ασυμμετρίας.
skew_value = stats.skew(data)
print(f"Skewness: {skew_value:.4f}")
print("Negative skew, meaning the distribution has a long left tail (more extreme low values).")

# task e) Θα υπολογίζετε και θα εκτυπώνετε τον συντελεστή και το είδος της κυρτότητας.
kurtosis_value = stats.kurtosis(data)
print(f"Kurtosis: {kurtosis_value:.4f}")
print("Kurtosis is less than 3 meaning that the distribution is platykurtic (flatter and lighter tails)")



# EXERCISE 2
Ithaka = pd.read_csv('SMAS_Ithaka_Jan1987.csv', sep=',', usecols=[0, 2, 3], index_col=0, parse_dates=True).dropna()
print(Ithaka)

# task a) Σχεδιάστε τα αντίστοιχα θηκογράμματα.
plt.boxplot([Ithaka.MaxTem_Ith, Ithaka.MinTem_Ith], labels=["Max Temperature", "Min Temperature"])
plt.title("Boxplots of Max and Min Temperatures in Ithaka (Jan 1987)")
plt.ylabel("Temperature (°C)")
plt.show()

# task b) Διερευνήστε αν υπάρχουν ενδεχόμενες παράτυπες τιμές σε κάποια ή και στις δύο χρονοσειρές και εκτυπώστε τες.
print("From the boxplot we can see that only the Max column has outliers but this can be also applied to the min column as well")
quantiles_Ith = statistics.quantiles(Ithaka.MaxTem_Ith, n=4) 
IQR_Ith = quantiles_Ith[2] - quantiles_Ith[0]  
lower_bound_Ith = quantiles_Ith[0] - 1.5 * IQR_Ith
upper_bound_Ith = quantiles_Ith[2] + 1.5 * IQR_Ith
outliers = Ithaka.MaxTem_Ith[(Ithaka.MaxTem_Ith < lower_bound_Ith) | (Ithaka.MaxTem_Ith > upper_bound_Ith)]
print("Outliers in MaxTem_Ith:")
print(outliers)

# task c) γ) Υπολογίστε και εκτυπώστε τους συντελεστές ασυμμετρίας και κυρτότητας.
skew_max = stats.skew(Ithaka.MaxTem_Ith)
kurtosis_max = stats.kurtosis(Ithaka.MaxTem_Ith)
skew_min = stats.skew(Ithaka.MinTem_Ith)
kurtosis_min = stats.kurtosis(Ithaka.MinTem_Ith)
print("Skewness and Kurtosis for Ithaka Temperatures:")
print(f"Max Temperature - Skewness: {skew_max:.4f}, Kurtosis: {kurtosis_max:.4f}")
print(f"Min Temperature - Skewness: {skew_min:.4f}, Kurtosis: {kurtosis_min:.4f}")

# task d) Σχεδιάστε την συνάρτηση αθροιστικής κατανομής και μέσω αυτής εκτιμήστε το ποσοστό των θερμοκρασιών που είναι μικρότερες των 30 °F.
T_cumfreq = stats.cumfreq(Ithaka.MaxTem_Ith, numbins=50) 
x = T_cumfreq.lowerlimit + np.linspace(0, T_cumfreq.binsize * T_cumfreq.cumcount.size, 
                                       T_cumfreq.cumcount.size)
plt.bar(x, T_cumfreq.cumcount, width=T_cumfreq.binsize, alpha=0.7, color='b', label='CDF')
plt.axvline(30, color='r', linestyle='--', label='30°F Threshold')  
plt.ylabel("Cumulative Count")
plt.title("Cumulative Distribution Function (CDF) of Max Temperature in Ithaka")
plt.legend()
plt.show()

total_count = T_cumfreq.cumcount[-1]
below_30_count = T_cumfreq.cumcount[np.searchsorted(x, 30)]  
percentage_below_30 = (below_30_count / total_count) * 100
print(f"Percentage of temperatures below 30°F: {percentage_below_30:.2f}%")

# for the min :
T_cumfreq2 = stats.cumfreq(Ithaka.MinTem_Ith, numbins=50) 
x = T_cumfreq2.lowerlimit + np.linspace(0, T_cumfreq2.binsize * T_cumfreq2.cumcount.size, 
                                       T_cumfreq2.cumcount.size)
plt.bar(x, T_cumfreq2.cumcount, width=T_cumfreq2.binsize, alpha=0.7, color='b', label='CDF')
plt.axvline(30, color='r', linestyle='--', label='30°F Threshold')  
plt.ylabel("Cumulative Count")
plt.title("Cumulative Distribution Function (CDF) of Min Temperature in Ithaka")
plt.legend()
plt.show()

total_count = T_cumfreq2.cumcount[-1]
if 30 < x[0] or 30 > x[-1]:
    print("30°F is out of the range of the data.")
else:
    below_30_count = T_cumfreq.cumcount[np.searchsorted(x, 30)] 
    percentage_below_30 = (below_30_count / total_count) * 100
    print(f"Percentage of temperatures below 30°F: {percentage_below_30:.2f}%")