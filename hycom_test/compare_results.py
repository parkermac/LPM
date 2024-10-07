"""
Check that the results of ocn02 look close to ocn01.
"""


import os
import numpy as np
from datetime import datetime, timedelta
import xarray as xr
from time import time
import pandas as pd
from lo_tools import Lfun, zfun
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

in_dir0 = Ldir['LOo'] / 'forcing' / 'cas7' / 'f2024.09.14'
in_dir1 = in_dir0 / 'ocn01'
in_dir2 = in_dir0 / 'ocn02'

fn1 = in_dir1 / 'ocean_clm.nc'
fn2 = in_dir2 / 'ocean_clm.nc'

ds1 = xr.open_dataset(fn1)
ds2 = xr.open_dataset(fn2)

# Note: it is odd that ds1 only has two times (9/11 and 9/17)
# whereas ds2 has the expected 4: 9/14-17.

# Also the zeta fields at 9/17 are the most different of the ones I looked at
# but this could be because its last "real" field came from 9/11!

# dsh = xr.open_dataset(in_dir2 / 'Data' / 'h2024.09.14.nc')
# this looks fine

plt.close('all')
pfun.start_plot(figsize=(20,10))

vlims_dict = {'zeta':(-.2,.2), 'salt':(31,34), 'temp':(16,20)}

for vn in ['zeta']:
    v1 = ds1[vn][-1,:,:].values
    v2 = ds2[vn][-1,:,:].values
    nan1 = np.sum(np.isnan(v1))
    nan2 = np.sum(np.isnan(v2))
    print('nan1 = %d, nan2 = %d' % (nan1,nan2))
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    vmin, vmax = vlims_dict[vn]
    ds1[vn][-1,:,:].plot(ax=ax1, vmin=vmin, vmax=vmax)
    ds2[vn][-1,:,:].plot(ax=ax2, vmin=vmin, vmax=vmax)

for vn in ['salt','temp']:
    v1 = ds1[vn][-1,-1,:,:].values
    v2 = ds2[vn][-1,-1,:,:].values
    nan1 = np.sum(np.isnan(v1))
    nan2 = np.sum(np.isnan(v2))
    print('nan1 = %d, nan2 = %d' % (nan1,nan2))
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    vmin, vmax = vlims_dict[vn]
    ds1[vn][-1,-1,:,:].plot(ax=ax1, vmin=vmin, vmax=vmax)
    ds2[vn][-1,-1,:,:].plot(ax=ax2, vmin=vmin, vmax=vmax)

plt.show()
