"""
Code to look at the differences between files generate by "identical"
runs that differ mainly in being old or new roms.
"""

import xarray as xr
from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun
import numpy as np
import matplotlib.pyplot as plt

Ldir = Lfun.Lstart()

# old roms
fn0 = Ldir['roms_out'] / 'cas6_v0_u0kb' / 'f2022.01.07' / 'ocean_his_0025.nc'

# new roms
fn1 = Ldir['roms_out'] / 'cas6_v0_uu0kb' / 'f2022.01.07' / 'ocean_his_0025.nc'

ds0 = xr.open_dataset(fn0)
ds1 = xr.open_dataset(fn1)

G, S, T = zrfun.get_basic_info(fn1)
plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])

# plotting

plt.close('all')
pfun.start_plot(figsize=(16,13))

fig, axes = plt.subplots(nrows=2, ncols=3)

vn = 'oxygen'

if vn == 'salt':
    Vmin = 20; Vmax = 35 # surface
    vmin = 20; vmax = 35 # bottom
    dd = 1 # scale for difference plot
    plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
elif vn == 'temp':
    Vmin = 3; Vmax = 15
    vmin = 3; vmax = 15
    dd = 1
    plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
elif vn == 'u':
    Vmin = -1; Vmax = 1
    vmin = -1; vmax = 1
    dd = .2
    plon, plat = pfun.get_plon_plat(G['lon_u'], G['lat_u'])
elif vn == 'v':
    Vmin = -1; Vmax = 1
    vmin = -1; vmax = 1
    dd = .2
    plon, plat = pfun.get_plon_plat(G['lon_v'], G['lat_v'])
elif vn == 'oxygen':
    Vmin = 0; Vmax = 350
    vmin = 0; vmax = 350
    dd = 20
    plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
elif vn == 'NO3':
    Vmin = 0; Vmax = 50
    vmin = 0; vmax = 50
    dd = 5
    plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
elif vn == 'phytoplankton':
    Vmin = 0; Vmax = 3
    vmin = 0; vmax = 1
    dd = .2
    plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
    
# ===== top ===========================
nn = -1
ax = axes[0,0]
cs = ax.pcolormesh(plon, plat,
    ds0[vn][0,nn,:,:].values,
    cmap='jet',
    vmin=Vmin, vmax = Vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Surface old')
#
ax = axes[0,1]
cs = ax.pcolormesh(plon, plat,
    ds1[vn][0,nn,:,:].values,
    cmap='jet',
    vmin=Vmin, vmax=Vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Surface new')
#
ax = axes[0,2]
cs = ax.pcolormesh(plon, plat,
    ds0[vn][0,nn,:,:].values - ds1[vn][0,nn,:,:].values,
    cmap='RdYlBu_r',
    vmin=-dd, vmax=dd)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Surface old-new')

# ===== bottom ======================
nn = 0
ax = axes[1,0]
cs = ax.pcolormesh(plon, plat,
    ds0[vn][0,nn,:,:].values,
    cmap='jet',
    vmin=vmin, vmax = vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Bottom old')
#
ax = axes[1,1]
cs = ax.pcolormesh(plon, plat,
    ds1[vn][0,nn,:,:].values,
    cmap='jet',
    vmin=vmin, vmax=vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Bottom new')
#
ax = axes[1,2]
cs = ax.pcolormesh(plon, plat,
    ds0[vn][0,nn,:,:].values - ds1[vn][0,nn,:,:].values,
    cmap='RdYlBu_r',
    vmin=-dd, vmax=dd)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)

fig.suptitle(vn)

plt.show()
pfun.end_plot()
ax.set_title('Bottom old-new')

