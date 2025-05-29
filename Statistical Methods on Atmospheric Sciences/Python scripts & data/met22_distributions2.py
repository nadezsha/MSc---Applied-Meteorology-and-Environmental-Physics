import scipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# Example 4.1 Calculate the probability of the lake freezing exactly once in 10 years
scipy.stats.binom.pmf(1, 10, 0.045)

# Example 4.2 Calculate the probability of the lake freezing at least once in 10 years
1-scipy.stats.binom.pmf(0, 10, 0.045)

# Geometric distribution
scipy.stats.geom.pmf(10, 0.05)
scipy.stats.geom.pmf(100, 0.05)
scipy.stats.geom.cdf(4, 0.2)

# Negative binomial distribution
# Calculate the probability of the lake freezing three times for a period of 10 and 100 years
scipy.stats.nbinom.pmf(10, 3, 0.045)
scipy.stats.nbinom.pmf(100, 3, 0.045)

# Poisson distribution
scipy.stats.poisson.pmf(3, 4.6)
scipy.stats.poisson.cdf(5, 4.6)

# Wilks Example 4.6
scipy.stats.norm.cdf(21.4, loc=22.2, scale=4.4)
scipy.stats.norm.cdf(-0.18, loc=0, scale=1)

scipy.stats.norm.cdf(0.6364, loc=0, scale=1) - scipy.stats.norm.cdf(-0.5, loc=0, scale=1)
scipy.stats.norm.cdf(25, loc=22.2, scale=4.4) - scipy.stats.norm.cdf(20, loc=22.2, scale=4.4)

# Central limit theorem example
# Set random seed for reproducibility
np.random.seed(42)

# Generate an exponential population
population = scipy.stats.expon.rvs(scale=2, size=100000)

# Function to demonstrate CLT by taking multiple samples and computing their means
def demonstrate_clt(sample_size, num_samples=1000):
    sample_means = [np.mean(np.random.choice(population, size=sample_size, replace=True)) 
                    for _ in range(num_samples)]
    
    # Plot histogram of sample means
    sns.histplot(sample_means, bins=30, kde=True)
    plt.axvline(np.mean(population), color='red', linestyle='dashed', label="True Mean")
    plt.title(f"Sampling Distribution of Sample Means (n={sample_size})")
    plt.xlabel("Sample Mean")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

# Plotting for different sample sizes
for n in [5, 20, 50, 100]:
    demonstrate_clt(sample_size=n)

# Student's t distribution
scipy.stats.t.cdf(1,6,1,2)-scipy.stats.t.cdf(0,6,1,2)
scipy.stats.t.cdf(0.,6,0,1)-scipy.stats.t.cdf(-.5,6,0,1)

# Gamma distribution
scipy.stats.gamma.cdf(3.15, a=3.76,scale=0.52)

# Weibul distribution

k = 2  # shape parameter
lambda_ = 5  # scale parameter
x = 8  # value to find the probability of

prob = scipy.stats.weibull_min.cdf(x, k, scale=lambda_)
f"Probability that X <=  {x}: {prob:.4f}."

# https://towardsdatascience.com/understand-q-q-plot-using-simple-python-4f83d5b89f8f

from numpy.random import seed
from numpy.random import normal
from numpy.random import binomial

#make this example reproducible
seed(1)

#generate sample of 200 values that follow a normal distribution 
normalised_data = normal(loc=0, scale=1, size=120000)

plt.hist(normalised_data)
plt.show()

sm.qqplot(normalised_data, line ='45')
plt.show()

binomial_data = binomial(n=10, p=0.045, size=1200)

plt.hist(binomial_data)
plt.show()

sm.qqplot(binomial_data, line ='45')
plt.show()

sm.qqplot(binomial_data, scipy.stats.binom(10, 0.045), line ='45')
plt.show()

df = pd.read_csv("Hellenicon_data.csv", index_col=0, parse_dates=True, sep=';')

plt.hist(df['Tmax'])
plt.show()

sm.qqplot(df['Tmax'], line ='45')
plt.show()

sm.qqplot(df['Tmin'], line ='45')
plt.show()

plt.hist(df['r'])
plt.show()

sm.qqplot(df['r'], line ='45')
plt.show()

Ithaka = pd.read_csv("SMAS_Ithaka_Jan1987.csv", index_col=0, parse_dates=True, sep=',')

plt.hist(Ithaka['Precip_Ith'])
plt.show()

sm.qqplot(Ithaka['Precip_Ith'], line ='45')
plt.show()