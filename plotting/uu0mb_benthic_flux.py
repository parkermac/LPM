"""
Code to plot uu0mb benthic flux.
"""

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

Ldir = Lfun.Lstart()

in_dir = Ldir['parent'] / 'LPM_data' / 'f2021.02.15'
fn = in_dir / 'ocean_his_0025_uu0mb.nc'
ds = xr.open_dataset(fn)

x, y = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)

Wsmall = 8 # [m/d]
Wlarge = 80 # [m/d]

# Flux units are [mmol N m-2 d-1]
Fsmall = ds.SdetritusN[0,0,:,:].values * Wsmall
Flarge = ds.LdetritusN[0,0,:,:].values * Wlarge
Denit = (Fsmall + Flarge) * (0.3 * 5.9)

plt.close('all')
pfun.start_plot(figsize=(20,8))
fig, axes = plt.subplots(nrows=1,ncols=3,squeeze=False)

vmax = 5
ax = axes[0,0]
cs = ax.pcolormesh(x, y, Fsmall, vmin=0, vmax=vmax, cmap='jet')
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('SDet Flux [mmol N m-2 d-1]')

ax = axes[0,1]
cs = ax.pcolormesh(x, y, Flarge, vmin=0, vmax=vmax, cmap='jet')
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('LDet Flux [mmol N m-2 d-1]')

ax = axes[0,2]
cs = ax.pcolormesh(x, y, Denit, vmin=0, vmax=20, cmap='jet')
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_title('Denit [mmol N m-2 d-1]')

plt.show()
