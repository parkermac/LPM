"""
Code to analyze a mooring extraction in relation to processes that affect bottom pressure.
"""

import xarray as xr
import numpy as np
import gsw
import pandas as pd
import matplotlib.pyplot as plt
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

# set mooring extraction to analyze (just needs salt, temp, and zeta)
Ldir = Lfun.Lstart()

plt.close('all')
pfun.start_plot(figsize=(18,12))
fig = plt.figure()

sn_list = ['CE01', 'CE02', 'CE04', 'PN01A']
nrow = len(sn_list)

ii = 1
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

    # anomalies from the annual mean
    saltlp_a = saltlp - Salt.reshape((1,N))
    templp_a = templp - Temp.reshape((1,N))
    rholp_a = rholp - Rho.reshape((1,N))
    plp_a = plp - P.reshape((1,N))

    # separate contributions of salt and temp to density
    rho_only_salt = gsw.rho(saltlp, templp - templp_a, p) - Rho.reshape((1,N))
    rho_only_temp = gsw.rho(saltlp - saltlp_a, templp, p) - Rho.reshape((1,N))

    # make the full pressure anomaly
    plp_aa = plp_a + plp0.reshape((NTlp,1))

    # plotting
    #
    ax = fig.add_subplot(nrow,1,ii)
    nfilt = 1 # days for Hanning filter
    ax.plot(tlp, zfun.lowpass(plp0, 'hanning', n=nfilt), '-', c='orange', lw=3, label='Due to surface height')
    ax.plot(tlp, zfun.lowpass(plp_a[:,0], 'hanning', n=nfilt), '-', c='cornflowerblue', lw=3, label='Baroclinic only')
    ax.plot(tlp, zfun.lowpass(plp_aa[:,0], 'hanning', n=nfilt), '-r', lw=3, label='Full')
    ax.set_ylim(-2000,3000)
    ax.set_xlim(dt[0],dt[-1])
    ax.axhline(c='k',lw=1.5)
    ax.grid(True)
    ax.text(.03, .87, sn, transform=ax.transAxes, weight='bold')
    if ii == 1:
        ax.legend()
        ax.text(.03, .07, 'Parts of the Bottom Pressure Anomaly [Pa]', transform=ax.transAxes, weight='bold')
    if ii == 4:
        ax.text(.95, .87, '1000 [Pa] is equivalent to 10 [cm] water height', transform=ax.transAxes, ha='right')
        ax.set_xlabel('Date')
    else:
        ax.set_xticklabels([])

    ii += 1

        
    ds.close()

plt.show()
