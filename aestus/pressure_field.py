"""
Code to plot the baroclinic contribution to pressure at a
chosen depth.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from time import time

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart(gridname='cas6', tag='v0', ex_name='live')

# Loop over 71 files to form a tidal average of selected fields
fn_list = Lfun.get_fn_list('hourly', Ldir, '2019.07.04', '2019.07.06')

# First get some basic info and clipping indices
G,S,T = zrfun.get_basic_info(fn_list[0])
aa = [-123.75, -122, 47, 49]
#aa = [-125, -122, 47, 50]
i0 = zfun.find_nearest_ind(G['lon_rho'][0,:], aa[0])
i1 = zfun.find_nearest_ind(G['lon_rho'][0,:], aa[1])
j0 = zfun.find_nearest_ind(G['lat_rho'][:,0], aa[2])
j1 = zfun.find_nearest_ind(G['lat_rho'][:,0], aa[3])
h = G['h'][j0:j1,i0:i1]
z_w = zrfun.get_z(h, 0*h, S, only_w=True)
dz = np.diff(z_w, axis=0)

if False:
    fn_list = fn_list[:5]
    shape = zfun.hanning_shape(n=len(fn_list))
else:
    fn_list = fn_list[1:-1] # 71 hours
    shape = zfun.godin_shape()

rho = np.zeros(dz.shape)
eta = np.zeros(h.shape)
spd = np.zeros(h.shape)
mask_u = G['mask_u'][j0+1:j1-1,i0:i1-1]
mask_v = G['mask_v'][j0:j1-1,i0+1:i1-1]
mask_rho = G['mask_rho'][j0:j1,i0:i1]
ii = 0
tt0 = time()
for fn in fn_list:
    ds = xr.open_dataset(fn)
    rho += shape[ii] * (ds.rho[0,:,j0:j1,i0:i1].values.squeeze()+1000)
    eta0 = ds.zeta[0,j0:j1,i0:i1].values.squeeze()
    eta0 -= np.nanmean(eta0)
    eta += shape[ii] * eta0
    u = ds.u[0,-1,j0+1:j1-1,i0:i1-1].values.squeeze()
    v = ds.v[0,-1,j0:j1-1,i0+1:i1-1].values.squeeze()
    u[mask_u==0] = 0
    v[mask_v==0] = 0
    uu = (u[:,1:]+u[:,:-1])/2
    vv = (v[1:,:]+v[:-1,:])/2
    spd0 = np.sqrt(uu**2 + vv**2)
    spd[1:-1,1:-1] += shape[ii] * spd0
    
    ii += 1
    

print('Took %0.2f sec to average %d hours' % (time()-tt0, len(fn_list)))

# find pressure on selected z-level "zlev"
tt0 = time()
g = 9.8
p = np.cumsum(g * rho[::-1,:,:] * dz[::-1,:,:], axis=0)[::-1,:,:]
M, L = h.shape
p0 = np.zeros((1,M,L))
pf = np.concatenate((p,p0), axis=0)
zlev = -40
P = pfun.get_layer(pf, z_w, zlev)
P = P - np.nanmean(P)
print('Took %0.2f sec to get P layer' % (time()-tt0))

# find the equivalent pressure due to the free surface
eta = eta - np.nanmean(eta)
rho0 = 1025
spd[mask_rho==0] = np.nan
Pfs = (g * rho0 * eta) + (rho0 * spd*spd)/2
Pfs -= np.nanmean(Pfs)

lon = G['lon_rho'][j0:j1,i0:i1]
lat = G['lat_rho'][j0:j1,i0:i1]
plon, plat = pfun.get_plon_plat(lon,lat)

# plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(13,8))

vmin = -500
vmax = 500

ax = fig.add_subplot(121)
cs = ax.pcolormesh(plon, plat, P, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
pfun.add_coast(ax)
ax.axis(aa)
ax.set_xticks([-123.5, -123, -122.5])
ax.set_yticks([47, 48, 49])

ax = fig.add_subplot(122)
cs = ax.pcolormesh(plon, plat, Pfs, cmap='jet', vmin=vmin, vmax=vmax)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
pfun.add_coast(ax)
ax.axis(aa)
ax.set_xticks([-123.5, -123, -122.5])
ax.set_yticks([47, 48, 49])

plt.show()
pfun.end_plot()