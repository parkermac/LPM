"""
Plot differences.

"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun

f_string = 'f2013.07.01'
vn = 'NO3'
his_name = 'ocean_his_0001.nc'

Ldir = Lfun.Lstart()
fn1 = Ldir['roms_out'] / 'cas7_t1noDIN160_x11ab' / f_string / his_name
fn2 = Ldir['roms_out'] / 'cas7_t1jxoae_x11bjx' / f_string / his_name
ds1 = xr.open_dataset(fn1)
ds2 = xr.open_dataset(fn2)

G, S, T = zrfun.get_basic_info(fn1)

x, y = pfun.get_plon_plat(G['lon_rho'],G['lat_rho'])

fld1 = ds1[vn][0,-1,:,:].to_numpy()
fld2 = ds2[vn][0,-1,:,:].to_numpy()
fldd = fld2 - fld1

#plt.close('all')
pfun.start_plot(figsize=(8,10))
fig = plt.figure()
ax = fig.add_subplot(111)
vv = 10
cs = ax.pcolormesh(x,y,fldd, vmin=-vv, vmax=vv,cmap='bwr')
#cs = ax.pcolormesh(x,y,fldd,cmap='bwr')
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
pfun.add_coast(ax)
ax.axis([G['lon_rho'][0,0],G['lon_rho'][0,-1],G['lat_rho'][0,0],G['lat_rho'][-1,0]])
ax.set_title('Difference in ' + vn)
plt.show()

# compute efficiency
xypad = 10 # trim edges where nudging happens
z_w = zrfun.get_z(G['h'], ds1.zeta[0,:,:].to_numpy(), S, only_w=True)
dz = np.diff(z_w, axis=0)
dx = G['DX']
dy = G['DY']
dv = dx * dy * dz
nz,ny,nx = dv.shape

dalk = ds2.alkalinity[0,:,:,:].to_numpy() - ds1.alkalinity[0,:,:,:].to_numpy()
dtic = ds2.TIC[0,:,:,:].to_numpy() - ds1.TIC[0,:,:,:].to_numpy()


DALK = np.nansum(dv[:,xypad:ny-xypad+1,xypad:nx-xypad+1] * 
    dalk[:,xypad:ny-xypad+1,xypad:nx-xypad+1])
DTIC = np.nansum(dv[:,xypad:ny-xypad+1,xypad:nx-xypad+1] * 
    dtic[:,xypad:ny-xypad+1,xypad:nx-xypad+1])

eff = DTIC/DALK
print('Efficiency = %0.1f percent' % (eff*100))

ds1.close()
ds2.close()