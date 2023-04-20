"""
Code to compare carbon variables in the updated ROMS.
"""

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
import matplotlib.pyplot as plt
import xarray as xr

Ldir = Lfun.Lstart()

fn_old = Ldir['roms_out'] / 'cas6_v0_live' / 'f2021.07.04' / 'ocean_his_0002.nc'
fn_new = Ldir['roms_out'] / 'cas6_v00_uu0mb' / 'f2021.07.04' / 'ocean_his_0002.nc'

ds_old = xr.open_dataset(fn_old)
ds_new = xr.open_dataset(fn_new)

nlev = 0
vn = 'alkalinity'
vmin = 1500
vmax = 2500

v_old = ds_old[vn][0,nlev,:,:].values
v_new = ds_new[vn][0,nlev,:,:].values

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
cs = ax.pcolormesh(plon, plat, v_new - v_old, cmap='jet', vmin=-100, vmax=100)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)


plt.show()
