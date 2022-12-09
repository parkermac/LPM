"""
Code to plot uu0mb field and compare with other runs
"""

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

Ldir = Lfun.Lstart()

in_dir = Ldir['parent'] / 'LPM_data' / 'f2021.02.15'
fn0 = in_dir / 'ocean_his_0025_live.nc'
fn1 = in_dir / 'ocean_his_0025_uu0mb.nc'
ds0 = xr.open_dataset(fn0)
ds1 = xr.open_dataset(fn1)

x, y = pfun.get_plon_plat(ds0.lon_rho.values, ds0.lat_rho.values)

plt.close('all')
pfun.start_plot(figsize=(26,10))
fig, axes = plt.subplots(nrows=1,ncols=3,squeeze=False)

cmap = 'Spectral_r'
vn = 'oxygen'
slev = 0

vm = {'TIC': (1500, 2500, 50),
    'alkalinity': (1500, 2500, 50),
    'NO3': (0, 50, 5),
    'salt': (25, 35, 1),
    'oxygen': (0, 250, 50),
    }

v0 = ds0[vn][0,slev,:,:].values
v1 = ds1[vn][0,slev,:,:].values

ax = axes[0,0]
cs = ax.pcolormesh(x,y,v0,cmap=cmap,
    vmin=vm[vn][0], vmax=vm[vn][1])
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title(vn + '[' + str(slev) + ']' + ' Old')
ax.text(.05,.2,'Max=%0.1f' % (np.nanmax(v0)), transform=ax.transAxes)
ax.text(.05,.1,'Min=%0.1f' % (np.nanmin(v0)), transform=ax.transAxes)

ax = axes[0,1]
cs = ax.pcolormesh(x,y,v1,cmap=cmap,
    vmin=vm[vn][0], vmax=vm[vn][1])
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('New')
ax.text(.05,.2,'Max=%0.1f' % (np.nanmax(v1)), transform=ax.transAxes)
ax.text(.05,.1,'Min=%0.1f' % (np.nanmin(v1)), transform=ax.transAxes)

ax = axes[0,2]
cs = ax.pcolormesh(x,y,v1-v0,cmap='RdYlBu_r',
    vmin=-vm[vn][2], vmax=vm[vn][2])
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('New - Old')

plt.show()

