"""
A generic bathymetry plot to use for penciling out TEF sections.

"""

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
import numpy as np

Ldir = Lfun.Lstart()
fn = Ldir['roms_out'] / 'cas6_v00_uu0mb' / 'f2021.07.04' / 'ocean_his_0025.nc'
G, S, T = zrfun.get_basic_info(fn)
z = -G['h'][1:-1,1:-1]
m = G['mask_rho'][1:-1,1:-1]
z[m==0] = np.nan

plt.close('all')
pfun.start_plot(figsize=(10,13))
fig = plt.figure()

ax = fig.add_subplot(111)
ax.pcolormesh(G['lon_psi'], G['lat_psi'], z, vmin=-500, vmax=100,
    cmap='terrain', alpha=0.3)
pfun.add_coast(ax)
pfun.dar(ax)
plt.grid(True)
ax.axis([-130, -122, 42, 52])

plt.show()
