"""
Code to start exploring National Water Model output.

This just plots locations of a couple of rivers, to see where their reported positions
are on a map.
"""

import xarray as xr
from pathlib import Path
from lo_tools import Lfun
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

fn = Ldir['data'] / 'river' / 'NWM' / 'nwm.t00z.medium_range.channel_rt_1.f001.conus.nc'
# I believe the f### corresponds to a forecast hour, so 238 would be near the end of the 10-day
# extent of the medium-range forecast

rds = xr.open_dataset(fn)

# Goldsborough Creek
g_fid = 23989319
g_lon = -123.0964
g_lat = 47.2090
g = rds.sel(feature_id=g_fid)

# Kennedy Creek
k_fid = 23989355
k_lon = -123.1091
k_lat = 47.0874
k = rds.sel(feature_id=k_fid)

# PLOTTING
hfn = Ldir['roms_out'] / 'so0_v0_n0k' / 'f2018.01.10' / 'ocean_his_0001.nc'
ds = xr.open_dataset(hfn)
salt = ds.salt[0,-1,:,:].values
plon, plat = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)

plt.close('all')
fig = plt.figure(figsize=(10,10))

ax = fig.add_subplot(111)
ax.pcolormesh(plon, plat, salt, cmap='jet', vmin=28.0, vmax=30.5)
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis(pfun.get_aa(ds))

ax.plot(g_lon,g_lat, '*y', markersize=8, mec='k')
ax.plot(k_lon,k_lat, '*c', markersize=8, mec='k')

plt.show()
