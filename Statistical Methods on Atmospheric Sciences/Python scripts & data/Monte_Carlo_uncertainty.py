#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  1 05:08:58 2018

@author: A. Argiriou
"""

import numpy as np
from scipy import optimize
import pylab as P
import matplotlib.pyplot as plt

# Function to be fit on data
def f_decay(x,a,b):
    return a*x**(b)

# Experimental data generation
xMeas = np.random.uniform(0.5,3.0,size=6)
yTrue = 1.5/xMeas
sError = 0.1
yMeas = yTrue + np.random.normal(scale=sError, size=np.size(yTrue))
plt.scatter(xMeas, yMeas)
plt.show()

P.errorbar(xMeas,yMeas,yerr=sError,lw=0,elinewidth=1,ecolor='b', fmt='ko',markersize=2)
P.xlabel('"Time"')
P.ylabel('Measured value')
P.xlim(0.4,3.0)
P.show()

# Initial guess of the parameters
vGuess = [2.0,-2.0]

# Curve fitting on experimental data, vPars: fitted parameters, 
# aCova: covariance of fitted parameters
vPars, aCova = optimize.curve_fit(f_decay, xMeas, yMeas, vGuess)

# Standard error of fitted parameters
std_vPars = np.sqrt(np.diag(aCova))
print(std_vPars)

# Plot of fitted curve
xFine = np.linspace(0.4,3.0,100)
P.errorbar(xMeas,yMeas,yerr=sError,lw=0,elinewidth=1,ecolor='b', fmt='ko',markersize=2)
P.plot(xFine, f_decay(xFine,*vPars), 'g-', lw=1) # Fitted parameters
P.plot(xFine, f_decay(xFine,1.5,-1.0), 'r--', lw=1) # Parameters used to generate data
P.title('Fitted curve (green) and "true" curve (red dashed)')
P.show()

# The above errors include only fitting errors and not data errors
# Calculation of overall uncertainty using Monte Carlo simulations
nTrials = 4000
aFitPars = np.array([])

for iTrial in range(nTrials):
    xTrial = np.random.uniform(0.5,3.0,size=np.size(xMeas))
    yGen = 1.5/xTrial
    yTrial = yGen + np.random.normal(scale=sError,size=np.size(yGen))
    
    # We use a try/except clause to catch pathologies
    try:
        vTrial, aCova = optimize.curve_fit(f_decay,xTrial,yTrial,vGuess)
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