"""
Code based on that from Ivica Janeković, ivica.jan@gmail.com

This is aimed at reliable extraction of the time and other axes.
"""


import os
import numpy as np
from datetime import datetime, timedelta
import xarray as xr
from time import time
import pandas as pd
from subprocess import Popen as Po
from subprocess import PIPE as Pi
from lo_tools import Lfun, zfun

Ldir = Lfun.Lstart()

# specify the sub region of hycom to extract
aa = [-131, -121, 39, 53]
# convert to hycom format
north = aa[3]
south = aa[2]
west = aa[0] + 360
east = aa[1] + 360

url  = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ssh/FMRC_ESPC-D-V02_ssh_best.ncd'

out_dir = Ldir['parent'] / 'LPM_output' / 'hycom_test'
Lfun.make_dir(out_dir)

def messages(mess_str, stdout, stderr):
    # utility function to help with subprocess errors
    try:
        if len(stdout) > 0:
            print(mess_str)
            print(stdout.decode())
    except TypeError:
        pass
    try:
        if len(stderr) > 0:
            print(mess_str)
            print(stderr.decode())
    except TypeError:
        pass

out_fn = out_dir / 'tyx.nc'
# get rid of the old version, if it exists
out_fn.unlink(missing_ok=True)

cmd_list = ['ncks','-O','-v','time,lat,lon',url,str(out_fn)]
proc = Po(cmd_list, stdout=Pi, stderr=Pi)
stdout, stderr = proc.communicate()
messages('ncks tyx messages:', stdout, stderr)

# check on the results
ds = xr.open_dataset(out_fn)
print(ds)
# find selected indices to use with ncks to extract fields
t = ds.time.values
tt = pd.DatetimeIndex(t)
t0 = datetime(2024,9,14)
it = np.argwhere(tt==t0)[0][0]
x = ds.lon.values
y = ds.lat.values
ix0 = zfun.find_nearest_ind(x,west)
ix1 = zfun.find_nearest_ind(x,east)
iy0 = zfun.find_nearest_ind(y,south)
iy1 = zfun.find_nearest_ind(y,north)
xx = x[ix0:ix1+1]
yy = y[iy0:iy1+1]
#
ds.close()

