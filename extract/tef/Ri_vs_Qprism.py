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

testing = False
year = 2018

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
if testing:
    sect_list = ['ai1', 'ai4', 'mb3', 'tn2']

dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
# specify bulk folder
ext_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('extractions_' + dates_string)
bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

# PLOTTING()
plt.close('all')
pfun.start_plot()
fig = plt.figure()
ax = fig.add_subplot(111)

# limit the time range
dt0 = datetime(year, 7, 1, 12)
dt1 = datetime(year, 10, 31, 12)

sect_list = ['ai1','ai2','ai3', 'ai4', 'tn2', 'jdf4', 'dp', 'mb3']
c_dict = dict(zip(sect_list,['r','b','g','c','orange', 'purple','k','cornflowerblue']))

for sect_name in sect_list: #sect_list:
    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(bulk_in_dir, sect_name, 'cas6')
    
    # limit the time range
    tef_df = tef_df[dt0:dt1]
    
    # make derived variables
    tef_df['Qprism'] = (tef_df['qabs']/2)
    # use Freshwater Flux as an alternate way to calculate Qr
    Socn = 34
    tef_df['Qfw'] = (tef_df['Qin']*(Socn-tef_df['salt_in'])
                    + tef_df['Qout']*(Socn-tef_df['salt_out']))/Socn
    
    # get section info
    ds = xr.open_dataset(ext_in_dir / (sect_name + '.nc'))
    A = ds.DA0.sum().values
    A2 = A*A
    H = ds.h.max().values
    g = 9.8
    beta = 7.7e-4
    
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    tef_df['Ri'] = g*beta*tef_df['DS']*A2*H/(32*tef_df['Qin']*tef_df['Qin'])
    tef_df['Ri'][tef_df['Ri'] <= 0] = np.nan
            
    ds.close()
    
    # add scribble
    ax.loglog(tef_df['Qprism'].to_numpy()/1e3, tef_df['Ri'].to_numpy(), '-', c=c_dict[sect_name], label=sect_name)
    
ax.legend()
ax.grid(True)
# ax.axis([0, 200, 0, 200])
# ax.plot([0,200], [0,200], '-k')
# ax.axis('square')
ax.set_xlabel(r'$Q_{prism} [10^{3} m^{3}s^{-1}]$')
ax.set_ylabel(r'$Ri$')
plt.show()
pfun.end_plot()
