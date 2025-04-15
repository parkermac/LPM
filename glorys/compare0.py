"""
Code to compare glorys and hycom output.
"""

import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

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
x = -128
y = 46
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

    dti = pd.DatetimeIndex(dshc.salt_time)
    tth = np.argwhere(dti == dt)[0][0]

    zh = zr[:,jjh,iih]
    zg = - dsg.depth.to_numpy()

    fld_h = dshc[vn][tth,:,jjh,iih].to_numpy()
    fld_g = dsg[vng][0,:,jjg,iig].to_numpy()

    ax = fig.add_subplot(1,len(vn_list),ii)
    ax.plot(fld_h,zh,'-or')
    ax.plot(fld_g,zg,'-ob')
    ax.set_xlabel(vn)
    if ii == 1:
        ax.set_ylabel('Z [m]')
    if ii == 2:
        ax.set_yticklabels([])

    ii += 1

plt.show()
pfun.end_plot()
