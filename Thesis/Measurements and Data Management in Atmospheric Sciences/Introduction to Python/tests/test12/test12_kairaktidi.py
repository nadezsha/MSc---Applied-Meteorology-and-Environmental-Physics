import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt


# TASK a) creates a dataframe with columns the two isotopic  
# concentrations (of deuterium and oxygen - 18) 
# that are included in the file with a timestamp index
columns =  ['Date', 'O18', 'H2']
df = pd.read_csv('isotopes.csv', sep=',', index_col=[0], parse_dates=True,
                  usecols=columns,)
df = df.dropna()
print(df.head())

# TASK b) calculates the topic meteorological line of Athens.
Y = df["H2"]
X = sm.add_constant(df["O18"])
model = sm.OLS(Y, X) 
results = model.fit()
print(results.summary())
print(results.params)
print(results.pvalues)

Y_hat = X*results.params[0]

# TASK c) creates a graph of the spots and the topic meteorological line. 
# The graph should be of publication-like quality and on it there should be printed
# the equation and its parameters as a result of this code

plt.scatter(df["O18"], df["H2"], color ='b')
plt.plot(X, Y_hat, "r")
plt.text(-13, 2, f'$\delta$H2 = {results.params.O18: .2f} $\delta$O18 + {results.params.const: .1f}', 
         color='r')
plt.xlabel("$\delta^{18}$O(‰)")
plt.ylabel("$\delta^2$ H(‰)")
plt.title("topic meterological line for Athens")
plt.grid()
plt.savefig('Linear_regression_graph_test12')
plt.show()


# TASK d) creates a file with the detailed results of the line's model
with open("regression_results.txt", "w") as f:
    f.write(results.summary().as_text())

resid_model = df["H2"] - results.predict(X)
print(f'Model with constant term mean residual value = {resid_model.mean():.3f}')


# TASK e) according to the results, write your comments and evaluate the model
'''
Model Evaluation Comments:
1. The regression equation is: δH2 = 6.99 * δO18 + 6.00
2. The slope determines how δO18 relates to δH2 and it's equal to 5.97.
3. The R² value indicates how well δO18 predicts δH2. The R² for this specific dataset
    is equal to 0.905 so it's excellent.
4. The p-value is equal to 0.000 so the predictor is statistically significant.
5. Residual mean is equal to to -0.000.
6. All in all, the model seems to provide a good prediction of the isotops' concentration.
'''

# TASK f) create boxplots of the two isotops' concentrations
# after evaluating whether it's correct to put them both
# on the same boxplot or in different ones 

# different boxplots because there's a big difference on the y axis values!

plt.boxplot(df['H2'])
plt.title('H2 concentration boxplot')
plt.xlabel('model/dependent variable')
plt.ylabel('$\delta^2$ H(‰)')
plt.grid(True)
plt.show()

plt.boxplot(df['O18'])
plt.title('O18 concentration boxplot')
plt.xlabel('independent variable')
plt.ylabel('$\delta^{18}$ O(‰)')
plt.grid(True)
plt.show()
