"""
Code to compare runs to evaluate noise in runs with
biogeochemical forcing differences.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

dstr = 'f2012.10.07'

if True:
    # My runs
    gtx1 = 'cas7_t3_y11b'
    gtx2 = 'cas7_t3noWP_y11b'
    his = 'ocean_his_0025.nc'
else:
    # Aurora's runs
    gtx1 = 'cas7_newtraps00_debugx11ab_OG'
    gtx2 = 'cas7_newtraps00noWP_debugx11ab_OG'
    his = 'ocean_his_0002.nc'

fn1 = Ldir['roms_out'] / gtx1 / dstr / his
fn2 = Ldir['roms_out'] / gtx2 / dstr / his

ds1 = xr.open_dataset(fn1)
ds2 = xr.open_dataset(fn2)

G, S, T = zrfun.get_basic_info(fn1)
zr, zw = zrfun.get_z(G['h'],ds1.zeta[0,:,:].to_numpy(),S)
dz = np.diff(zw, axis=0)

vn = 'TN'

if vn == 'DIN':
    fld1 = ds1['NH4'][0,:,:,:].to_numpy() + ds1['NO3'][0,:,:,:].to_numpy()
    fld2 = ds2['NH4'][0,:,:,:].to_numpy() + ds2['NO3'][0,:,:,:].to_numpy()
if vn == 'TN':
    vvn_list = ['NO3','NH4','phytoplankton','zooplankton','LdetritusN','SdetritusN']
    ii = 0
    for vvn in vvn_list:
        if ii == 0:
            fld1 = ds1[vvn][0,:,:,:].to_numpy()
            fld2 = ds2[vvn][0,:,:,:].to_numpy()
        else:
            fld1 += ds1[vvn][0,:,:,:].to_numpy()
            fld2 += ds2[vvn][0,:,:,:].to_numpy()
        ii += 1
else:
    fld1 = ds1[vn][0,:,:,:].to_numpy()
    fld2 = ds2[vn][0,:,:,:].to_numpy()

# vertical integrals
c1 = (fld1 * dz).sum(axis=0)
c2 = (fld2 * dz).sum(axis=0)

if True:
    c1 = c1.astype('float32')
    c2 = c2.astype('float32')

dc = c1 - c2 # expect only positive differences
print('%s Max diff = %0.8f, Min diff = %0.8f' % (vn, np.nanmax(dc),np.nanmin(dc)))
net_pos = np.sum(dc[dc>=0])
net_neg = np.sum(dc[dc<0])
print('Net positive = %0.3f' % (net_pos))
print('Net negative = %0.3f' % (net_neg))

#dc = dc.astype('float32')

plt.close('all')
pfun.start_plot(figsize=(20,10))
fig = plt.figure()
aa = [-123, -122.1, 47.2, 48.2]
dcmax = np.nanmax(dc)

# Map plot
ax1 = fig.add_subplot(121)
x,y = pfun.get_plon_plat(G['lon_rho'],G['lat_rho'])
vv = 1e-3
cs = plt.pcolormesh(x,y,dc/dcmax,cmap='RdYlBu_r',vmin=-vv,vmax=vv)
fig.colorbar(cs, ax=ax1)
fig.suptitle(r'$\Delta$' + ' Normalized Vertically Integrated %s [m uM]' % (vn))
ax1.set_title('Normal color limits')
pfun.dar(ax1)
pfun.add_coast(ax1)
ax1.axis(aa)
if True:
    # Second map plot
    ax2 = fig.add_subplot(122)
    vv = 1e-18
    cs = plt.pcolormesh(x,y,dc/dcmax,cmap='RdYlBu_r',vmin=-vv,vmax=vv)
    fig.colorbar(cs, ax=ax2)
    ax2.set_title('Extreme color limits')
    pfun.dar(ax2)
    pfun.add_coast(ax2)
    ax2.axis(aa)
    plt.show()
    pfun.end_plot()

else:
    # vertical profile as some location 
    ii = 566; jj = 821 # indicies for where to look
    cc1 = fld1[:,jj,ii]
    cc2 = fld2[:,jj,ii]
    dcc = cc1-cc2
    zz = zr[:,jj,ii]
    # profile at the loading location
    II = 594; JJ = 755 # King County West Point WWTP
    CC1 = fld1[:,JJ,II]
    CC2 = fld2[:,JJ,II]
    dCC = CC1-CC2
    ZZ = zr[:,JJ,II]
    # Profile plots
    ax2 = fig.add_subplot(143)
    ax2.plot(dcc, zz, '-c')
    ax2.plot(dCC, ZZ, '-g')
    ax1.plot(G['lon_rho'][jj,ii],G['lat_rho'][jj,ii],'oc')
    ax1.plot(G['lon_rho'][JJ,II],G['lat_rho'][JJ,II],'og')
    ax2.set_title('Diff Profiles (green=WWTP, cyan=2nd)')
    ax2.set_xlabel(vn)
    ax2.set_ylabel('Z (m)')
    ax3 = fig.add_subplot(144)
    ax3.plot(dcc, zz, '-c')
    ax3.set_title('Diff Profile (2nd location)')
    ax3.set_xlabel(vn)
    ax3.set_ylabel('Z (m)')
    plt.show()
    pfun.end_plot()