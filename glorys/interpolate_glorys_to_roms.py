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

from importlib import reload
reload(gfun)

Ldir = Lfun.Lstart()

gridname = 'cas7'
run_type = 'backfill'
if run_type == 'forecast':
    dt = datetime(2025,4,15)
elif run_type == 'backfill':
    dt = datetime(2018,4,15)
dstr = dt.strftime(Lfun.ds_fmt)

indir0 = Ldir['parent'] / 'LPM_output' / 'glorys' / ('f' + dstr)
Lfun.make_dir(indir0)

G, S = gfun.create_roms_grid_info('cas7')

# variables to look at
vn_list = ['salt','temp','u','v','zeta']
# vn_list = ['salt','temp','u','v']
# vn_list = ['salt', 'zeta']

# dict to relate the roms variables to the glorys variables
vn_dict = {'salt':'so', 'temp':'thetao', 'u':'uo', 'v':'vo', 'zeta':'zos'}

# create an ocean_clm-like file for this time using glorys fields

ds = xr.Dataset()

for vn in vn_list:
    vng = vn_dict[vn]

    print('Getting %s from %s' % (vn, vng))

    if run_type == 'forecast':
        if vng in ['so','thetao','zos']:
            fng = indir0 / 'glorys' / 'Data' / ('forecast_'+vng+'.nc')
        elif vng in ['uo','vo']:
            fng = indir0 / 'glorys' / 'Data' / 'forecast_cur.nc'
    elif run_type == 'backfill':
        fng = Ldir['parent'] / 'LPM_output' / 'glorys_archive' / ('hindcast_'+dstr+'.nc')

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
        FLD = gfun.interpolate_glorys_to_roms_2d(fng, vn, vng, gtag, G, verbose=True)
    else:
        zr = gfun.get_zr(G, S, vn)
        FLD = gfun.interpolate_glorys_to_roms(fng, vn, vng, gtag, zr, G, verbose=True)

    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = vinfo['space_dims_tup']
    ds[vn] = (dims, FLD)
    ds[vn].attrs['units'] = vinfo['units']
    ds[vn].attrs['long_name'] = vinfo['long_name']

    # I am skipping adding a time coordinate.

# add spatial coordinates
for gtag in ['rho','u','v']:
    ds.coords['lon_'+gtag] = (('eta_'+gtag, 'xi_'+gtag), G['lon_'+gtag])
    ds.coords['lat_'+gtag] = (('eta_'+gtag, 'xi_'+gtag), G['lat_'+gtag])
# add depth and z_rho
ds['h'] = (('eta_rho', 'xi_rho'), G['h'])
ds['z_rho'] = (('s_rho','eta_rho', 'xi_rho'), gfun.get_zr(G, S, 'salt'))

# save the result to NetCDF
out_fn = indir0 / 'glorys_clm.nc'
out_fn.unlink(missing_ok=True)
ds.to_netcdf(out_fn)
ds.close()


