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

for sect_name in sect_list:
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
    H = ds.h.max().values
    g = 9.8
    beta = 7.7e-4
    
    # parameters for the transport theories
    alpha = .25
    Ricrit = 1
    
    # form time means
    Qr = -tef_df['Qfw'].mean()
    Qin = tef_df['Qin'].mean()
    Qprism = tef_df['Qprism'].mean()
    Sin = (tef_df['Qin'] * tef_df['salt_in']).mean() / tef_df['Qin'].mean()
    Sout = (tef_df['Qout'] * tef_df['salt_out']).mean() / tef_df['Qout'].mean()
    
    # more derived quantities
    c2 = g * beta * H * Sin
    A2 = A*A
    
    # for theoretical predictions of Qin (converted to )
    Qtide = alpha*Qprism
    Qgrav = (c2 * A2 * Qr * (Sout / Sin) / (32 * Ricrit))**(1/3)
    
    print('%s: Qin = %0.1f, Qtide = %0.1f, Qgrav = %0.1f' % (sect_name, Qin/1e3, Qtide/1e3, Qgrav/1e3))
        
    ds.close()
    
    # add points and section names to plot
    if (not np.isnan(Qin)) and (not np.isnan(Qgrav)):
        ax.plot(Qin/1e3, Qgrav/1e3, 'ob', alpha=.2)
        ax.text(Qin/1e3, Qgrav/1e3, sect_name, fontsize=12, ha='center', va='center', rotation=-45)

ax.grid(True)
ax.axis([0, 200, 0, 200])
ax.plot([0,200], [0,200], '-k')
ax.axis('square')
ax.set_xlabel('Qin')
ax.set_ylabel('Qgrav (theory)')
plt.show()
pfun.end_plot()
