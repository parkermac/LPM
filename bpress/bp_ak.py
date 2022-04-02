"""
Code to analyze a mooring extraction in relation to processes that affect bottom pressure.

Works with a mooring extraction from Alex Kurapov.
"""

import xarray as xr
import numpy as np
import gsw
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

# set mooring extraction to analyze (just needs salt, temp, and zeta)
Ldir = Lfun.Lstart()

fs = 12
def icb(ax, cs):
    # cbaxes = inset_axes(ax, width="40%", height="4%", loc='upper right', borderpad=2)
    # cb = fig.colorbar(cs, cax=cbaxes, orientation='horizontal')
    ax.fill([.93,.995,.995,.93],[.05,.05,.95,.95],'w', alpha=.5, transform=ax.transAxes)
    cbaxes = inset_axes(ax, width="2%", height="80%", loc='right', borderpad=3) 
    cb = fig.colorbar(cs, cax=cbaxes, orientation='vertical')
    cb.ax.tick_params(labelsize=.85*fs)

plt.close('all')
    
fn = Ldir['LOo'] / 'extract' / 'kurapov' / 'moor' / 'zuvts_rho_lon125lat36_Exp42d.nc'
ds = xr.open_dataset(fn)

# get time axis
ot = ds.ocean_time.values # an array with dtype='datetime64[ns]'
dti = pd.to_datetime(ot) # a pandas DatetimeIndex with dtype='datetime64[ns]'
dt = dti.to_pydatetime() # an array of datetimes

# set constants
pad = 36 # this trims the ends after the low pass so there are no nan's
g = 9.81 # gravity [m s-2]
rho0 = 1025 # reference density [kg m-3]

# pull fields from dataset
Z = ds.z_r.values
h = ds.h.values
zz = Z[:-1] + np.diff(Z)/2
ZW = np.concatenate( (np.array([-h]), zz, np.array([0])) )

eta = ds.zeta.values
salt = ds.salt.values
temp = ds.temp.values
lon = ds.lon.values
lat = ds.lat.values
u = ds.u.values
v = ds.v.values
NT, N = salt.shape

DZ = np.diff(ZW)

# Equation of state calculations
p00 = gsw.p_from_z(Z, lat)
SA = gsw.SA_from_SP(salt, p00, lon, lat) # absolute salinity
CT = gsw.CT_from_pt(SA, temp) # conservative temperature
rho = gsw.rho(SA, CT, p00)

# low pass filtered version
eta = zfun.lowpass(eta, f='godin')[pad:-pad:24]
eta = eta - np.mean(eta) # remove mean SSH
rho = zfun.lowpass(rho, f='godin')[pad:-pad:24, :]
salt = zfun.lowpass(SA, f='godin')[pad:-pad:24, :]
temp = zfun.lowpass(CT, f='godin')[pad:-pad:24, :]
u = zfun.lowpass(u, f='godin')[pad:-pad:24, :]
v = zfun.lowpass(v, f='godin')[pad:-pad:24, :]

# also make associated time vectors
t = dt[pad:-pad:24]
tf = dt[24:-24:24] # "full" version used for pcolormesh plots
    
# calculate the baroclinic pressure
p = np.flip(np.cumsum(np.flip(g * rho * DZ.reshape((1,N)), axis=1), axis=1), axis=1)

# calculate the pressure due to SSH
p0 = g * rho0 *eta

# annual means
Rho = np.mean(rho, axis=0)
Salt = np.mean(salt, axis=0)
Temp = np.mean(temp, axis=0)
P = np.mean(p, axis=0)
U = np.mean(u, axis=0)
V = np.mean(v, axis=0)

# anomalies from the annual mean
salt_a = salt - Salt.reshape((1,N))
temp_a = temp - Temp.reshape((1,N))
rho_a = rho - Rho.reshape((1,N))
p_a = p - P.reshape((1,N))
u_a = u - U.reshape((1,N))
v_a = v - V.reshape((1,N))

# make the full pressure anomaly
p_aa = p_a + p0.reshape((len(t),1))

if True:
    
    # plotting
    plt.close('all')
    pfun.start_plot(fs=fs, figsize=(18,12))

    # pressure
    fig = plt.figure()
    nrow = 3
    #
    ax = fig.add_subplot(nrow,1,1)
    cs = ax.pcolormesh(tf, ZW, p_a.T, cmap='RdYlBu_r', vmin=-500, vmax=500)
    ax.text(.03, .07, 'Low-passed Baroclinic Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
    ax.grid(True)
    icb(ax,cs)
    sn = fn.name.replace('.nc','')
    ax.set_title(sn)
    ax.set_xlim(dt[0],dt[-1])
    ax.set_ylabel('Z [m]')
    #
    ax = fig.add_subplot(nrow,1,2)
    cs = ax.pcolormesh(tf, ZW, p_aa.T, cmap='RdYlBu_r', vmin=-500, vmax=500)
    ax.text(.03, .07, 'Low-passed Full Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
    ax.grid(True)
    icb(ax,cs)
    ax.set_xlim(dt[0],dt[-1])
    ax.set_ylabel('Z [m]')
    #
    ax = fig.add_subplot(nrow,1,3)
    nfilt = 1 # days for Hanning filter
    ax.plot(t, zfun.lowpass(p0, 'hanning', n=nfilt), '-', c='orange', lw=3, label='Due to surface height')
    ax.plot(t, zfun.lowpass(p_a[:,0], 'hanning', n=nfilt), '-', c='cornflowerblue', lw=3, label='Baroclinic only')
    ax.plot(t, zfun.lowpass(p_aa[:,0], 'hanning', n=nfilt), '-r', lw=3, label='Full')
    ax.legend(loc='upper left', ncol=3)
    ax.grid(True)
    ax.text(.03, .07, 'Parts of the Bottom Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
    ax.set_xlim(dt[0],dt[-1])
    ax.set_xlabel('Date')

    plt.show()
