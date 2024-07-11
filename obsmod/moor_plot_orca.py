"""
Code to plot model comparisons to the ORCA mooring records.
"""

import pandas as pd
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import gsw

import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

# ORCA mooring locations, from Erin Broatch 2023.06.16
sta_dict = {
    'CI': (-122.7300, 47.2800),
    'PW': (-122.3972, 47.7612),
    'NB': (-122.6270, 47.9073),
    'DB': (-122.8029, 47.8034),
    'HP': (-123.1126, 47.4218),
    'TW': (-123.0083, 47.3750)
}

testing = False
small = False
if testing:
    sn_list = ['HP']
else:
    sn_list = sta_dict.keys()
if small:
    figsize = (12,7)
else:
    figsize = (16,12)

# Create output directory
out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod' / 'moor_orca'
Lfun.make_dir(out_dir)

plt.close('all')
for sn in sn_list:

    print('\n===================')
    print(sn)

    # Specify obs and mod files to work on.
    source = 'orca'
    fn_obs = Ldir['LOo'] / 'obs' / source / 'moor' / (sn + '_daily.nc')
    gtx = 'cas7_t0_x4b'
    fn_mod = Ldir['LOo'] / 'extract' / gtx / 'moor' / source / \
        (sn + '_2013.01.01_2021.12.31.nc')

    dso = xr.open_dataset(fn_obs)
    To = dso.time.values # Daily at midnight and we assume that the time corresponds
    # to an average over the day, so we would add 12 hours to center it at noon.
    dto = pd.DatetimeIndex(To)
    zo = dso.z.values

    # # extended axes
    # # - time
    # dto_ext = dto.union(dto[-2:]+timedelta(days=1))
    # jdo_ext = dto_ext.to_julian_date().to_numpy()
    # jdo_ext -= jdo_ext[0]
    # # - z
    # dzo = np.diff(zo)
    # zo_ext = np.concatenate((np.array(zo[0]-dzo[0]/2).reshape((1)),
    #     zo[:-1]+dzo/2,
    #     np.array(zo[-1]+dzo[-1]/2).reshape((1))))
    # # make axes arrays instead of vectors
    # JD = jdo_ext.reshape((-1,1)) * np.ones(len(zo_ext)).reshape((1,-1))
    # Z = np.ones(len(jdo_ext)).reshape((-1,1)) * zo_ext.reshape((1,-1))

    dsm = xr.open_dataset(fn_mod)
    Tm = dsm.ocean_time.values
    # daily at noon UTC because we extracted from lowpassed files
    dtm = pd.DatetimeIndex(Tm)
    zm = np.mean(dsm.z_rho.values, axis=0)

    # set z levels
    # z = np.array([-100, -50, -20, -5])
    z = np.arange(-205,5,10)
    z = z[z>zo.min()+5]
    z = z[z>zm.min()+5]
    z = np.array([z[0],z[-1]])
    nz = len(z)

    # interpolate observations
    i0, i1, fr = zfun.get_interpolant(z, zo)
    vn_list = ['SA', 'CT', 'DO (uM)']
    o_dict = dict()
    for vn in vn_list:
        v = dso[vn].values
        vv = np.nan * np.ones((len(dto),nz)) # initialize a result array
        for ii in range (nz):
            # Fill the result array by using the interpolants.
            vv[:,ii] = (1-fr[ii])*v[:,i0[ii]] + fr[ii]*v[:,i1[ii]]
        o_dict[vn] = vv # store the result in a dict

    # interpolate model fields
    i0, i1, fr = zfun.get_interpolant(z, zm)
    # Pull out model fields and interpolate to the good z-level of the
    # observations.
    m_dict = dict()
    m_vn_list = ['salt', 'temp', 'oxygen','z_rho']
    for vn in m_vn_list:
        v = dsm[vn].values
        vv = np.nan * np.ones((len(Tm),nz)) # initialize a result array
        for ii in range (nz):
            # Fill the result array by using the interpolants.
            vv[:,ii] = (1-fr[ii])*v[:,i0[ii]] + fr[ii]*v[:,i1[ii]]
        m_dict[vn] = vv # store the result in a dict
    # Convert model fields to LO standard units and names. Makes use of
    # the gsw equations of state for seawater.
    SP = m_dict['salt'] # salinity [psu]
    zr = m_dict['z_rho']
    PT = m_dict['temp'] # potential temperature [degC]
    lon = dsm.lon_rho.values
    lat = dsm.lat_rho.values
    p = gsw.p_from_z(zr, lat) # get pressure
    SA = gsw.SA_from_SP(SP, p, lon, lat) # Absolute Salinity [g kg-1]
    CT = gsw.CT_from_pt(SA, PT) # Conservative Temperature [deg C]
    # save results in the dict
    m_dict['SA'] = SA
    m_dict['CT'] = CT
    m_dict['DO (uM)'] = m_dict['oxygen']
    # Now we have two dictionaries that have fields with matching structures
    # that we can use for plotting

    # Plotting


    if nz > 0:

        pfun.start_plot(figsize=figsize)
        fig = plt.figure()
        fig.suptitle(sn)
        ii = 1
        zcol = 'brcgmky' # colors to use for z-levels
        for vn in ['SA', 'CT', 'DO (uM)']:
            ax = fig.add_subplot(3,1,ii)
            cc = 0
            for zz in z:
                ax.plot(dto,o_dict[vn][:,cc],'-'+zcol[cc])
                ax.plot(dtm,m_dict[vn][:,cc],'-'+zcol[cc],alpha=.4)
                ax.set_xlim(dtm[0],dtm[-1]) # trim time axis to only use model period.
                ax.set_ylabel(vn)
                if vn == 'DO (uM)':
                    ax.set_xlabel('Year')
                else:
                    ax.set_xticklabels([])
                if vn == 'SA':
                    ax.text(.05,.05+cc*.15,'Z = %0.1f [m]' % (z[cc]),fontweight='bold', color=zcol[cc],
                        transform=ax.transAxes)
                cc += 1
            ax.grid(True)
            ii += 1

    if testing:
        plt.show()
    else:
        fig.savefig(out_dir / (sn + '.png'))



