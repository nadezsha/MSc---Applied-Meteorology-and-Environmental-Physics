from scipy.stats import norm
import pandas as pd

Ithaka = pd.read_csv("SMAS_Ithaka_Jan1987.csv", index_col=0, parse_dates=True, sep=',')

# Υπολογισμός μέσης τιμής και τυπικής απόκλισης
mean_tmin_ith = Ithaka['MinTem_Ith'].mean()
std_tmin_ith = Ithaka['MinTem_Ith'].std()

mean_tmin_can = Ithaka['MinTem_Can'].mean()
std_tmin_can = Ithaka['MinTem_Can'].std()

# Υπολογισμός πιθανότητας Tmin > 38
prob_min_ith = 1 - norm.cdf(38, loc=mean_tmin_ith, scale=std_tmin_ith)
prob_min_can = 1 - norm.cdf(38, loc=mean_tmin_can, scale=std_tmin_can)

print(f"Πιθανότητα Tmin > 38°F (Ith): {prob_min_ith:.3f} ή {prob_min_ith*100:.3f}%")
print(f"Πιθανότητα Tmin > 38°F (Can): {prob_min_can:.3f} ή {prob_min_can*100:.3f}%")

# Υπολογισμός μέσης τιμής και τυπικής απόκλισης
mean_tmax_ith = Ithaka['MaxTem_Ith'].mean()
std_tmax_ith = Ithaka['MaxTem_Ith'].std()

mean_tmax_can = Ithaka['MaxTem_Can'].mean()
std_tmax_can = Ithaka['MaxTem_Can'].std()

# Υπολογισμός πιθανότητας Tmax > 38
prob_max_ith = 1 - norm.cdf(38, loc=mean_tmax_ith, scale=std_tmax_ith)
prob_max_can = 1 - norm.cdf(38, loc=mean_tmax_can, scale=std_tmax_can)

print(f"Πιθανότητα Tmax > 38°F (Ith): {prob_max_ith:.3f} ή {prob_max_ith*100:.3f}%")
print(f"Πιθανότητα Tmax > 38°F (Can): {prob_max_can:.3f} ή {prob_max_can*100:.3f}%")
