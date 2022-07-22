"""
Checking on the results of running with EMINUSP.

Result: the new version with EMINUSP is clearly fresher at the surface overall.

It is also interesting that these do not exactly reproduce each other - small
differences can lead to big changes in the exact location of the river plumes
in this case.

"""

import matplotlib.pyplot as plt
import xarray as xr

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

# model output
fn1 = Ldir['roms_out']/ 'cas6_v00_uu0kb' / 'f2021.01.31' / 'ocean_his_0025.nc'
fn2 = Ldir['roms_out']/ 'cas6_v00_uu0k' / 'f2021.01.31' / 'ocean_his_0025.nc' # has EMINUSP

ds1 = xr.open_dataset(fn1)
ds2 = xr.open_dataset(fn2)

x,y = pfun.get_plon_plat(ds1.lon_rho.values, ds1.lat_rho.values)
s1 = ds1.salt[0,-1,:,:].values
s2 = ds2.salt[0,-1,:,:].values


# PLOTTING
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(18,9))

ax = fig.add_subplot(131)
cs = ax.pcolormesh(x,y,s1,vmin=25,vmax=33.5,cmap='jet')
fig.colorbar(cs,ax=ax)
ax.set_title('Salt Old: uu0kb')

ax = fig.add_subplot(132)
cs = ax.pcolormesh(x,y,s2,vmin=25,vmax=33.5,cmap='jet')
fig.colorbar(cs,ax=ax)
ax.set_title('New: uu0k with EMINUSP')

ax = fig.add_subplot(133)
cs = ax.pcolormesh(x,y,s2-s1,vmin=-1,vmax=1,cmap='bwr')
fig.colorbar(cs,ax=ax)
ax.set_title('New - Old')

fig.tight_layout()

plt.show()
pfun.end_plot