"""
Code to analyze a mooring extraction in relation to processes that affect bottom pressure.
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

sn_list = ['CE01', 'CE02', 'CE04', 'PN01A']
#sn_list = ['CE04']

fs = 12
def icb(ax, cs):
    # cbaxes = inset_axes(ax, width="40%", height="4%", loc='upper right', borderpad=2)
    # cb = fig.colorbar(cs, cax=cbaxes, orientation='horizontal')
    ax.fill([.93,.995,.995,.93],[.05,.05,.95,.95],'w', alpha=.5, transform=ax.transAxes)
    cbaxes = inset_axes(ax, width="2%", height="80%", loc='right', borderpad=3) 
    cb = fig.colorbar(cs, cax=cbaxes, orientation='vertical')
    cb.ax.tick_params(labelsize=.85*fs)

for sn in sn_list:
    
    fn = Ldir['LOo'] / 'extract' / 'cas6_v3_lo8b' / 'moor' / 'ooi' / (sn + '_2018.01.01_2018.12.31.nc')
    ds = xr.open_dataset(fn)

    # get time axis
    ot = ds.ocean_time.values # an array with dtype='datetime64[ns]'
    dti = pd.to_datetime(ot) # a pandas DatetimeIndex with dtype='datetime64[ns]'
    dt = dti.to_pydatetime() # an array of datetimes

    # set constants
    pad = 36 # this trims the ends after the low pass so there are no nan's
    g = 9.81 # gravity [m s-2]

    # pull fields from dataset
    z = ds.z_rho.values
    zw = ds.z_w.values
    eta = ds.zeta.values
    salt = ds.salt.values
    temp = ds.temp.values
    lon = ds.lon_rho.values
    lat = ds.lat_rho.values
    u = ds.u.values
    v = ds.v.values
    NT, N = z.shape

    # make time-mean z positions so we can isolate baroclinic and SSH
    # contributions to pressure variation
    Z = np.mean(z, axis=0)
    ZW = np.mean(zw, axis=0)
    DZ = np.diff(ZW)
    # adjust so free surface is at 0
    Z -= ZW[-1]
    ZW -= ZW[-1]

    # Equation of state calculations
    p = gsw.p_from_z(Z, lat)
    SA = gsw.SA_from_SP(salt, p, lon, lat) # absolute salinity
    CT = gsw.CT_from_pt(SA, temp) # conservative temperature
    if True:
        rho = gsw.rho(SA, CT, p)
        # This is denser than ROMS rho by 0.037 [kg m-3] at the bottom and 0.0046 [kg m-3]
        # (annual averages), and it is the full density, not density minus 1000.
        # There was no visual difference between the pressure time series.
    else:
        rho = ds.rho.values # makes no difference to add 1000 [kg m-3]

    # low pass filtered version
    etalp = zfun.lowpass(eta, f='godin')[pad:-pad:24]
    etalp = etalp - np.mean(etalp) # remove mean SSH
    rholp = zfun.lowpass(rho, f='godin')[pad:-pad:24, :]
    saltlp = zfun.lowpass(SA, f='godin')[pad:-pad:24, :]
    templp = zfun.lowpass(CT, f='godin')[pad:-pad:24, :]
    ulp = zfun.lowpass(u, f='godin')[pad:-pad:24, :]
    vlp = zfun.lowpass(v, f='godin')[pad:-pad:24, :]

    # also make associated time vectors
    tlp = dt[pad:-pad:24]
    tlpf = dt[24:-24:24] # "full" version used for pcolormesh plots
    NTlp = len(etalp)

    # calculate the baroclinic pressure
    plp = np.flip(np.cumsum(np.flip(g * rholp * DZ.reshape((1,N)), axis=1), axis=1), axis=1)

    # calculate the pressure due to SSH
    plp0 = g * 1025 *etalp

    # annual means
    Rho = np.mean(rholp, axis=0)
    Salt = np.mean(saltlp, axis=0)
    Temp = np.mean(templp, axis=0)
    P = np.mean(plp, axis=0)
    U = np.mean(ulp, axis=0)
    V = np.mean(vlp, axis=0)

    # anomalies from the annual mean
    saltlp_a = saltlp - Salt.reshape((1,N))
    templp_a = templp - Temp.reshape((1,N))
    rholp_a = rholp - Rho.reshape((1,N))
    plp_a = plp - P.reshape((1,N))
    ulp_a = ulp - U.reshape((1,N))
    vlp_a = vlp - V.reshape((1,N))

    # separate contributions of salt and temp to density
    rho_only_salt = gsw.rho(saltlp, templp - templp_a, p) - Rho.reshape((1,N))
    rho_only_temp = gsw.rho(saltlp - saltlp_a, templp, p) - Rho.reshape((1,N))

    # make the full pressure anomaly
    plp_aa = plp_a + plp0.reshape((NTlp,1))

    # plotting
    #plt.close('all')
    pfun.start_plot(fs=fs, figsize=(18,12))

    if True:
        # (1) pressure
        fig = plt.figure()
        nrow = 4
        #
        ax = fig.add_subplot(nrow,1,1)
        cs = ax.pcolormesh(tlpf, ZW, plp_a.T, cmap='RdYlBu_r', vmin=-500, vmax=500)
        icb(ax,cs)
        ax.text(.03, .07, 'Low-passed Baroclinic Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
        ax.grid(True)
        ax.set_title(sn)
        ax.set_xlim(dt[0],dt[-1])
        #
        ax = fig.add_subplot(nrow,1,2)
        cs = ax.pcolormesh(tlpf, ZW, plp_aa.T, cmap='RdYlBu_r', vmin=-500, vmax=500)
        ax.text(.03, .07, 'Low-passed Full Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
        ax.grid(True)
        icb(ax,cs)
        ax.set_xlim(dt[0],dt[-1])
        #
        ax = fig.add_subplot(nrow,1,3)
        cs = ax.pcolormesh(tlpf, ZW, vlp_a.T, cmap='RdYlBu_r', vmin=-0.2, vmax=0.2)
        ax.text(.03, .07, 'Low-passed V [m s-1]', transform=ax.transAxes, weight='bold')
        ax.grid(True)
        icb(ax,cs)
        ax.set_xlim(dt[0],dt[-1])
        #
        ax = fig.add_subplot(nrow,1,4)
        nfilt = 1 # days for Hanning filter
        ax.plot(tlp, zfun.lowpass(plp0, 'hanning', n=nfilt), '-', c='orange', lw=3, label='Due to surface height')
        ax.plot(tlp, zfun.lowpass(plp_a[:,0], 'hanning', n=nfilt), '-', c='cornflowerblue', lw=3, label='Baroclinic only')
        ax.plot(tlp, zfun.lowpass(plp_aa[:,0], 'hanning', n=nfilt), '-r', lw=3, label='Full')
        ax.legend(loc='upper left', ncol=3)
        ax.grid(True)
        ax.text(.03, .07, 'Parts of the Bottom Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
        ax.set_xlim(dt[0],dt[-1])

    if False:
        # (2) properties that affect baroclinic pressure
        fig = plt.figure()
        nrow = 3
        #
        ax = fig.add_subplot(nrow,1,1)
        cs = ax.pcolormesh(tlpf, ZW, saltlp_a.T, cmap='RdYlBu_r', vmin=-.5, vmax=.5)
        ax.text(.03, .07, 'Low-passed Absolute Salinity Anomaly [g kg-1]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)
        #
        ax = fig.add_subplot(nrow,1,2)
        cs = ax.pcolormesh(tlpf, ZW, templp_a.T, cmap='RdYlBu_r', vmin=-2,vmax=2)
        ax.text(.03, .07, 'Low-passed Conservative Temperature Anomaly [deg C]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)
        #
        ax = fig.add_subplot(nrow,1,3)
        cs = ax.pcolormesh(tlpf, ZW, rholp_a.T, cmap='RdYlBu_r', vmin=-.5,vmax=.5)
        ax.text(.03, .07, 'Low-passed Density Anomaly [Pa]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)

    if False:
        # (2) properties that affect density
        fig = plt.figure()
        nrow = 3
        #
        ax = fig.add_subplot(nrow,1,1)
        cs = ax.pcolormesh(tlpf, ZW, rho_only_salt.T, cmap='RdYlBu_r', vmin=-.5, vmax=.5)
        ax.text(.03, .07, 'Portion Due to Absolute Salinity Anomaly [g kg-1]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)
        #
        ax = fig.add_subplot(nrow,1,2)
        cs = ax.pcolormesh(tlpf, ZW, rho_only_temp.T, cmap='RdYlBu_r', vmin=-.5,vmax=.5)
        ax.text(.03, .07, 'Portion Due to Conservative Temperature Anomaly [deg C]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)
        #
        ax = fig.add_subplot(nrow,1,3)
        cs = ax.pcolormesh(tlpf, ZW, rholp_a.T, cmap='RdYlBu_r', vmin=-.5,vmax=.5)
        ax.text(.03, .07, 'Low-passed Density Anomaly [Pa]', transform=ax.transAxes, weight='bold')
        fig.colorbar(cs, ax=ax)
        #
        # ax = fig.add_subplot(nrow,1,4)
        # cs = ax.pcolormesh(tlpf, ZW, rho_only_salt.T + rho_only_temp.T, cmap='RdYlBu_r', vmin=-.5,vmax=.5)
        # ax.text(.03, .07, 'Sum of 1 and 2 [Pa]', transform=ax.transAxes, weight='bold')
        # fig.colorbar(cs, ax=ax)
        
    ds.close()

plt.show()
