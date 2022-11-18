"""
Code to compare carbon variables in the undated ROMS.

RESULT: they look identical
"""

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
import matplotlib.pyplot as plt
import xarray as xr

from pathlib import Path

P = Path('/Users/pm8/Desktop')

fn_old = P / 'original' / 'layers1' / 'layers.nc'
fn_new = P / 'new' / 'layers1' / 'layers.nc'

ds_old = xr.open_dataset(fn_old)
ds_new = xr.open_dataset(fn_new)

vn = 'PH_10'
vmin = 7
vmax = 8.5

v_old = ds_old[vn][0,:,:].values
v_new = ds_new[vn][0,:,:].values

plon, plat = pfun.get_plon_plat(ds_old.lon_rho.values, ds_old.lat_rho.values)

plt.close('all')
pfun.start_plot(figsize=(24,12))
fig = plt.figure()

ax = fig.add_subplot(131)
cs = ax.pcolormesh(plon, plat, v_old, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)

ax = fig.add_subplot(132)
cs = ax.pcolormesh(plon, plat, v_new, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)

ax = fig.add_subplot(133)
cs = ax.pcolormesh(plon, plat, v_new - v_old, cmap='jet', vmin=-.01, vmax=.01)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)


plt.show()
