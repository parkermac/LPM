"""
Code to plot time series for the aiN mooring extraction.  Starting with
vertically-integrated buoyancy flux.
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import seawater as sw

from lo_tools import Lfun
Ldir = Lfun.Lstart()

fn = Ldir['LOo'] / 'extract' / 'ai0_v0_n0k' / 'moor' / 'aiN_2018.01.01_2018.01.14.nc'
#fn = Ldir['LOo'] / 'extract' / 'cas6_v3_lo8b' / 'moor' / 'Admiralty_2020.01.01_2021.12.31.nc'

ds = xr.open_dataset(fn)

# time
ot = ds.ocean_time.values
ot_dt = pd.to_datetime(ot)
t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
T = t/86400 # time in days from start

zeta = ds.zeta.values

# calculate potential density
rho = sw.dens0(ds.salt.values, ds.temp.values)

# calculate vertically-integrated buoyancy flux
Fb = -9.8 * np.sum( ds.AKs[:,1:-1] * np.diff(rho, axis=1), axis=1).values
Fb[Fb<=.001] = .001

# calculate along-channel velocity

def rot_vec(u,v,theta):
    ur = u*np.cos(theta) + v*np.sin(theta)
    vr = v*np.cos(theta) - u*np.sin(theta)
    return ur, vr
    
def de_mean(u, v):
    up = u - np.nanmean(u)
    vp = v - np.nanmean(v)
    return up, vp

ubar = ds.ubar.values
vbar = ds.vbar.values

# find angle of principal axes
up, vp = de_mean(ubar, vbar)
theta = 0.5 * np.arctan2(2*np.nanmean(up*vp),(np.nanvar(up)-np.nanvar(vp)))

# and rotate
ubar_r, vbar_r = rot_vec(ubar, vbar, theta)
u_r, v_r = rot_vec(ubar,vbar,theta)

# PLOTTING

plt.close('all')

# Time series

fig = plt.figure(figsize=(12,7))
N = 3 # number of rows

ax = fig.add_subplot(N,1,1)
ax.plot(T, zeta)

ax = fig.add_subplot(N,1,2)
ax.plot(T, u_r, '-r', label='u_r')
ax.plot(T, v_r, '-b', label='v_r')
ax.legend()

ax = fig.add_subplot(N,1,3)
ax.plot(T, Fb)

# Scatter plot

fig = plt.figure(figsize=(10,10))

ax = fig.add_subplot(111)
ax.scatter(u_r, zeta, s=800*Fb, c=Fb, marker='o', cmap='YlOrRd', edgecolors='k')
ax.set_xlim(-3.5, 3.5)
ax.set_ylim(-2.5, 2.5)
ax.grid(True)
ax.set_xlabel('Ubar: Flood Positive [m/s]')
ax.set_ylabel('SSH [m]')
ax.axhline()
ax.axvline()


plt.show()