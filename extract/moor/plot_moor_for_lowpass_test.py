"""
Code to compare the results of an extraction from the lowpassed files
to an hourly extraction that is lowpassed.

RESULT: Every field I looked at (2D, 3D, z_rho grid, and z_w grid)
all looked identical, indicating that the lowpass estraction code is
working as expected.

"""
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

Ldir = Lfun.Lstart()

verbose = False

# choose the files
in_dir = Ldir['LOo'] / 'extract' / 'cas7_t0_x4b' / 'moor'
hourly_fn = in_dir / 'test_hourly_2015.01.01_2015.12.31.nc'
lowpass_fn = in_dir / 'test_lowpass_2015.01.01_2015.12.31.nc'

pad = 36
# this pad is more than is required for the nans from the godin filter (35),
# but, when combined with the subsampling we end up with fields at Noon of
# each day (excluding the first and last days of the record)

# plotting

plt.close('all')
pfun.start_plot(figsize=(12,8))
fig = plt.figure()

hds = xr.open_dataset(hourly_fn)
lds = xr.open_dataset(lowpass_fn)

hot = hds.ocean_time.values
hdti = pd.to_datetime(hot) # a datetime index
hdtilp = hdti[pad:-pad+1:24]

lot = lds.ocean_time.values
ldti = pd.to_datetime(lot) # a datetime index

vn = 'TIC'

if ('s_rho' in hds[vn].coords) or ('s_w' in hds[vn].coords):
    nlev = 25
    hv = hds[vn][:,nlev].values
    hvlp = zfun.lowpass(hv, f='godin')[pad:-pad+1:24]
    lv = lds[vn][:,nlev].values
else:
    hv = hds[vn].values
    hvlp = zfun.lowpass(hv, f='godin')[pad:-pad+1:24]
    lv = lds[vn].values

ax = fig.add_subplot(111)

ax.plot(ldti,lv,'--c',lw=3) # from lowpassed files
ax.plot(hdtilp,hvlp,'-b') # from hourly files after lowpass
ax.set_title(vn)

plt.show()
pfun.end_plot()