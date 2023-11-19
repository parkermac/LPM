"""
Code to explore an initial condition for LiveOcean. Focused on
the results of LO/forcing/ocn01.
"""

from lo_tools import Lfun, zfun, zrfun
from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
import matplotlib.path as mpth
import xarray as xr
import numpy as np
import pandas as pd

gridname = 'cas7'
Ldir = Lfun.Lstart(gridname=gridname)

# grid
fng = Ldir['grid'] / 'grid.nc'
dsg = xr.open_dataset(fng)
x = dsg.lon_rho.values
y = dsg.lat_rho.values
m = dsg.mask_rho.values
xp, yp = pfun.get_plon_plat(x,y)

# ocean_ini 
fn = (Ldir['LOo'] / 'forcing' / gridname /
    'f2012.10.07' / 'ocn01' / 'ocean_ini.nc')
ds = xr.open_dataset(fn)

# PLOTTING

plt.close('all')
pfun.start_plot(fs=10, figsize=(22,12))
fig = plt.figure()

vn_list = ['salt','temp','NO3','oxygen','TIC','alkalinity','phytoplankton','NH4']

ii = 1
for vn in vn_list:
    
    # map
    v = ds[vn][0,-1,:,:].values
    ax = fig.add_subplot(2,4,ii)
    cs = ax.pcolormesh(xp,yp,v)
    pfun.add_coast(ax)
    pfun.dar(ax)
    aa = [-125.5, -122, 47, 50.5]
    ax.axis(aa)
    fig.colorbar(cs, ax=ax)
    ax.set_title(vn)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    ii += 1

plt.show()