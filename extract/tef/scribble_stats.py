"""
Calculate and plot statistics of varios TEF things vs Qprism, for
all sections.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
from time import time
from datetime import datetime, timedelta
import xarray as xr

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

if True:
    sect_df = tef_fun.get_sect_df(gridname)
    sect_list = list(sect_df.index)
else:
    sect_list = ['ai1','ai4', 'tn2', 'sji1']

# specify bulk folder
dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

# prep output location for plots
out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef'
Lfun.make_dir(out_dir)

# PLOTTING
plt.close('all')
fs = 16
pfun.start_plot(fs=fs, figsize=(16,8))

fig, axes = plt.subplots(nrows=1, ncols=2, squeeze=True)

vn_dict = {0:'Qin', 1:'DS'}

for sect_name in sect_list:
    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(bulk_in_dir, sect_name, 'cas6')
    
    # limit the time range
    tef_df = tef_df[dt0:dt1]
    
    # make derived variables
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    qp = tef_df['qabs'].to_numpy()/2
    tef_df['Qprism'] = qp
    
    # drop times with negative DS
    tef_df[tef_df['DS']<=0] = np.nan
    
    # calculate fit statistics
    x = np.log10(tef_df['Qprism'].to_numpy())
    
    for ii in range(2):
        ax = axes[ii]
        vn = vn_dict[ii]
        if vn == 'Qin':
            y = np.log10(tef_df[vn].to_numpy())
        elif vn == 'DS':
            y = tef_df[vn].to_numpy()
        mask = np.isnan(y) | np.isnan(x)
        xx = x[~mask]
        yy = y[~mask]
        slope, y0, r, ci_mean, ci_trend = zfun.linefit(xx, yy)
        ax.plot(slope, r, '.')
        ax.text(slope, r, sect_name, fontsize=.7*(fs),
            color='k', ha='center', va='center')

for ii in range(2):
    ax = axes[ii]
    ax.grid(True)
    # ax.axis('square')
    ax.set_ylim(-1,1)
    ax.set_xlabel('Slope')
    ax.set_ylabel('Correlation Coefficient: r')
    vn = vn_dict[ii]
    if vn == 'Qin':
        ax.set_title('log10(' + vn + ') vs. log10(Qprism)')
    elif vn == 'DS':
        ax.set_title(vn + ' vs. log10(Qprism)')
    ax.axhline()
    ax.axvline()
    
# fig.tight_layout()
fig.savefig(out_dir / 'scribble_stats.png')

plt.show()
pfun.end_plot()
