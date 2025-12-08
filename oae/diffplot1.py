"""
Plot differences for the ARPAe OAE experiments
that Aurora did in December 2025.

Like diffplot1 but formatting the figure per Kyle Hinson's
instructions.

"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

f_string2 = 'f2013.07.07'
his_name2 = 'ocean_his_0002.nc'
vn = 'TIC'

Ldir = Lfun.Lstart()
"""
BASELINE:
NO cas7_t1_x11ab
NO cas7_t1noDIN_x11ab
NOcas7_t1noDIN160_x11ab
YES! cas7_t1jxNOoae_x11bjx

OAE:
cas7_t1jxoae_x11bjx standard fennel code
cas7_t1jxoae_x11ecb old pnnl module
cas7_t1jxoae_x11ecbnew new pnnl module
"""
fn1 = Ldir['roms_out'] / 'cas7_t1jxoae_x11bjx' / f_string2 / his_name2
G, S, T = zrfun.get_basic_info(fn1)
x, y = pfun.get_plon_plat(G['lon_rho'],G['lat_rho'])
ds1 = xr.open_dataset(fn1)
fld1 = ds1[vn][0,-1,:,:].to_numpy()
# find limits for an ad-hoc box
Lon = G['lon_rho'][0,:]
Lat = G['lat_rho'][:,0]
ix0 = zfun.find_nearest_ind(Lon, -129)
ix1 = zfun.find_nearest_ind(Lon, -123)
iy0 = zfun.find_nearest_ind(Lat, 43)
iy1 = zfun.find_nearest_ind(Lat, 51)

z_w = zrfun.get_z(G['h'], ds1.zeta[0,:,:].to_numpy(), S, only_w=True)
dz = np.diff(z_w, axis=0)
dx = G['DX']
dy = G['DY']
dv = dx * dy * dz
nz,ny,nx = dv.shape

plt.close('all')
pfun.start_plot(figsize=(12,8))
fig = plt.figure()

# loop over two new OAE experiments
gtx_list = ['cas7_t1jxoae_x11ecb',
    'cas7_t1jxoae_x11ecbnew']

gtx_dict = {'cas7_t1jxoae_x11ecb':'No Module - Old Module',
    'cas7_t1jxoae_x11ecbnew':'No Module - New Module'}

ii = 1
N = 2
for gtx in gtx_list:
    fn2 = Ldir['roms_out'] / gtx / f_string2 / his_name2
    ds2 = xr.open_dataset(fn2)
    fld2 = ds2[vn][0,-1,:,:].to_numpy()
    fldd = fld2 - fld1

    ax = fig.add_subplot(1,N,ii)
    vv = 5
    cs = ax.pcolormesh(x,y,fldd, vmin=-vv, vmax=vv,cmap='bwr')
    #cs = ax.pcolormesh(x,y,fldd,cmap='bwr')
    fig.colorbar(cs, ax=ax)
    pfun.dar(ax)
    pfun.add_coast(ax)
    ax.axis([Lon[ix0],Lon[ix1],Lat[iy0],Lat[iy1]])
    ax.set_title(gtx_dict[gtx])
    ax.text(.05,.1,r'$\Delta$' + ' Surface TIC [mmol m-3]',transform=ax.transAxes)
    ax.text(.05,.05,gtx,transform=ax.transAxes)


    ds2.close()
    ii += 1
plt.show()
ds1.close()
