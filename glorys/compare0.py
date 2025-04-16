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

Ldir = Lfun.Lstart()
dt = datetime(2025,4,15)
dstr = f_dstr = dt.strftime(Lfun.ds_fmt)

indir0 = Ldir['parent'] / 'LPM_output' / 'glorys' / ('f' + dstr)

# open the ocean_clm.nc file for this day, and create associated coordinates
fnhc = indir0 / 'ocn03' / 'ocean_clm.nc'
dshc = xr.open_dataset(fnhc)
grid_dir = Ldir['data'] / 'grids' / 'cas7'
G = zrfun.get_basic_info(grid_dir / 'grid.nc', only_G=True)
S_info_dict = Lfun.csv_to_dict(grid_dir / 'S_COORDINATE_INFO.csv')
S = zrfun.get_S(S_info_dict)
zr = zrfun.get_z(G['h'], 0*G['h'], S, only_rho=True)

vn_list = ['salt','temp']
vn_dict = {'salt':'so', 'temp':'thetao'}
x = -125
y = 47
iih = zfun.find_nearest_ind(G['lon_rho'][0,:],x)
jjh = zfun.find_nearest_ind(G['lat_rho'][:,0],y)

plt.close('all')
pfun.start_plot(figsize=(12,8))
fig = plt.figure()

ii = 1
for vn in vn_list:

    vng = vn_dict[vn]
    fng = indir0 / 'glorys' / 'Data' / ('forecast_'+vng+'.nc')
    dsg = xr.open_dataset(fng)
    iig = np.argwhere(dsg.longitude.to_numpy() == x)[0][0]
    jjg = np.argwhere(dsg.latitude.to_numpy() == y)[0][0]

    tt0 = time()
    # Interpolate glorys field to our ROMS grid.
    # start by using linear interpolation...
    from scipy.interpolate import RegularGridInterpolator
    xx = dsg.longitude.to_numpy()
    yy = dsg.latitude.to_numpy()
    zz = - dsg.depth.to_numpy()
    data = dsg[vng][0,:,:,:].to_numpy()
    interp = RegularGridInterpolator((zz,yy,xx), data,
        method='linear', bounds_error=False)
    # points in the ROMS grid
    N,M,L = zr.shape
    X = np.tile(G['lon_rho'].reshape(1,M,L),[N,1,1])
    Y = np.tile(G['lat_rho'].reshape(1,M,L),[N,1,1])
    Z = zr
    mask = G['mask_rho']==1
    Mask = np.tile(mask.reshape(1,M,L),[N,1,1])
    zyx = np.array((Z[Mask].flatten(),Y[Mask].flatten(),X[Mask].flatten())).T
    interpolated_values = interp(zyx)
    FLD = np.nan * zr
    FLD[Mask] = interpolated_values
    print('time to interpolate = %0.1f sec' % (time()-tt0))

    tt0 = time()
    # Next fill in remaining missing values using nearest neighbor.
    from scipy.spatial import cKDTree
    z2,y2,x2 = np.meshgrid(zz,yy,xx, indexing='ij')
    mask2 = ~ np.isnan(data)
    Data = data[mask2].flatten()
    zyx2 = np.array((z2[mask2].flatten(),y2[mask2].flatten(),x2[mask2].flatten())).T
    zyxT = cKDTree(zyx2)
    print('time to make tree = %0.1f sec' % (time()-tt0))
    tt0 = time()
    mask3 = np.isnan(FLD) & Mask
    zyx3 = np.array((Z[mask3],Y[mask3],X[mask3])).T
    fill_data = Data[zyxT.query(zyx3, workers=-1)[1]]
    FLD[mask3] = fill_data
    print('time to use tree = %0.1f sec' % (time()-tt0))

    # get the cast from the ocean_clm file (hycom)
    dti = pd.DatetimeIndex(dshc.salt_time)
    tth = np.argwhere(dti == dt)[0][0]
    zh = zr[:,jjh,iih]
    fld_h = dshc[vn][tth,:,jjh,iih].to_numpy()

    # check that we have filled in all the missing values
    print(np.isnan(dshc[vn][tth,:,:,:].to_numpy()).sum())
    print(np.isnan(FLD).sum())
    # these numbers should be the same

    # and get the cast from the gield made from glorys that is on the model grid
    FLD_g = FLD[:,jjh,iih]

    # and get the cast from the original glorys data
    zg = - dsg.depth.to_numpy()
    fld_g = dsg[vng][0,:,jjg,iig].to_numpy()

    # plotting
    ax = fig.add_subplot(1,len(vn_list),ii)
    ax.plot(fld_h,zh,'-or')
    ax.plot(FLD_g,zh,'-og')
    ax.plot(fld_g,zg,'-ob')
    ax.set_xlabel(vn)
    if ii == 1:
        ax.set_ylabel('Z [m]')
        ax.text(.05,.1,'HYCOM on ROMS grid',color='r',transform=ax.transAxes)
        ax.text(.05,.2,'GLORYS on ROMS grid',color='g',transform=ax.transAxes)
        ax.text(.05,.3,'Original GLORYS field',color='b',transform=ax.transAxes)
    if ii == 2:
        ax.set_yticklabels([])

    ii += 1

plt.show()
pfun.end_plot()
