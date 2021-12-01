"""
A tool to extract time series of hypoxic volume in the segments.

To test on mac:
run extract_hvol_segments -gtx cas6_v3_lo8b -ro 2 -0 2019.07.04 -1 2019.07.06

Performance:
"""
import sys
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from lo_tools import Lfun, zrfun

Ldir = Lfun.Lstart()

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

fn = Ldir['LOo'] / 'extract' / 'cas6_v3_lo8b' / 'tef'/ 'hvol_segments_2018.01.01_2018.12.31.nc'

ds = xr.open_dataset(fn)

which_vol = 'Puget Sound'

# Info specific to each volume
if which_vol == 'Salish Sea':
    seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
        + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH
        + flux_fun.ssJ + flux_fun.ssG)
elif which_vol == 'Puget Sound':
    seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
        + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH)
elif which_vol == 'Hood Canal':
    seg_list = flux_fun.ssH
    
a = ds.sel(seg=seg_list)
aa = a.sum(dim='seg')

hv = aa.hypoxic_volume/1e9
v = aa.volume/1e9

plt.close('all')
hv.plot()
plt.show()

