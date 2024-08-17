"""
Code to test layers_uv.py output.
"""

import xarray as xr
import numpy as np
from pathlib import Path

def find_nearest_ind(array, value):
    # gives the index of the item in array that is closest to value
    idx = (np.abs(array-value)).argmin()
    return int(idx)

fn = Path('/Users/parkermaccready/Documents') / 'LPM_data' / 'layers' / 'layers_hour_0000.nc'

ds = xr.open_dataset(fn)

lon = ds.lon_rho.values
lat = ds.lat_rho.values
mask = ds.mask_rho.values
x = lon[0,:]
y = lat[:,0]
z = ds.z.values

Lon = -124.23
Lat = 48.35
ix = find_nearest_ind(x,Lon)
iy = find_nearest_ind(y,Lat)

temp = ds.temp[0,:,iy,ix].values
salt = ds.salt[0,:,iy,ix].values
u = ds.ur[0,:,iy,ix].values
v = ds.vr[0,:,iy,ix].values
h = ds.h[iy,ix].values

print('\nLon = %0.2f  Lat = %0.2f  Depth = %0.2f\n' % (Lon,Lat,h))
print('%10s%10s%10s%10s%10s' % ('z','temp', 'salt', 'u', 'v'))
for ii in range(len(z)):
    print('%10.1f%10.1f%10.1f%10.1f%10.1f' % (z[ii],temp[ii],salt[ii],u[ii],v[ii]))