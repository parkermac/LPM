"""
Code based on that from Ivica Janeković, ivica.jan@gmail.com

This is aimed at reliable extraction of the time axis.
"""


import os
import numpy as np
# from netCDF4 import Dataset, num2date
from datetime import datetime, timedelta
import xarray as xr
import cftime
from time import time
from lo_tools import Lfun

Ldir = Lfun.Lstart()

url  = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ssh/FMRC_ESPC-D-V02_ssh_best.ncd'

out_dir = Ldir['parent'] / 'LPM_output' / 'hycom_test'
Lfun.make_dir(out_dir)

out_fn = out_dir / 'time.nc'

cmd = 'ncks -O -C -v time ' + url + ' ' + str(out_fn)

print(cmd)
os.system(cmd)

# check on the results
ds = xr.open_dataset(out_fn)
print(ds)
