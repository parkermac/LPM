"""
Stand-alone code to plot a layers extraction.

As an example for Troy and Alex.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

plt.close('all')

# You will need to adjust the path.
ds = xr.open_dataset('/Users/parkermaccready/Documents/LPM_data/layers/layers.nc')

# get a layer to plot, and the coordinates
temp = ds.temp_surface[0,:,:].values
lon = ds.lon_rho.values
lat = ds.lat_rho.values

# lon and lat are arrays at the centers of the grid cells, but to use pcolormesh
# we want to generate a grid at the corners of the grid cells. We call this plon, plat.
Lon = lon[0,:]
Lat = lat[:,0]
if (Lon - lon[-1,:]).sum() != 0:
    print('Error from get_plon_plat: lon grid not plaid')
    sys.exit()
if (Lat - lat[:,-1]).sum() != 0:
    print('Error from get_plon_plat: lat grid not plaid')
    sys.exit()
plon = np.ones(len(Lon) + 1)
plat = np.ones(len(Lat) + 1)
dx2 = np.diff(Lon)/2
dy2 = np.diff(Lat)/2
Plon = np.concatenate(((Lon[0]-dx2[0]).reshape((1,)), Lon[:-1]+dx2, (Lon[-1]+dx2[-1]).reshape((1,))))
Plat = np.concatenate(((Lat[0]-dy2[0]).reshape((1,)), Lat[:-1]+dy2, (Lat[-1]+dy2[-1]).reshape((1,))))
plon, plat = np.meshgrid(Plon, Plat)

# plot the field
fig = plt.figure(figsize=(8,12))
ax = fig.add_subplot(111)
cs = ax.pcolormesh(plon,plat,temp, vmin=6, vmax=14)
fig.colorbar(cs, ax=ax)

# and adjust the aspect ratio
yl = ax.get_ylim()
yav = (yl[0] + yl[1])/2
ax.set_aspect(1/np.cos(np.pi*yav/180))

plt.show()