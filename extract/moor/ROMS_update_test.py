"""
Code to plot time series for the aiN mooring extraction.  Starting with
vertically-integrated buoyancy flux.
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

#sn = 'ORCA_Hoodsport'
sn = 'CE02'
date_str = '2021.01.01_2021.01.28'
fn = sn + '_' + date_str + '.nc'

dir_old = Ldir['LOo'] / 'extract' / 'cas6_v0_live' / 'moor' / 'ROMS_update'
dir_new = Ldir['LOo'] / 'extract' / 'cas6_v00_uu0kb' / 'moor' / 'ROMS_update'
fn_old = dir_old / fn
fn_new = dir_new / fn

ds_old = xr.open_dataset(fn_old)
ds_new = xr.open_dataset(fn_new)

# time
ot = ds_old.ocean_time.values
ot_dt = pd.to_datetime(ot)
t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
T = t/86400 # time in days from start

# plotting
plt.close('all')
pfun.start_plot()

fig = plt.figure(figsize=(16,12))

vn_list = ['salt', 'temp', 'phytoplankton', 'zooplankton', 'oxygen', 'NO3', 'TIC', 'alkalinity']

ii = 1
for vn in vn_list:
    ax = fig.add_subplot(4,2,ii)
    ax.plot(T, ds_old[vn][:,-1].values, '-r', label='Old Surface')
    ax.plot(T, ds_old[vn][:,0].values, '--r', label='Old Bottom')
    ax.plot(T, ds_new[vn][:,-1].values, '-b', label='New Surface')
    ax.plot(T, ds_new[vn][:,0].values, '--b', label='New Bottom')
    
    if vn == 'NO3':
        ax.plot(T, ds_new['NH4'][:,-1].values, '-g', label='New NH4 Surface')
        ax.plot(T, ds_new['NH4'][:,0].values, '--g', label='New NH4 Bottom')
        
    if ii == 1:
        ax.legend()
    ax.text(.05,.9,vn,transform=ax.transAxes)
    if ii in [7,8]:
        pass
    else:
        ax.set_xticklabels([])
    ii += 1
fig.suptitle(fn)
    
plt.show()
pfun.end_plot()

