"""
Code to plot the work required to mix the top H m of a model field.
Essentially Simpson's phi for a limted depth.

Result is a map with units [J m-2]
"""

import gsw
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zrfun

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

# Integrate over depth H
H = 30
mask = zr < -H
zr[mask] = 0
dz[mask] = 0
rho[mask] = 0

# thickness
hh = dz.sum(axis=0)

# vertically averaged density
rho_bar = (rho*dz).sum(axis=0) / hh
Rho_bar = rho_bar.reshape((1,M,L)) * np.ones((N,1,1))

# Delta PE_a calculation
g = 9.8 # gravity [m s-2]
dPE = (g * zr * dz * (Rho_bar - rho)).sum(axis=0)

# plotting
plt.close('all')
pfun.start_plot(figsize=(8,8))
fig = plt.figure()

ax = fig.add_subplot(111)
plon, plat = pfun.get_plon_plat(lon,lat)
cs = plt.pcolormesh(plon,plat,dPE,vmin=0,vmax=1e4,cmap='rainbow')
fig.colorbar(cs, ax=ax)

ax.axis([-124, -122, 47, 50])
pfun.dar(ax)
pfun.add_coast(ax)

plt.show()
pfun.end_plot()
