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

# dsh = xr.open_dataset(in_dir2 / 'Data' / 'h2024.09.14.nc')
# this looks fine

plt.close('all')
pfun.start_plot(figsize=(20,10))

for vn in ['zeta']:
    v1 = ds1[vn][0,:,:].values
    v2 = ds2[vn][0,:,:].values
    nan1 = np.sum(np.isnan(v1))
    nan2 = np.sum(np.isnan(v2))
    print('nan1 = %d, nan2 = %d' % (nan1,nan2))
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ds1[vn][0,:,:].plot(ax=ax1)
    ds2[vn][0,:,:].plot(ax=ax2)

for vn in ['salt','temp']:
    v1 = ds1[vn][0,-1,:,:].values
    v2 = ds2[vn][0,-1,:,:].values
    nan1 = np.sum(np.isnan(v1))
    nan2 = np.sum(np.isnan(v2))
    print('nan1 = %d, nan2 = %d' % (nan1,nan2))
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ds1[vn][0,-1,:,:].plot(ax=ax1)
    ds2[vn][0,-1,:,:].plot(ax=ax2)

plt.show()
