"""
Code to explore the extracted hycom fields.  The specific goal is
to see if there are obvous artifacts of data assimilation that might
contaminate bottom pressure analysis that I am doing for the MG&G folks.

This one makes a time series.
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from time import time

from lo_tools import zfun, Lfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()
hdir0 = Ldir['data'] / 'hycom'
hy_list = ['hy'+str(item) for item in range(1,7)]

out_dir = Ldir['parent'] / 'LPM_output' / 'hycom'
Lfun.make_dir(out_dir)

t_list = []
salt_list = []
temp_list = []
hexp_list = []

testing = False

if testing:
    hy_list = hy_list[:2]
    
for hy in hy_list:
    print('Working on %s' % (hy))
    sys.stdout.flush()
    hdir = hdir0 / hy
    fn_list = list(hdir.glob('*.nc'))
    fn_list.sort()
    
    if testing:
        pass
        #fn_list = fn_list[:100]
        
    for fn in fn_list:
        ds = xr.open_dataset(fn)
        lon = ds.lon.values - 360 # convert from 0:360 to -360:0 format
        lat = ds.lat.values
        ii = zfun.find_nearest_ind(lon, -126)
        jj = zfun.find_nearest_ind(lat, 46)
        t = ds.time.values[0]
        # depth index -5 is 2000 m
        N = -5
        salt = ds.salinity[0, N, jj, ii].values
        temp = ds.water_temp[0, N, jj, ii].values
        t_list.append(t)
        salt_list.append(float(salt))
        temp_list.append(float(temp))
        hexp_list.append(float(hy[-1]))
        ds.close()

NT = len(salt_list)
data = np.concatenate((np.array(salt_list).reshape(NT,1),
                        np.array(temp_list).reshape(NT,1),
                        np.array(hexp_list).reshape(NT,1)), axis=1)
df = pd.DataFrame(index=t_list, data=data, columns=['salt', 'temp', 'hexp'])

df.to_pickle(out_dir / 'h1.p')



