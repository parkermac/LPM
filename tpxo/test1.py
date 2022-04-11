"""
Code to experiment with tpxo9 files.
"""

import xarray as xr
import matplotlib.pyplot as plt
import cmath
import numpy as np

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun
Ldir = Lfun.Lstart()

# example cmath functions, where z is a complex number
# e.g. z = 2 + 2j
# (A, phi) = cmath.polar(z)
# A = abs(z)
# phi=cmath.phase(z)
# z = cmath.rect(A,phi)

in_dir = Ldir['data'] / 'tide' / 'tpxo9'

g_fn = in_dir / 'grid_tpxo9_atlas_30_v5.nc'
c_fn = in_dir / 'h_m2_tpxo9_atlas_30_v5.nc'

g_ds = xr.open_dataset(g_fn)
c_ds = xr.open_dataset(c_fn)

lon = g_ds.lon_z.values # 0:360
lat = g_ds.lat_z.values # -90:90

i0 = zfun.find_nearest_ind(lon, -131 + 360)
i1 = zfun.find_nearest_ind(lon, -121 + 360)
j0 = zfun.find_nearest_ind(lat, 41)
j1 = zfun.find_nearest_ind(lat, 53)

z = g_ds.hz[i0:i1, j0:j1].values
z[z==0] = np.nan
z = z.T

llon, llat = np.meshgrid(lon[i0:i1], lat[j0:j1])
plon, plat = pfun.get_plon_plat(llon, llat)
plon = plon - 360

plt.close('all')
pfun.start_plot(figsize=(10,10))

fig = plt.figure()
ax = fig.add_subplot(111)

cs = ax.pcolormesh(plon, plat, z)
pfun.dar(ax)

plt.show()
pfun.end_plot()
