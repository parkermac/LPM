"""
Plot things vs. Qprism time series as a little scribble for each section.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
from time import time
from datetime import datetime, timedelta

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

year = 2018
year_str = str(year)

# limit the time range
dt0 = datetime(year, 7, 1, 12)
dt1 = datetime(year, 10, 31, 12)

gtagex = 'cas6_v3_lo8b'
gridname, tag, ex_name = gtagex.split('_')
Ldir = Lfun.Lstart(gridname=gridname, tag=tag, ex_name=ex_name)

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

# sect_df = tef_fun.get_sect_df(gridname)
# sect_list = list(sect_df.index)
sect_list = ['ai1', 'ai4', 'mb3', 'tn2']

# specify bulk folder
in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_'+year_str+'.01.01_'+year_str+'.12.31')

# PLOTTING
#plt.close('all')
pfun.start_plot(figsize=(15,5))

fig = plt.figure()

ax1 = fig.add_subplot(131)
ax1.grid(True)
ax1.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
ax1.set_ylabel(r'$\Delta S$')

ax2 = fig.add_subplot(132)
ax2.grid(True)
ax2.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
ax2.set_ylabel(r'$Q_{in}\ [10^{3}\ m^{3}s^{-1}]$')

ax3 = fig.add_subplot(133)
ax3.grid(True)
ax3.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
ax3.set_ylabel(r'$Q_{in} \Delta S\ [10^{3}\ m^{3}s^{-1}]$')

for sect_name in sect_list:
    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(in_dir, sect_name, 'cas6')
    
    # limit the time range
    tef_df = tef_df[dt0:dt1]
    
    # make derived variables
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    qp = tef_df['qabs'].to_numpy()/2
    lag = 0
    qpl = np.roll(qp,lag)
    tef_df['Qprism'] = qpl
    
    # drop times with negative DS
    # tef_df.loc[tef_df['DS'] <= 0, :] = np.nan
    # and plot this section
    ax1.plot(tef_df['Qprism'].to_numpy()/1000,tef_df['DS'].to_numpy(),'-', label=sect_name, alpha=.8)
    ax2.plot(tef_df['Qprism'].to_numpy()/1000,tef_df['Qin'].to_numpy()/1000,'-', label=sect_name, alpha=.8)
    ax3.plot(tef_df['Qprism'].to_numpy()/1000,(tef_df['Qin']*tef_df['DS']).to_numpy()/1000,'-', label=sect_name, alpha=.8)

    
ax1.legend()
ax1.set_title('lag = %d days' % (lag))
fig.tight_layout()
plt.show()
pfun.end_plot()
