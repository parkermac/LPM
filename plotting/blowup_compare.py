"""
Code to compare fields from two similar runs. Meant to help figure out
why 2014.06.18 is blowing up in the new long hindcast.

2025.09.29 PM
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from lo_tools import Lfun, zfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

fn1 = Ldir['roms_out'] / 'cas7_t0_x4b' / 'f2014.06.18' / 'ocean_his_0019.nc'
fn2 = Ldir['roms_out'] / 'cas7_t1_x11' / 'f2014.06.18' / 'ocean_his_0019.nc'

ds1 = xr.open_dataset(fn1)
ds2 = xr.open_dataset(fn2)

pfun.start_plot(figsize=(20,12))
fig = plt.figure()
ax = fig.add_subplot(111)

# a1 = ds1.zeta[0,:,:].to_numpy()
# a2 = ds2.zeta[0,:,:].to_numpy()
a1 = ds1.u[0,0,:,:].to_numpy()
a2 = ds2.u[0,0,:,:].to_numpy()

da = a2-a1

cs = plt.pcolormesh(da)
fig.colorbar(cs,ax=ax)

plt.show()
pfun.end_plot()