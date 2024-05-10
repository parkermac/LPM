"""
Code to plot benthic flux.
"""

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

Ldir = Lfun.Lstart()

in_dir = Ldir['roms_out'] / 'cas7_t0_x4b' / 'f2017.07.04'
# in_dir = Ldir['roms_out'] / 'cas7_t0_x4b' / 'f2013.01.03'
fn = in_dir / 'lowpassed.nc'
ds = xr.open_dataset(fn)

x, y = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)

Wsmall = 8 # [m/d]
Wlarge = 80 # [m/d]

# Flux units are [mmol N m-2 d-1]
Fsmall = ds.SdetritusN[0,0,:,:].values * Wsmall
Flarge = ds.LdetritusN[0,0,:,:].values * Wlarge
F = Fsmall + Flarge
Denit = np.zeros(F.shape)
Denit[F>1.2] = 1.2
Denit[ds.mask_rho.values == 0] = np.nan

plt.close('all')
pfun.start_plot(figsize=(14,8))
fig, axes = plt.subplots(nrows=1,ncols=3,squeeze=False)

aa = [-126, -122, 47, 51]
vmax = 10

ax = axes[0,0]
cs = ax.pcolormesh(x, y, Fsmall, vmin=0, vmax=vmax, cmap='jet')
fig.colorbar(cs, ax=ax, location='bottom', orientation='horizontal')
pfun.dar(ax)
ax.set_title('SDet Flux [mmol N m-2 d-1]')
ax.axis(aa)
ax.set_yticks([48,49])
ax.set_xticks([-124,-123])

ax = axes[0,1]
cs = ax.pcolormesh(x, y, Flarge, vmin=0, vmax=vmax, cmap='jet')
fig.colorbar(cs, ax=ax, location='bottom', orientation='horizontal')
pfun.dar(ax)
ax.set_title('LDet Flux [mmol N m-2 d-1]')
ax.axis(aa)
ax.set_xticks([-124,-123])
ax.set_yticklabels([])

ax = axes[0,2]
cs = ax.pcolormesh(x, y, Denit, vmin=0, vmax=vmax, cmap='jet')
fig.colorbar(cs, ax=ax, location='bottom', orientation='horizontal')
pfun.dar(ax)
ax.set_title('Denit [mmol N m-2 d-1]')
ax.axis(aa)
ax.set_xticks([-124,-123])
ax.set_yticklabels([])

plt.show()
