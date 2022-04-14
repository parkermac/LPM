"""
Code to experiment with tpxo9 files.
"""

import xarray as xr
import matplotlib.pyplot as plt
import cmath
import numpy as np
import pytide
from datetime import datetime

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

lon_vec = g_ds.lon_z.values # 0:360
lat_vec = g_ds.lat_z.values # -90:90

i0 = zfun.find_nearest_ind(lon_vec, -130 + 360)
i1 = zfun.find_nearest_ind(lon_vec, -122 + 360)
j0 = zfun.find_nearest_ind(lat_vec, 42)
j1 = zfun.find_nearest_ind(lat_vec, 52)

depth = g_ds.hz[i0:i1, j0:j1].values
depth[depth==0] = np.nan
depth = depth.T

lon, lat = np.meshgrid(lon_vec[i0:i1], lat_vec[j0:j1])
lon = lon - 360 # improve algorithm?
plon, plat = pfun.get_plon_plat(lon, lat)

# contituent fields: info from c_ds.hRe.field
# amp=abs(hRe+i*hIm);GMT phase=atan2(-hIm,hRe)/pi*180
# also, just like for depth, 0 = land
# and the units are mm (int)
# and I believe the phase is relative to 1/1/1992
hRe = c_ds.hRe[i0:i1, j0:j1].values
hIm = c_ds.hIm[i0:i1, j0:j1].values

hRe = np.float64(hRe)
hRe[hRe==0] = np.nan
hRe = hRe.T

hIm = np.float64(hIm)
hIm[hIm==0] = np.nan
hIm = hIm.T

hcx = hRe + 1j*hIm
amp = abs(hcx)
phase = np.arctan2(-hIm,hRe) # -pi:pi

# for comparison I will also load a ROMS forcing file
r_fn = Ldir['LOo'] / 'forcing' / 'cas6_v0' / 'f2019.07.04' / 'tide1' / 'tides.nc'
r_ds = xr.open_dataset(r_fn)
amp_r = r_ds.tide_Eamp[0,:,:].values
phase_r = r_ds.tide_Ephase[0,:,:].values

rg_fn = Ldir['data'] / 'grids' / 'cas6' / 'grid.nc'
rg_ds = xr.open_dataset(rg_fn)
lon_r = rg_ds.lon_rho.values
lat_r = rg_ds.lat_rho.values
mask_r = rg_ds.mask_rho.values
plon_r, plat_r = pfun.get_plon_plat(lon_r, lat_r)

amp_r[mask_r==0] = np.nan
phase_r[mask_r==0] = np.nan

wt = pytide.WaveTable(['M2'])
dt = datetime(1992,1,1)
f, vu = wt.compute_nodal_modulations([dt])

f = f[0][0]
vu = vu[0][0]

# add Greenwich phase and nodal modulation
#phase = phase - 1.7316
phase = phase - vu

# wrap phase to ensure it is in -pi to pi
phase = np.angle(np.exp(1j*phase))

# convert to degrees
phase = 180 * phase / np.pi

amp = f * amp / 1000

amp_adj = 1.17 * 1.075 * amp # apply adjustment used in tide1

plt.close('all')
pfun.start_plot(figsize=(20, 12))

fig = plt.figure()

ax = fig.add_subplot(231)
cs = ax.pcolormesh(plon, plat, amp, vmin=0, vmax=2, cmap='jet')
fig.colorbar(cs)
pfun.dar(ax)
ax.set_title('TPXO9 Amplitude [m]')

ax = fig.add_subplot(232)
cs = ax.pcolormesh(plon_r, plat_r, amp_r, vmin=0, vmax=2, cmap='jet')
fig.colorbar(cs)
pfun.dar(ax)
ax.set_title('tide1 Amplitude [m]')

ax = fig.add_subplot(233)
ax.plot(amp[:,0], lat[:,0], '-r', label='TPXO9')
ax.plot(amp_adj[:,0], lat[:,0], '--r', label='TPXO9 adjusted')
ax.plot(amp_r[:,0], lat_r[:,0], '-b', label='tide1')
ax.legend()
ax.set_ylim(42, 52)
ax.grid(True)
ax.set_title('Amplitude at West [m]')

ax = fig.add_subplot(234)
cs = ax.pcolormesh(plon, plat, phase, vmin=-180, vmax=180, cmap='bwr')
fig.colorbar(cs)
pfun.dar(ax)
ax.set_title('TPXO9 Phase [deg]')
ax.contour(lon, lat, phase, np.arange(-180, 190, 10))

ax = fig.add_subplot(235)
cs = ax.pcolormesh(plon_r, plat_r, phase_r, vmin=-180, vmax=180, cmap='bwr')
fig.colorbar(cs)
pfun.dar(ax)
ax.set_title('tide1 Phase [deg]')
ax.contour(lon_r, lat_r, phase_r, np.arange(-180, 190, 10))

ax = fig.add_subplot(236)
ax.plot(phase[:,0], lat[:,0], '-r', label='TPXO9')
ax.plot(phase_r[:,0], lat_r[:,0], '-b', label='tide1')
ax.legend()
ax.set_ylim(42, 52)
ax.grid(True)
ax.set_title('Phase at West [deg]')

plt.show()
pfun.end_plot()
