#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is code to test getting glorys model output. It is based on code from Felipe Soares,
and then modified by me.

Created on Wed Dec  6 10:39:40 2023
@author: fsoares

NOTES:

depth is positive down and packed top-to-bottom

The REANALYSIS product goes from 1993 - recent past

daily (this is daily mean):
cmems_mod_glo_phy_my_0.083deg_P1D-m

The FORECAST product has the last two years + (sliding window)
including 10 days of forecast.

hourly:
cmems_mod_glo_phy_anfc_0.083deg_PT1H-m
time range on 2025.04.02: 06/01/2022, 00:00 to 04/11/2025, 23:00

daily:
cmems_mod_glo_phy_anfc_0.083deg_P1D-m [ERROR: need to do separate downloads]

"""
import copernicusmarine
from datetime import datetime, timedelta
from time import time
import xarray as xr

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# get Copernicus login credentials
cred_fn = Ldir['data'] / 'accounts' / 'glorys_pm_2025.04.02.csv'
cred_dict = Lfun.csv_to_dict(cred_fn)

# name the output file
out_dir = Ldir['parent'] / 'LPM_output' / 'glorys'
Lfun.make_dir(out_dir)

# Use copernicusmarine.subset
# copernicusmarine.subset? gives useful info on the API

if True:
    # daily average from forecast
    tt0 = time()
    out_name = 'glorys_test0_daily.nc'
    out_fn = out_dir / out_name
    start_date = datetime(2025, 4, 6)
    date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
        variables=["uo", "vo", "so", "thetao", "zos"],

        # minimum_longitude=-131,
        # maximum_longitude=-121,
        # minimum_latitude=41,
        # maximum_latitude=53,
        minimum_longitude=-125,
        maximum_longitude=-124.75,
        minimum_latitude=45,
        maximum_latitude=45.25,

        start_datetime=date_str,
        end_datetime=date_str,

        # No need to specify depth - the defalt is to get all depths
        # minimum_depth=0.494,
        # maximum_depth=5727.917,
        # minimum_depth=0,
        # maximum_depth=6000,

        output_filename=out_name,
        output_directory=str(out_dir),

        username=cred_dict['username'],
        password=cred_dict['password'],
        overwrite=True,
        disable_progress_bar=True
    )
    print('time to get one snapshot = %0.1f' % (time()-tt0))

if False:
    # daily average from renalaysis
    tt0 = time()
    out_name = 'glorys_test0_daily.nc'
    out_fn = out_dir / out_name
    start_date = datetime(2019, 2, 26)
    date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
        variables=["uo", "vo", "so", "thetao", "zos"],

        # minimum_longitude=-131,
        # maximum_longitude=-121,
        # minimum_latitude=41,
        # maximum_latitude=53,
        minimum_longitude=-125,
        maximum_longitude=-124.5,
        minimum_latitude=45,
        maximum_latitude=45.5,

        start_datetime=date_str,
        end_datetime=date_str,

        # No need to specify depth - the defalt is to get all depths
        # minimum_depth=0.494,
        # maximum_depth=5727.917,
        # minimum_depth=0,
        # maximum_depth=6000,

        output_filename=out_name,
        output_directory=str(out_dir),

        username=cred_dict['username'],
        password=cred_dict['password'],
        overwrite=True,
        disable_progress_bar=True
    )
    print('time to get one snapshot = %0.1f' % (time()-tt0))

if False:
    # hourly from forecast [only appears to have surface fields]
    tt0 = time()
    out_name = 'glorys_test0_hourly.nc'
    out_fn = out_dir / out_name
    start_date = datetime(2025, 4, 2)
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date = datetime(2025, 4, 3)
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        variables=["uo", "vo", "so", "thetao", "zos"],

        minimum_longitude=-125,
        maximum_longitude=-124.75,
        minimum_latitude=45,
        maximum_latitude=45.25,

        minimum_depth=0,
        maximum_depth=6000,

        start_datetime=start_date_str,
        end_datetime=end_date_str,

        output_filename=out_name,
        output_directory=str(out_dir),

        username=cred_dict['username'],
        password=cred_dict['password'],
        overwrite=True,
        disable_progress_bar=True
    )
    print('time to get one day of hours = %0.1f' % (time()-tt0))

# ds = xr.open_dataset(out_fn)
