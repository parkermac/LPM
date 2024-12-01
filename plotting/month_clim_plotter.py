"""
Code to explore plotting of monthly means and their anomaly from climatology.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

gtagex = 'cas7_t0_x4b'
month = 1
year = 2020
dt = datetime(year,month,1)
ym_str = dt.strftime('%Y_%m')
mo_str = ('000' + str(month))[-2:]

in_dir0 = Ldir['parent'] / 'LO_roms' / gtagex
in_fn1 = in_dir0 / 'averages' / ('monthly_mean_' + ym_str + '.nc')
in_fn2 = in_dir0 / 'climatologies' / ('monthly_clim_' + mo_str + '.nc')

ds1 = xr.open_dataset(in_fn1)
ds2 = xr.open_dataset(in_fn2)

plt.close('all')

fld = 'temp'
slev = -1
f1 = ds1[fld][0,slev,:,:].values
f2 = ds2[fld][0,slev,:,:].values

plon, plat = pfun.get_plon_plat(ds1['lon_rho'].values, ds1['lat_rho'].values)

pfun.start_plot(figsize=(16,10))
fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

cs1 = ax1.pcolormesh(plon,plat,f1,cmap='rainbow')
fig.colorbar(cs1, ax=ax1)
pfun.dar(ax1)

cs2 = ax2.pcolormesh(plon,plat,f1-f2,cmap='RdYlBu_r')
fig.colorbar(cs2, ax=ax2)
pfun.dar(ax2)

plt.show()