"""
Code to explore the extracted hycom fields.  The specific goal is
to see if there are obvous artifacts of data assimilation that might
contaminate bottom pressure analysis that I am doing for the MG&G folks.

This one makes a map to help get started.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lo_tools import zfun, Lfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

hdir0 = Ldir['data'] / 'hycom'

hy = 'hy6'

hdir = hdir0 / hy

fn_list = list(hdir.glob('*.nc'))
fn_list.sort()

fn = fn_list[0]

ds = xr.open_dataset(fn)

lon = ds.lon.values - 360 # convert from 0:360 to -360:0 format
lat = ds.lat.values
Lon, Lat = np.meshgrid(lon, lat)
x, y = pfun.get_plon_plat(Lon, Lat)

depth = ds.depth.values

V = dict()
V['ssh'] = ds.surf_el[0, :, :].values
V['salt'] = ds.salinity[0, 0, :, :].values
V['temp'] = ds.water_temp[0, 0, :, :].values
V['u'] = ds.water_u[0, 0, :, :].values
V['v'] = ds.water_v[0, 0, :, :].values

# note that fields are packed bottom to top, and that
# water_temp is in-situ temperature, not potential temperature.

# plotting
plt.close('all')
pfun.start_plot(figsize=(25,7))

fig, axes = plt.subplots(nrows=1, ncols=len(V.keys()), squeeze=False)

ii = 0
for vn in V.keys():
    ax = axes[0,ii]
    cs = ax.pcolormesh(x, y, V[vn], cmap='jet')
    fig.colorbar(cs, ax=ax)
    pfun.dar(ax)
    pfun.add_coast(ax)
    ax.set_title(vn)
    ii += 1

plt.show()
pfun.end_plot()
