#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  1 05:08:58 2018

@author: A. Argiriou

"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
import numpy as np
import time

start_time = time.time()

# Function to be fit on data
def f_co2(x,a,b):
    return a*np.exp(b*x)

# Reads annual CO_2 data
data = pd.read_csv('MaunaLoa_2017.txt', header = 0, delimiter=';')
plt.plot(data['year'],data['co2'],'ro')
plt.xlabel('Year')
plt.ylabel('[CO_2] ppm/year')
plt.show()

# Initial guess of the parameters
vGuess = [0.06,0.004]

# Curve fitting on experimental data, vPars: fitted parameters, 
# aCova: covariance of fitted parameters
vPars, aCova = optimize.curve_fit(f_co2, data['year'], data['co2'], p0=vGuess)

# Standard error of fitted parameters
std_vPars = np.sqrt(np.diag(aCova))
print(std_vPars)
plt.figure()
line1, = plt.plot(data['year'],data['co2'],'ro', label='$measured$')
line2, =plt.plot(data['year'],f_co2(data['year'], vPars[0],vPars[1]), 'b-',label='$estimated$')
plt.xlabel('Year')
plt.ylabel('[CO_2] ppm/year')
plt.legend(loc='upper left')
plt.show()

# But the standard error of the [CO_2] is +/- 0.12
yerror = 0.12
nTrials = 4000
aFitPars = np.array([])

for iTrial in range(nTrials):
    yTrial = data['co2'] + np.random.normal(loc=0.,scale=yerror,size=np.size(data['co2']))
    
    # We use a try/except clause to catch pathologies
    try:
        vTrial, aCova = optimize.curve_fit(f_co2,data['year'],yTrial,p0=vGuess)
    except:
        dumdum=1
        continue  # This moves us to the next loop without stacking.

#here follows the syntax for stacking the trial onto the running sample:
    if np.size(aFitPars) < 1:
        aFitPars=np.copy(vTrial)
    else:
        aFitPars = np.vstack(( aFitPars, vTrial ))
        
np.shape(aFitPars)
print (np.median(aFitPars[:,0]))
print (np.std(aFitPars[:,0]))
print (np.median(aFitPars[:,1]))
print (np.std(aFitPars[:,1]))

print('Duration:  ', time.time() - start_time)