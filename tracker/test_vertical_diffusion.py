"""
Code to test the vertical diffusion in tracker, paying special
attention to the top and bottom boundaries and possible interaction
with the nearest neighbor method.
"""

from scipy.interpolate import interp1d
from time import time
import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

NP = 100
NT = 1000

H = 100
zw = np.linspace(-H,0,101)
zr = zw[:-1] + np.diff(zw)/2

k_shape = 4*(-zw)*(H+zw)/(H*H) # shape of k(z) with max = 1, and 0 at ends
#k_shape = np.ones(zw.shape)

k = 0.01 * k_shape # on zw
k[0] = k[1]
k[-1] = k[-2]

dkdz = np.zeros(k.shape)
dkdz[1:-1] = (k[2:]-k[:-2])/(zw[2]-zw[0])
# dkdz = np.diff(k) / np.diff(zw)  # on zr

fk = interp1d(zw, k, kind='nearest')
fdk = interp1d(zw, dkdz, kind='nearest')


# initial condition
p = np.linspace(-H,0,NP)

# array to save results
P = np.nan * np.ones((NP,NT))

dt = 100

rand = np.random.standard_normal(NP)

for ii in range(NT):
    
    # p[p>zr[-1]] = zr[-1]
    # p[p<zr[0]] = zr[0]
    
    P[:,ii] = p
    
    pk = fk(p)
    pdk = fdk(p)
    
    rand = np.random.standard_normal(NP)
    
    dz = dt * (rand*np.sqrt(2*pk/dt) + pdk)
    
    p = p + dz
    
    # reflective
    hit_top = p > 0
    p[hit_top] = - np.remainder(p[hit_top],H)
    hit_bottom = p < -H
    p[hit_bottom] = -H - np.remainder(p[hit_bottom],-H)
    
    # and finally enforce more limits if needed
    # Pcs[Pcs < -1] = -1
    # Pcs[Pcs > 0] = 0
    
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(14,12))
ax = fig.add_subplot(111)

T = np.linspace(0,NT*dt,NT) * np.ones((NP,NT))
ax.plot(T,P, '.b')

plt.show()
pfun.end_plot()
    


