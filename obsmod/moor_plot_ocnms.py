"""
Code to plot model comparisons to the OCNMS mooring records.
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

# OCNMS moorings, generated by LO/obs/ocnms/extract_locations.py
sta_dict = {
    'MB042':(-124.7354, 48.3240), # Makah Bay 42m
    'MB015':(-124.6768, 48.3254), # Makah Bay 15m
    'CA042':(-124.8234, 48.1660), # Cape Alava 42m
    'CA015':(-124.7568, 48.1663), # Cape Alava 15m
    'TH042':(-124.7334, 47.8762), # Teahwhit Head 42m
    'TH015':(-124.6195, 47.8755), # Teahwhit Head 15m
    'KL027':(-124.4971, 47.5946), # Kalaloch 27m
    'KL015':(-124.4284, 47.6008), # Kalaloch 15m
    'CE042':(-124.4887, 47.3531), # Cape Elizabeth 42m
    'CE015':(-124.3481, 47.3568), # Cape Elizabeth 15m
}

testing = False
if testing:
    sn_list = ['MB042']
else:
    sn_list = sta_dict.keys()

# Create output directory
out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod' / 'moor_ocnms'
Lfun.make_dir(out_dir)

plt.close('all')
for sn in sn_list:

    print('\n===================')
    print(sn)

    # Specify obs and mod files to work on.
    source = 'ocnms'
    fn_obs = Ldir['LOo'] / 'obs' / source / 'moor' / (sn + '_2011_2023_hourly.nc')
    gtx = 'cas7_t0_x4b'
    fn_mod = Ldir['LOo'] / 'extract' / gtx / 'moor' / source / (sn + '_2013.01.01_2020.12.31.nc')

    dso = xr.open_dataset(fn_obs)
    To = dso.time.values # hourly
    nz = len(dso.z) # Original number of obs z-positions.
    # NOTE: We will end up with fewer z-levels because we only keep levels that have SA or CT
    # or DO. I _think_ that a lot of the z_levels shown in the LO/obs/ocnms README figure
    # only have in-situ temperature. I should check this.

    dsm = xr.open_dataset(fn_mod)
    Tm = dsm.ocean_time.values # daily at noon UTC because we extracted from lowpassed files

    # Interpolate model z to z of observed values. I
    zo = dso.z.values
    zo = [float(item) for item in zo]
    zo = np.array(zo)
    # NOTE: the ocnms mooring Datasets are packed shallow-to-deep. Throughout
    # this code we will repack them to be deep-to-shallow, thereby matching
    # the model mooring fields.
    zo = zo[::-1] # flip to be ordered bottom to top
    zm = np.mean(dsm.z_rho.values, axis=0) # vector of mean model z
    # get the interpolants to map modeled fields to observed depths
    i0, i1, fr = zfun.get_interpolant(zo, zm)
    # Use the interpolants.
    print('\nOriginal z levels:')
    for ii in range(nz):
        zoo = zo[ii]
        # Account for times when observations are deeper than the
        # deepest rho point. This is hard-wired to only work for the
        # deepest obs point.
        if np.isnan(fr[ii]) and ii == 0:
            fr[0] = 0 # the effect is the use the deepest model value.
        zmm = (1-fr[ii])*zm[i0[ii]] + fr[ii]*zm[i1[ii]]
        # This print statement is just to let us see what the depth ranges are
        # and to check that our interpolants will work at all of them.
        print('Observed z = %0.1f, Interpolated model z = %0.1f' % (zoo, zmm))

    # Lowpass the observed fields and keep only daily values, in order to match
    # the time axis of the model fields.
    # We assume we started from hourly time series and that the first hour was
    # at midnight of the first day.
    pad = 36
    To = To[pad:-pad+1:24] # subsample obs times to daily at noon UTC
    o_dict = dict() # dict to hold processed obs fields
    good_zo_mask = np.zeros(nz) # Initialize a vector to help keep track of which
    # observed z positions we want to use in the comparison.
    o_vn_list = ['SA', 'CT', 'DO (uM)']
    for vn in o_vn_list:
        fld = dso[vn].values
        fld = zfun.lowpass(fld, f='godin') # lowpass
        fld = fld[:, ::-1] # flip to be packed bottom-to-top
        fld = fld[pad:-pad+1:24, :] # subsample to daily at noon UTC
        o_dict[vn] = fld # save the result array (packed time,z)
        good_zo_mask += np.nansum(fld, axis=0) # Update the mask.
        # NOTE: the mask update step above relies on the fact that in up-to-date
        # versions of numpy np.nansum() will return zero when it is adding up
        # row of all NaN's. Thus the result is that good_zo_mask will only have
        # non-zero entries fo z levels that have data in any of the three
        # variables we are using.
    good_zo_mask = good_zo_mask != 0 # Make good_zo_mask a boolean array
    
    # Use the mask to make a vector "good_zo" that is the model z's we keep.
    good_zo = zo[good_zo_mask]
    print('\nNew z levels:')
    print(good_zo)
    nz = len(good_zo) # update nz
    # Use the mask to keep only the interpolants we need.
    i0 = i0[good_zo_mask]
    i1 = i1[good_zo_mask]
    fr = fr[good_zo_mask]

    # Use the mask to keep only the observed z-levels that we need.
    o_dict_good = dict()
    for vn in o_vn_list:
        vv = o_dict[vn][:,good_zo_mask]
        o_dict_good[vn] = vv

    # Pull out model fields and interpolate to the good z-level of the
    # observations.
    m_dict = dict()
    m_vn_list = ['salt', 'temp', 'oxygen','z_rho']
    for vn in m_vn_list:
        v = dsm[vn].values
        vv = np.nan * np.ones((len(Tm),nz)) # initialize a result array
        for ii in range (nz):
            # Fill the result array by using the shortened interpolants.
            vv[:,ii] = (1-fr[ii])*v[:,i0[ii]] + fr[ii]*v[:,i1[ii]]
        m_dict[vn] = vv # store the result in a dict

    # Convert model fields to LO standard units and names. Makes use of
    # the gsw equations of state for seawater.
    SP = m_dict['salt'] # salinity [psu]
    z = m_dict['z_rho']
    PT = m_dict['temp'] # potential temperature [degC]
    lon = dsm.lon_rho.values
    lat = dsm.lat_rho.values
    p = gsw.p_from_z(z, lat) # get pressure
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

        pfun.start_plot(figsize=(22,12))
        fig = plt.figure()
        fig.suptitle(sn)
        ii = 1
        zcol = 'brcgmky' # colors to use for z-levels
        for vn in ['SA', 'CT', 'DO (uM)']:
            ax = fig.add_subplot(3,1,ii)
            cc = 0
            for zz in good_zo:
                ax.plot(To,o_dict_good[vn][:,cc],'-'+zcol[cc])
                ax.plot(Tm,m_dict[vn][:,cc],'-'+zcol[cc],alpha=.4)
                ax.set_xlim(Tm[0],Tm[-1]) # trim time axis to only use model period.
                ax.set_ylabel(vn)
                if vn == 'DO (uM)':
                    ax.set_xlabel('Time')
                else:
                    ax.set_xticklabels([])
                if vn == 'SA':
                    ax.text(.05,.05+cc*.15,'Z = %0.1f [m]' % (good_zo[cc]),fontweight='bold', color=zcol[cc],
                        transform=ax.transAxes)
                cc += 1
            ax.grid(True)
            ii += 1

        if testing:
            plt.show()
        else:
            fig.savefig(out_dir / (sn + '.png'))

    else:
        print('** No good z-levels for ' + sn)

