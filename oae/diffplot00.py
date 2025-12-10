"""
Plot differences for my OAE experiments from December 2025.

Focusing on a single panel using my new driver_roms00oae.py method,

"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

f_string2 = 'f2013.07.31'
his_name2 = 'ocean_his_0002.nc'
vn = 'oxygen'

Ldir = Lfun.Lstart()
"""
BASELINE:
cas7_t1_x11ab

OAE:
cas7_t1_x11ab alk added using driver
"""
fn1 = Ldir['roms_out'] / 'cas7_t1_x11ab' / f_string2 / his_name2
G, S, T = zrfun.get_basic_info(fn1)
x, y = pfun.get_plon_plat(G['lon_rho'],G['lat_rho'])
ds1 = xr.open_dataset(fn1)
fld1 = ds1[vn][0,-1,:,:].to_numpy()
# find limits for an ad-hoc box
Lon = G['lon_rho'][0,:]
Lat = G['lat_rho'][:,0]
ix0 = zfun.find_nearest_ind(Lon, -130)
ix1 = zfun.find_nearest_ind(Lon, -122)
iy0 = zfun.find_nearest_ind(Lat, 42)
iy1 = zfun.find_nearest_ind(Lat, 52)

z_w = zrfun.get_z(G['h'], ds1.zeta[0,:,:].to_numpy(), S, only_w=True)
dz = np.diff(z_w, axis=0)
dx = G['DX']
dy = G['DY']
dv = dx * dy * dz
nz,ny,nx = dv.shape

plt.close('all')
pfun.start_plot(figsize=(8,10))
fig = plt.figure()

# loop over all three OAE experiments
gtx_list = ['cas7_t1_x11abc']
gtx_dict = {'cas7_t1_x11abc':'Alkalinity from driver'}

ii = 1
N = 1
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

    # compute efficiency
    dalk = ds2.alkalinity[0,:,:,:].to_numpy() - ds1.alkalinity[0,:,:,:].to_numpy()
    dtic = ds2.TIC[0,:,:,:].to_numpy() - ds1.TIC[0,:,:,:].to_numpy()
    DALK_actual = np.nansum(dv[:,iy0:iy1,ix0:ix1] * 
        dalk[:,iy0:iy1,ix0:ix1])
    DTIC = np.nansum(dv[:,iy0:iy1,ix0:ix1] * 
        dtic[:,iy0:iy1,ix0:ix1])

    eff = DTIC/DALK_actual
    print('\n' + gtx)
    print('Efficiency = %0.1f percent' % (eff*100))
    print('DTALK_actual = %0.1fe9 mmol' % (DALK_actual/1e9))
    print('DTIC = %0.1fe9 mmol' % (DTIC/1e9))

    ax.text(.05,.15,'Efficiency = %0.1f%%' % (eff*100),transform=ax.transAxes)

    ds2.close()
    ii += 1
plt.show()
ds1.close()
