"""
Code to compare glorys and hycom output.
"""

import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from time import time

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

import glorys_functions as gfun

from importlib import reload
reload(gfun)

Ldir = Lfun.Lstart()
dt = datetime(2025,4,15)
dstr = f_dstr = dt.strftime(Lfun.ds_fmt)
ot_vec = pd.DatetimeIndex([dt])

indir0 = Ldir['parent'] / 'LPM_output' / 'glorys' / ('f' + dstr)

# open the ocean_clm.nc file for this day, and create associated coordinates
fnhc = indir0 / 'ocn03' / 'ocean_clm.nc'
dshc = xr.open_dataset(fnhc)
# NOTE: when I create the ocan _clm fields from hycom I don't include
# coordinates, which is a pain when you want to look at them. I will not
# make this mistake when processing the glorys fields.

G, S = gfun.create_roms_grid_info('cas7')

# variables to look at
# vn_list = ['salt','temp','u','v','zeta']
vn_list = ['salt','temp','u','v']

# dict to relate the roms variables to the glorys variables
vn_dict = {'salt':'so', 'temp':'thetao', 'u':'uo', 'v':'vo', 'zeta':'zos'}

# create an ocean_clm-like file for this time using glorys fields

ds = xr.Dataset()

for vn in vn_list:
    vng = vn_dict[vn]

    print('Getting %s from %s' % (vn, vng))

    if vng in ['so','thetao','zos']:
        fng = indir0 / 'glorys' / 'Data' / ('forecast_'+vng+'.nc')
    elif vng in ['uo','vo']:
        fng = indir0 / 'glorys' / 'Data' / 'forecast_cur.nc'

    if vn in ['salt', 'temp', 'zeta']:
        gtag = 'rho'
    elif vn == 'u':
        gtag = 'u'
    elif vn == 'v':
        gtag = 'v'

    if vn == 'zeta':
        do_2d = True
    else:
        do_2d = False

    if do_2d == True:
        FLD = interpolate_glorys_to_roms_2d(fng, vn, vng, gtag, G, verbose=True)
    else:
        zr = gfun.get_zr(G, S, vn)
        FLD = gfun.interpolate_glorys_to_roms(fng, vn, vng, gtag, zr, G, verbose=True)

    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    tname = vinfo['time_name']
    dims = (vinfo['time_name'],) + vinfo['space_dims_tup']
    ds[vn] = (dims, FLD[None,:])
    ds[vn].attrs['units'] = vinfo['units']
    ds[vn].attrs['long_name'] = vinfo['long_name']
    # time coordinate
    ds[tname] = ((tname,), ot_vec)
    ds[tname].attrs['units'] = Lfun.roms_time_units

# add spatial coordinates
for gtag in ['rho','u','v']:
    ds.coords['lon_'+gtag] = (('eta_'+gtag, 'xi_'+gtag), G['lon_'+gtag])
    ds.coords['lat_'+gtag] = (('eta_'+gtag, 'xi_'+gtag), G['lat_'+gtag])
# add depth and z_rho
ds['h'] = (('eta_rho', 'xi_rho'), G['h'])
ds['z_rho'] = (('s_rho','eta_rho', 'xi_rho'), gfun.get_zr(G, S, 'salt'))

# # location for a cast-like comparison
# x = -129.5
# y = 47

# # indices of the cast location in the roms grid
# # (the "r" indicates this is associated with the roms grid)
# iir = zfun.find_nearest_ind(G['lon_rho'][0,:],x)
# jjr = zfun.find_nearest_ind(G['lat_rho'][:,0],y)

# plt.close('all')
# pfun.start_plot(figsize=(12,8))
# fig = plt.figure()

# ii = 1
# for vn in vn_list:
#     print('\nvn = %s' % (vn))

#     # open the raw glorys field and find indices for the cast
#     vng = vn_dict[vn]
#     fng = indir0 / 'glorys' / 'Data' / ('forecast_'+vng+'.nc')
#     dsg = xr.open_dataset(fng)
#     iig = np.argwhere(dsg.longitude.to_numpy() == x)[0][0]
#     jjg = np.argwhere(dsg.latitude.to_numpy() == y)[0][0]

#     tt0 = time()
#     # Interpolate glorys field to our ROMS grid.
#     # start by using linear interpolation...
#     from scipy.interpolate import RegularGridInterpolator
#     xx = dsg.longitude.to_numpy()
#     yy = dsg.latitude.to_numpy()
#     zz = - dsg.depth.to_numpy()
#     data = dsg[vng][0,:,:,:].to_numpy()
#     interp = RegularGridInterpolator((zz,yy,xx), data,
#         method='linear', bounds_error=False)
#     # points in the ROMS grid
#     N,M,L = zr.shape
#     X = np.tile(G['lon_rho'].reshape(1,M,L),[N,1,1])
#     Y = np.tile(G['lat_rho'].reshape(1,M,L),[N,1,1])
#     Z = zr
#     mask = G['mask_rho']==1
#     Mask = np.tile(mask.reshape(1,M,L),[N,1,1])
#     zyx = np.array((Z[Mask].flatten(),Y[Mask].flatten(),X[Mask].flatten())).T
#     interpolated_values = interp(zyx)
#     FLD = np.nan * zr
#     FLD[Mask] = interpolated_values
#     print('- time to interpolate = %0.1f sec' % (time()-tt0))

#     if True:
#         tt0 = time()
#         # Next fill in remaining missing values using nearest neighbor.
#         from scipy.spatial import cKDTree
#         z2,y2,x2 = np.meshgrid(zz,yy,xx, indexing='ij')
#         mask2 = ~ np.isnan(data)
#         Data = data[mask2].flatten()
#         zyx2 = np.array((z2[mask2].flatten(),y2[mask2].flatten(),x2[mask2].flatten())).T
#         zyxT = cKDTree(zyx2)
#         print('- time to make tree = %0.1f sec' % (time()-tt0))
#         tt0 = time()
#         mask3 = np.isnan(FLD) & Mask
#         zyx3 = np.array((Z[mask3].flatten(),Y[mask3].flatten(),X[mask3].flatten())).T
#         fill_data = Data[zyxT.query(zyx3, workers=-1)[1]]
#         FLD[mask3] = fill_data
#         print('- time to use tree = %0.1f sec' % (time()-tt0))
#         # RESULT: Using the tree is the slowest part, 8 sec per 3-D field on my mac.

#     # get the cast from the ocean_clm file (the "h" is for hycom)
#     dti = pd.DatetimeIndex(dshc.salt_time)
#     ttr = np.argwhere(dti == dt)[0][0]
#     zh = zr[:,jjr,iir]
#     fld_h = dshc[vn][ttr,:,jjr,iir].to_numpy()

#     # Check that we have filled in all the missing values
#     nans_orig = np.isnan(dshc[vn][ttr,:,:,:].to_numpy()).sum()
#     nans_new = np.isnan(FLD).sum()
#     if nans_orig != nans_new:
#         print('WARNING: inconsistent number of nans in new field')
#         print('- orig = %d' % (np.isnan(dshc[vn][ttr,:,:,:].to_numpy()).sum()))
#         print('- new = %d' % (np.isnan(FLD).sum()))
#     # these numbers should be the same

#     # and get the cast from the gield made from glorys that is on the model grid
#     FLD_g = FLD[:,jjr,iir]

#     # and get the cast from the original glorys data
#     zg = - dsg.depth.to_numpy()
#     fld_g = dsg[vng][0,:,jjg,iig].to_numpy()

#     # plotting
#     ax = fig.add_subplot(1,len(vn_list),ii)
#     ax.plot(fld_h,zh,'-or')
#     ax.plot(FLD_g,zh,'-og')
#     ax.plot(fld_g,zg,'-b')
#     ax.set_xlabel(vn)
#     if ii == 1:
#         ax.set_ylabel('Z [m]')
#         ax.text(.05,.1,'HYCOM on ROMS grid',color='r',transform=ax.transAxes)
#         ax.text(.05,.2,'GLORYS on ROMS grid',color='g',transform=ax.transAxes)
#         ax.text(.05,.3,'Original GLORYS field',color='b',transform=ax.transAxes)
#     if ii == 2:
#         ax.set_yticklabels([])

#     ii += 1

# plt.show()
# pfun.end_plot()
