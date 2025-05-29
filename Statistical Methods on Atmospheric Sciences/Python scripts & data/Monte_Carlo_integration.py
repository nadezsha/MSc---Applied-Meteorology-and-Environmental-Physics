#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  1 03:32:18 2018

@author: thanos
"""
""" 
Example of Monte Carlo integration of exp(x) within [0,1)
"""
import numpy as np
import matplotlib.pyplot as plt

# Plots the function between 0 and 1 with a step of 0.01
x = np.linspace(0, 1, 100) 
plt.plot(x, np.exp(x))

# How to randomly select points within the desired area
pts = np.random.uniform(0,1,(100, 2)) # Draws 100 random pairs from the uniform distribution within the range [0,1)]
pts[:, 1] *= np.e # Multiplies the second column with e 
plt.scatter(pts[:, 0], pts[:, 1])
plt.xlim([0,1])
plt.ylim([0, np.e])
plt.show()

# Monte Carlo approximation
a = 0 #lower integration limit
b = 1 #upper integration limit
x1=np.zeros(8)
y1=np.zeros(8)
i=0
for n in 10**np.array([1,2,3,4,5,6,7,8]): # n: number of iterations
    pts = np.random.uniform(0, 1, (n, 2))
    pts[:, 1] *= np.exp(b)
    count = np.sum(pts[:, 1] < np.exp(pts[:, 0])) # Counts the number of points below the graph line
    area = np.e * (b-a) # area of region
    sol = area * count/n # Solution of the integral
    print ('%10d %.6f' % (n, sol))
    x1[i]=n
    y1[i]=sol
    i +=1

# Graph showing the evolution of the solution as a function of the number of iterations     
plt.scatter(np.log(x1),y1)
plt.show()