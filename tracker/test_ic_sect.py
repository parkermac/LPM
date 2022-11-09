"""
Testing the code to seed tracker particles along a section
"""

import numpy as np
from lo_tools import Lfun, zfun, zrfun
import xarray as xar
from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
from cmocean import cm

Ldir = Lfun.Lstart()

# inputs to function in experiments.py
fn00 = Ldir['roms_out'] / 'cas6_v00_uu0mb' / 'f2021.07.04' / 'ocean_his_0002.nc'
lons = [-122.808, -122.584]
lats = [48.083,   48.083]
NPmax=10000

G = zrfun.get_basic_info(fn00, only_G=True)
h = G['h']
m = G['mask_rho']
xr = G['lon_rho']
yr = G['lat_rho']
X = xr[0,:]
Y = yr[:,0]

lon0 = lons[0]; lon1 = lons[1]
lat0 = lats[0]; lat1 = lats[1]

ix0 = zfun.find_nearest_ind(X, lon0)
ix1 = zfun.find_nearest_ind(X, lon1)
iy0 = zfun.find_nearest_ind(Y, lat0)
iy1 = zfun.find_nearest_ind(Y, lat1)

# adjust indices to make it perfectly zonal or meridional
dix = np.abs(ix1 - ix0)
diy = np.abs(iy1 - iy0)
if dix > diy: # EW section
    iy1 = iy0
elif diy > dix: # NS section
    ix1 = ix0
    
hvec = h[iy0:iy1+1, ix0:ix1+1].squeeze()
mvec = m[iy0:iy1+1, ix0:ix1+1].squeeze()
xvec = xr[iy0:iy1+1, ix0:ix1+1].squeeze()
yvec = yr[iy0:iy1+1, ix0:ix1+1].squeeze()

# add up total depth of water
hnet = 0
for ii in range(len(hvec)):
    if mvec[ii] == 1:
        hnet += hvec[ii]
p_per_meter = NPmax/hnet
        
# initialize result arrays
plon00 = np.array([]); plat00 = np.array([]); pcs00 = np.array([])
for ii in range(len(hvec)):
    if mvec[ii] == 1:
        this_h = hvec[ii]
        this_np = int(np.floor(p_per_meter * this_h))
        plon00 = np.concatenate((plon00,xvec[ii]*np.ones(this_np)))
        plat00 = np.concatenate((plat00,yvec[ii]*np.ones(this_np)))
        pcs00 = np.concatenate((pcs00,np.linspace(-1,0,this_np)))

# get grid data
ds = xar.open_dataset(fn00)
h = ds.h.values
m = ds.mask_rho.values
h[m==0] = np.nan
plon, plat = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)
aa = pfun.get_aa(ds)
ds.close

# initialize plot
plt.close('all')
fig = plt.figure(figsize=(12,12)) # external monitor size
ax = fig.add_subplot(111)
ax.pcolormesh(plon,plat,h, vmin=-30, vmax=200, cmap=cm.deep)
pfun.dar(ax)
ax.text(.05,.95,'cas6',transform=ax.transAxes,
    fontweight='bold',bbox=pfun.bbox)
ax.plot(xvec,yvec,'or')
plt.show()
        
        