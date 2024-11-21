import pandas as pd

df = pd.read_csv("atmosphere.csv")
df.head()
print(df['H(km)'].head()) 

press = {"H(km)" : df['H(km)'], "P(hPa)": df['P(hPa)']}
pressure = pd.DataFrame(data=press)
pressure = pressure.set_index('H(km)')
pressure.head()

dens = {"H(km)" : df['H(km)'], "P(hPa)": df['r(kg/m^3)']}
density = pd.DataFrame(data=dens)
density = density.set_index('H(km)')
density.head()


pressure.to_csv("pressure.csv", sep=";")
density.to_csv("density.csv", sep=";")
