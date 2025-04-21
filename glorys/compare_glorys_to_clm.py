"""
Code to interpolate a raw glorys extraction to a roms grid.
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
Ldir = Lfun.Lstart()

# set some parameters for the comparison, including where to find the
# ocean forcing we made from hycom
gridname = 'cas7'
run_type = 'backfill'
if run_type == 'forecast':
    dt = datetime(2025,4,15)
    dstr = dt.strftime(Lfun.ds_fmt)
    hc_fn = Ldir['LOo'] / 'forcing' / gridname / ('f' + dstr) / 'ocn03' / 'ocean_clm.nc'
elif run_type == 'backfill':
    dt = datetime(2018,4,15)
    dstr = dt.strftime(Lfun.ds_fmt)
    hc_fn = Ldir['LOo'] / 'forcing' / gridname / ('f' + dstr) / 'ocn01' / 'ocean_clm.nc'
# open the ocean_clm.nc file for this day, and create associated coordinates
dshc = xr.open_dataset(hc_fn)
# NOTE: when I create the ocan _clm fields from hycom I don't include
# coordinates, which is a pain when you want to look at them. I will not
# make this mistake when processing the glorys fields.
G, S = gfun.create_roms_grid_info(gridname)
ot_vec = pd.DatetimeIndex([dt])

# open the glorys_clm.nc file
indir0 = Ldir['parent'] / 'LPM_output' / 'glorys' / ('f' + dstr)
gc_fn = indir0 / 'glorys_clm.nc'
dsgc = xr.open_dataset(gc_fn)

# variables to look at
vn_list = ['salt','temp','u','v']

# dict to relate the roms variables to the glorys variables
vn_dict = {'salt':'so', 'temp':'thetao', 'u':'uo', 'v':'vo', 'zeta':'zos'}

# location for a cast-like comparison
x = -129
y = 47

# indices of the cast location in the roms grid
# (the "r" indicates this is associated with the roms grid)
iir = zfun.find_nearest_ind(G['lon_rho'][0,:],x)
jjr = zfun.find_nearest_ind(G['lat_rho'][:,0],y)

plt.close('all')
pfun.start_plot(figsize=(12,10))
fig = plt.figure()

ii = 1
for vn in vn_list:

    # open the raw glorys field and find indices for the cast
    vng = vn_dict[vn]
    if run_type == 'forecast':
        if vng in ['uo','vo']:
            fng = indir0 / 'glorys' / 'Data' / ('forecast_cur.nc')
        else:
            fng = indir0 / 'glorys' / 'Data' / ('forecast_'+vng+'.nc')
    elif run_type== 'backfill':
        fng = Ldir['parent'] / 'LPM_output' / 'glorys_archive' / ('hindcast_'+dstr+'.nc')
    dsg = xr.open_dataset(fng)
    iig = np.argwhere(dsg.longitude.to_numpy() == x)[0][0]
    jjg = np.argwhere(dsg.latitude.to_numpy() == y)[0][0]

    # get the cast from the ocean_clm file (the "h" is for hycom)
    dti = pd.DatetimeIndex(dshc.salt_time)
    ttr = np.argwhere(dti == dt)[0][0]
    zh = dsgc.z_rho[:,jjr,iir]
    fld_h = dshc[vn][ttr,:,jjr,iir].to_numpy()

    # and get the cast from the gield made from glorys that is on the model grid
    FLD_g = dsgc[vn][:,jjr,iir].to_numpy()

    # and get the cast from the original glorys data
    zg = - dsg.depth.to_numpy()
    fld_g = dsg[vng][0,:,jjg,iig].to_numpy()

    # plotting
    ax = fig.add_subplot(2,2,ii)
    ax.plot(fld_h,zh,'-or')
    ax.plot(FLD_g,zh,'-og')
    ax.plot(fld_g,zg,'-b')
    ax.text(.9,.9,vn,fontweight='bold',fontsize=24,
        transform=ax.transAxes,bbox=pfun.bbox,ha='right')
    if ii == 1:
        ax.set_ylabel('Z [m]')
        ax.text(.05,.1,'HYCOM on ROMS grid',color='r',transform=ax.transAxes)
        ax.text(.05,.2,'GLORYS on ROMS grid',color='g',transform=ax.transAxes)
        ax.text(.05,.3,'Original GLORYS field',color='b',transform=ax.transAxes)
    if ii in [2,4]:
        ax.set_yticklabels([])

    ii += 1
    fig.suptitle(dstr)

plt.show()
pfun.end_plot()
