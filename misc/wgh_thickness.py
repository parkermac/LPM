"""
Code to look at the wgh grid, exploring the bathymetry and water thickness.

The goal is to look at the causes of the apparent non-drying of south Willapa Bay.
"""

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cmcrameri.cm as cmc

Ldir = Lfun.Lstart()
fn = Ldir['roms_out'] / 'wgh1_t0_xn0b' / 'f2017.07.04' / 'ocean_his_0015.nc'
G = zrfun.get_basic_info(fn, only_G=True)
ds = xr.open_dataset(fn)
lon = G['lon_rho']
lat = G['lat_rho']
plon, plat = pfun.get_plon_plat(lon, lat)

h = G['h']
zeta = ds.zeta.values.squeeze()
m = G['mask_rho']
mwd = ds.wetdry_mask_rho.values.squeeze()

h[m==0] = np.nan
zeta[mwd==0] = np.nan

# Also load the original bathymetry file
tfn = Ldir['data'] / 'topo' / 'nw_pacific' / 'nw_pacific.nc'
tds = xr.open_dataset(tfn)
tlon_vec = tds['lon'].values
tlat_vec = tds['lat'].values
tz = tds['z'].values
# There is a bug in xarray with these files: it does
# not set masked regions to nan.  So we do it by hand.
tz[tz>1e6] = np.nan
tlon, tlat = np.meshgrid(tlon_vec, tlat_vec)
z = zfun.interp2(lon, lat, tlon, tlat, tz)
hh = -z
hh[m==0] = np.nan

cmap = cmc.roma_r

plt.close('all')
pfun.start_plot(figsize=(13,8))
fig = plt.figure()

ax = fig.add_subplot(221)
cs = plt.pcolormesh(plon,plat, h, vmin=0, vmax=2, cmap=cmap)
fig.colorbar(cs, ax=ax)
ax.set_title('h [m]')
ax.set_axis_off()

ax = fig.add_subplot(222)
cs = plt.pcolormesh(plon,plat, zeta+h, vmin=0, vmax=1, cmap=cmap)
fig.colorbar(cs, ax=ax)
ax.set_title('water thickness [m]')
ax.set_axis_off()

ax = fig.add_subplot(223)
cs = plt.pcolormesh(plon,plat, hh, vmin=0, vmax=2, cmap=cmap)
fig.colorbar(cs, ax=ax)
ax.set_title('original h [m]')
ax.set_axis_off()

ax = fig.add_subplot(224)
cs = plt.pcolormesh(plon,plat, zeta, vmin=-2, vmax=0, cmap=cmap)
fig.colorbar(cs, ax=ax)
ax.set_title('zeta [m]')
ax.set_axis_off()

plt.show()
pfun.end_plot()