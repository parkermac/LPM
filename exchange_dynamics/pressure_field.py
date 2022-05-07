"""
Code to plot the baroclinic contribution to pressure at a
chosen depth.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

fn = Ldir['roms_out'] / 'cas6_v0_live' / 'f2019.07.04' / 'ocean_his_0006.nc'
G,S,T = zrfun.get_basic_info(fn)
ds = xr.open_dataset(fn)

z_w = zrfun.get_z(G['h'], 0*G['h'], S, only_w=True)
dz = np.diff(z_w, axis=0)
rho = ds.rho.values.squeeze()
g = 9.8

p = np.cumsum(g * rho[::-1,:,:] * dz[::-1,:,:], axis=0)[::-1,:,:]
M, L = G['h'].shape
p0 = np.zeros((1,M,L))
pf = np.concatenate((p,p0), axis=0)

zref = -40
P = pfun.get_layer(pf, z_w, zref)

P = P - np.nanmean(P)

# plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111)

plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])

cs = ax.pcolormesh(plon, plat, P, cmap='jet', vmin = -1000, vmax=0)
fig.colorbar(cs, ax=ax)

pfun.dar(ax)
pfun.add_coast(ax)

#ax.axis([-123.75, -122, 47, 49])

plt.show()
pfun.end_plot()