"""
Plot a time series to see if dsdx changes throughout the year in Admiralty Inlet

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

dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
# specify bulk folder
ext_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('extractions_' + dates_string)
bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

# PLOTTING()
plt.close('all')
pfun.start_plot()
fig = plt.figure()

# get two-layer time series

# landward 0
tef_df0, in_sign0, dir_str0, sdir0 = flux_fun.get_two_layer(bulk_in_dir, 'ai4', 'cas6')

# seaward 1
tef_df1, in_sign1, dir_str1, sdir1 = flux_fun.get_two_layer(bulk_in_dir, 'ai1', 'cas6')

tef_df0 = tef_df0.resample('M').mean()
tef_df1 = tef_df1.resample('M').mean()


tef_df0['Sbar'] = (tef_df0['salt_in'] + tef_df0['salt_out'])/2
tef_df1['Sbar'] = (tef_df1['salt_in'] + tef_df1['salt_out'])/2

tef_df1['dsdx'] = tef_df1['Sbar'].to_numpy() - tef_df0['Sbar'].to_numpy()

ax = fig.add_subplot(211)
tef_df1['dsdx'].plot(ax=ax)

ax = fig.add_subplot(212)
tef_df1['Qin'].plot(ax=ax)

plt.show()
pfun.end_plot()
