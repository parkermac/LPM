"""
Plot the results of hypoxic_volume_extract_segments.py.
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

fn = Ldir['LOo'] / 'extract' / 'cas6_v3_lo8b' / 'tef'/ 'hvol_segments_2017.01.01_2021.11.30.nc'

ds = xr.open_dataset(fn)

which_vol = 'Strait of Georgia'

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
elif which_vol == 'Strait of Georgia':
    seg_list = flux_fun.ssG
    
a = ds.sel(seg=seg_list)
aa = a.sum(dim='seg')

hv1 = aa.hypoxic_volume_1/1e9
hv2 = aa.hypoxic_volume_2/1e9
hv3 = aa.hypoxic_volume_3/1e9
v = aa.volume/1e9

plt.close('all')
hv1.plot()
hv2.plot()
hv3.plot()
plt.show()

