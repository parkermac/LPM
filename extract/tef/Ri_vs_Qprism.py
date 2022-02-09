"""
Plot a ratio that is supposed to tell us whether the exchange is
enabled by tides or limited by graviational circulation.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
from time import time
import xarray as xr
from datetime import datetime, timedelta

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

year = 2018
g = 9.8
beta = 7.7e-4

gtagex = 'cas6_v3_lo8b'
#gtagex = 'cas6_v3t110_lo8'
#gtagex = 'cas6_v3t075_lo8'
gridname, tag, ex_name = gtagex.split('_')
Ldir = Lfun.Lstart(gridname=gridname, tag=tag, ex_name=ex_name)

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

sect_df = tef_fun.get_sect_df(gridname)
sect_list = list(sect_df.index)

dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
ext_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('extractions_' + dates_string)
bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

# prep output location for plots
out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef'
Lfun.make_dir(out_dir)

# PLOTTING()
plt.close('all')

# limits for the time range
dt0 = datetime(year, 7, 1, 12)
dt1 = datetime(year, 10, 31, 12)

fs = 18 # fontsize
# all sections, time-means
pfun.start_plot(fs=fs)
fig = plt.figure()
ax = fig.add_subplot(111)
for sect_name in sect_list:
    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(bulk_in_dir, sect_name, 'cas6')
    
    # limit the time range
    tef_df = tef_df[dt0:dt1]
    
    # make derived variables
    tef_df['Qprism'] = (tef_df['qabs']/2)
    
    # get section info
    ds = xr.open_dataset(ext_in_dir / (sect_name + '.nc'))
    A = ds.DA0.sum().values
    A2 = A*A
    H = ds.h.max().values
    ds.close()
    
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    # drop times with negative DS
    tef_df[tef_df['DS']<=0] = np.nan
    
    tef_df['Ri'] = g*beta*tef_df['DS']*A2*H/(32*tef_df['Qin']*tef_df['Qin'])
    tef_df['Ri'][tef_df['Ri'] <= 0] = np.nan
            
    
    # add point
    if sect_name in ['tn2','ai4', 'ss3', 'mb4']:
        ax.loglog(tef_df['Qprism'].mean()/1e3, tef_df['Ri'].mean(), 's', ms=24)
        ax.text(1.01*tef_df['Qprism'].mean()/1e3, 1.01*tef_df['Ri'].mean(), sect_name, weight='bold')
    else:
        ax.loglog(tef_df['Qprism'].mean()/1e3, tef_df['Ri'].mean(), 'o', alpha=.6)
        ax.text(1.01*tef_df['Qprism'].mean()/1e3, 1.01*tef_df['Ri'].mean(), sect_name)

ax.grid(True)
ax.set_xlabel(r'$Q_{prism}\ [10^{3} m^{3}s^{-1}]$')
ax.set_ylabel(r'$Ri$')

fig.savefig(out_dir / 'Ri_vs_Qprism_mean.png')

pfun.end_plot()

plt.show()

