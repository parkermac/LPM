"""
Code to plot the work required to mix the top H m of a model field.
Essentially Simpson's phi for a limted depth.

We also calculate the met mixing rate in approximately the same layer,
and present the ratio as a timescale.

Result is maps with units [J m-2] and [days]
"""

import gsw
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zrfun
from cmocean import cm

Ldir = Lfun.Lstart()
fn = Ldir['roms_out'] / 'cas6_traps2_x2b' / 'f2017.07.04' / 'ocean_his_0002.nc'

G, S, T = zrfun.get_basic_info(fn)
h = G['h']
lon = G['lon_rho']
lat = G['lat_rho']
ds = xr.open_dataset(fn)

zr, zw = zrfun.get_z(h, 0*h, S)
dz = np.diff(zw, axis=0)

salt = ds.salt.values.squeeze()
temp = ds.temp.values.squeeze()
N, M, L = salt.shape

pres = gsw.p_from_z(zr, lat) # pressure [dbar]
SA = gsw.SA_from_SP(salt, pres, lon, lat)
CT = gsw.CT_from_pt(SA, temp)
rho = gsw.rho(SA, CT, 0) # potential density
drho = np.diff(rho, axis=0) # for buoyancy flux

# Integrate over depth H
H = 30
mask = zr < -H
zr[mask] = 0
dz[mask] = 0
rho[mask] = 0

# thickness
hh = dz.sum(axis=0)

# vertically averaged density
rho_bar = np.sum(rho*dz, axis=0) / hh
Rho_bar = rho_bar.reshape((1,M,L)) * np.ones((N,1,1))
Rho_bar[mask] = 0

# Delta PE_a calculation
g = 9.8 # gravity [m s-2]
dPE = np.sum(g * zr * dz * (Rho_bar - rho), axis=0) # Energy to mix [J m-2]

# Mixing rate (integrated buoyancy flux)
K = ds.AKs[0,1:-1,:,:].values.squeeze()
mask_w = zw[1:-1,:,:] < -H
K[mask_w] = 0
drho[mask_w] = 0
F = - np.sum(g * K * drho, axis=0) # Vertically integrated buoyancy flux [W m-2]

ds.close()

Tmix = dPE / (F * 86400) # Mixing time [days]

# plotting
plt.close('all')
pfun.start_plot(figsize=(16,10))
fig = plt.figure()

aa = [-124.5, -122, 47, 50]
# aa = pfun.get_aa(ds)

ax = fig.add_subplot(121)
plon, plat = pfun.get_plon_plat(lon,lat)
cs = plt.pcolormesh(plon,plat,dPE,cmap=cm.matter,vmin=0,vmax=5e3)
fig.colorbar(cs, ax=ax)
ax.axis(aa)
pfun.dar(ax)
pfun.add_coast(ax)
ax.set_title('Energy to mix top %d m [J m-2]' % (H))
pfun.add_info(ax, fn, fs=12, loc='lower_right', his_num=False)

ax = fig.add_subplot(122)
plon, plat = pfun.get_plon_plat(lon,lat)
cs = plt.pcolormesh(plon,plat,Tmix,cmap=cm.tempo,vmin=0,vmax=50)
fig.colorbar(cs, ax=ax)
ax.axis(aa)
pfun.dar(ax)
pfun.add_coast(ax)
ax.set_title('Time to mix top %d m [days]' % (H))

plt.show()
pfun.end_plot()
