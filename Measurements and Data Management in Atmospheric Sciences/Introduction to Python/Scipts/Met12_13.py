import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt

# Summary of Linear Regression
df = pd.read_csv('Adrar_2015.txt', sep=' ', usecols=("GHIsat", "GHIstation"))
#df = df.apply(lambda x: pd.Series(x.dropna().values))
df = df.dropna()
df.head()

# Independent variable: GHIsat, Dependent variable: GHIstation, No constant
Y = df["GHIstation"]
X = df["GHIsat"]
model1 = sm.OLS(Y, X) # Definition of the model
results1 = model1.fit() # Calculation of the model parameters
print(results1.summary())
print(results1.params)
print(results1.pvalues)

Y1_hat = X*results1.params[0]

plt.scatter(df["GHIsat"], df["GHIstation"])
plt.plot(X, Y1_hat, "r")
plt.text(1.2, 8.5, f'GHI ground = {results1.params.GHIsat: .2f} GHI satellite', color='r')
plt.xlabel("GHI satellite ($kWh/m^2$)")
plt.ylabel("GHI ground ($kWh/m^2$)")
plt.savefig('Linear_regression_without_constant')
plt.show()

# Independent variable:GHIsat, Dependent variable: GHIstation with constant
Y = df["GHIstation"]
X1 = sm.add_constant(df["GHIsat"])
model2 = sm.OLS(Y, X1)
results2 = model2.fit()
print(results2.summary())
print(results2.params)
print(results2.pvalues)

Y2_hat = X*results2.params[1]+results2.params[0]

plt.scatter(df["GHIsat"], df["GHIstation"])
plt.plot(X, Y2_hat, "r")
plt.text(1.2, 7, f'GHI ground = {results2.params.GHIsat: .2f} GHI satellite + {results2.params.const: .1f}', 
         color='r')
plt.xlabel("GHI satellite ($kWh/m^2$)")
plt.ylabel("GHI ground ($kWh/m^2$)")
plt.savefig('Linear_regression_with_constant')
plt.show()

# Calculation of residuals
resid_model1 = df["GHIstation"] - Y1_hat
resid_model2 = df["GHIstation"] - Y2_hat
print(f'Model without constant term mean residual value = {resid_model1.mean(): .3f}')
print(f'Model with constant term mean residual value = {resid_model2.mean(): .3f}')

residuals = pd.concat([resid_model1, resid_model2], axis=1)
plt.boxplot(residuals)
plt.title('Linear regression residuals boxplots')
plt.xlabel('Model')
plt.ylabel('GHI [$kWh.m^{-2}$]')
plt.xticks([1, 2], ['No intercept', 'With intercept'])
plt.grid(True)
plt.show()

plt.hist(resid_model1, 100)
plt.title('Residuals histogram - No intercept')
plt.xlabel('Residuals (K)')
plt.savefig('hist1')
plt.show()

plt.hist(resid_model2, 100)
plt.title('Residuals histogram - With intercept')
plt.xlabel('Residuals (K)')
plt.savefig('hist2')
plt.show()