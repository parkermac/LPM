"""
Code to plot the Willapa Bay mooring data, and model output.

"""

import pandas as pd
import xarray as xr
import numpy as np
import gsw
from time import time
from datetime import datetime, timedelta

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# input location
source = 'willapa'
otype = 'moor' # introducing a new "otype" beyond ctd and bottle

from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
plt.close('all')
pfun.start_plot(figsize=(14,8))

year_str = '2024'
# processed data location
out_dir = Ldir['LOo'] / 'obs' / source / otype / year_str

sta_dict = {
    'Tokeland': (-123.96797728985608, 46.707252252710354),
    'Nahcotta': (-124.03074795328776, 46.500242867945865),
    'BayCenter': (-123.95239473341415, 46.629030151420984),
}

for sta in ['Nahcotta']:
    obs_fn = out_dir / (sta + '.p') # a pickled DataFrame
    obs_df = pd.read_pickle(obs_fn)
    ot = obs_df.index

    fig = plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    ax1.plot(ot, obs_df.SA.to_numpy(),'-r')
    ax1.set_title(sta)
    ax1.set_ylabel('Salinity')
    ax2.plot(ot, obs_df.CT.to_numpy(),'-r')
    ax2.set_ylabel('Temp (degC)')
    ax3.plot(ot, obs_df['DO (uM)'].to_numpy(),'-r')
    ax3.set_ylabel('DO (uM)')
    ax2.text(.05,.9,'Observed',color='r',fontweight='bold',transform=ax2.transAxes)

    gtx_dict = {
        'wgh2_t0_xn0b':'b',
        'cas7_t0_x4b':'g'
        }
    ii = 0
    for gtx in ['wgh2_t0_xn0b']:
        mod_dir = Ldir['LOo'] / 'extract' / gtx / 'moor' / 'willapa0'
        mod_fn = mod_dir / (sta + '_' + year_str + '.01.01' + '_' + year_str + '.12.31.nc')
        mod_ds = xr.open_dataset(mod_fn)
        mt = pd.DatetimeIndex(mod_ds.ocean_time)
        salt = mod_ds.salt[:,-1].to_numpy().squeeze()
        temp = mod_ds.temp[:,-1].to_numpy().squeeze()
        oxygen = mod_ds.oxygen[:,-1].to_numpy().squeeze()
        wdm = mod_ds.wetdry_mask_rho.to_numpy().squeeze()
        dpth = mod_ds.zeta.to_numpy().squeeze() + mod_ds.h.to_numpy()
        lon, lat = sta_dict[sta]
        P = 0 # pressure (the mooring is near the surface)
        # - do the conversions
        SA = gsw.SA_from_SP(salt, P, lon, lat)
        CT = gsw.CT_from_t(SA, temp, P)
        # SA[wdm==0] = np.nan
        # CT[wdm==0] = np.nan
        # oxygen[wdm==0] = np.nan
        SA[dpth<1] = np.nan
        CT[dpth<1] = np.nan
        oxygen[dpth<1] = np.nan

        # plot lines
        ax1.plot(mt, SA,'-'+gtx_dict[gtx],alpha=.6)
        ax2.plot(mt, CT,'-'+gtx_dict[gtx],alpha=.6)
        ax3.plot(mt, oxygen,'-'+gtx_dict[gtx],alpha=.6)
        ax2.text(.05,.8-ii*.1,gtx,color=gtx_dict[gtx],fontweight='bold',transform=ax2.transAxes)

        ii += 1




