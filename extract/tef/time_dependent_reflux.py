"""
Plot a time series of the efflux-reflux coefficients in the segment
between two or more sections.

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

# output location
out_dir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef'
Lfun.make_dir(out_dir)

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

# get two-layer time series

# seaward 0
tef_df0, in_sign0, dir_str0, sdir0 = flux_fun.get_two_layer(bulk_in_dir, 'ai1', 'cas6')

# landward 1
if False:
    # simple case: single section
    tef_df1, in_sign1, dir_str1, sdir1 = flux_fun.get_two_layer(bulk_in_dir, 'ai2', 'cas6')
    tstr = 'Admiralty Inlet: ai1 to ai2'
else:
    # more complicated: two sections
    # The sign for each section indicates which direction is INTO the volume.
    sect_list = ['ai4','hc1']
    tef_df1a,_,_,_ = flux_fun.get_two_layer(bulk_in_dir, sect_list[0], 'cas6')
    tef_df1b,_,_,_ = flux_fun.get_two_layer(bulk_in_dir, sect_list[1], 'cas6')
    tef_df1 = pd.DataFrame(index = tef_df1a.index)
    tef_df1['Qin'] = tef_df1a['Qin'] + tef_df1b['Qin']
    tef_df1['Qout'] = tef_df1a['Qout'] + tef_df1b['Qout']
    tef_df1['salt_in'] = (tef_df1a['Qin']*tef_df1a['salt_in'] +
                    tef_df1b['Qin']*tef_df1b['salt_in'])/tef_df1['Qin']
    tef_df1['salt_out'] = (tef_df1a['Qout']*tef_df1a['salt_out'] +
                    tef_df1b['Qout']*tef_df1b['salt_out'])/tef_df1['Qout']
    tef_df1['qabs'] = tef_df1a['qabs'] + tef_df1b['qabs']
    tstr = 'Admiralty Inlet: ai1 to ai4 & hc1'

# translate to my efflux-reflux notation
# volume transport
df = pd.DataFrame(index=tef_df0.index)
df['q0'] = tef_df0['Qin']/1000
df['Q0_orig'] = -tef_df0['Qout']/1000
df['Q1'] = tef_df1['Qin']/1000
df['q1'] = -tef_df1['Qout']/1000
# salinity
df['s0'] = tef_df0['salt_in']
df['S0'] = tef_df0['salt_out']
df['S1'] = tef_df1['salt_in']
df['s1'] = tef_df1['salt_out']

# enforce volume conservation
df['Q0'] = df['q0'] + df['q1'] - df['Q1']

# add Qprism and DS
df['Qprism0'] = (tef_df0['qabs']/2)/1000
df['Qprism1'] = (tef_df1['qabs']/2)/1000
df['DS0'] = tef_df0['salt_in'] - tef_df0['salt_out']
df['DS1'] = tef_df1['salt_in'] - tef_df1['salt_out']
df['Qin'] = df['q0']
df['Qout'] = -df['q1']

# calculate efflux-reflux coefficients
df['a0'] = (df['Q0']/df['q0'])*(df['S0']-df['s1'])/(df['s0']-df['s1'])
df['a1'] = 1 + (df['Q0']/df['q1'])*(df['S0']-df['s0'])/(df['s0']-df['s1'])

# calculate efflux_reflux volume transports
df['Qefflux'] = df['a0'] * df['q0']
df['Qreflux'] = -df['a1'] * df['q1']

# alternate versions using the steady Knudsen balance
df['a0_alt'] = (df['s0']/df['S0'])*(df['S0']-df['s1'])/(df['s0']-df['s1'])
df['a1_alt'] = (df['s1']/df['S1'])*(df['s0']-df['S1'])/(df['s0']-df['s1'])

# time limits
t0 = df.index[0]
t1 = df.index[-1]

# PLOTTING()
plt.close('all')
fs = 16
lw=2
pfun.start_plot(fs=fs, figsize=(18,8))
fig = plt.figure()

cprism = 'c'
cQin = 'm'
cDS = 'violet'
c_dict = {'Qin': cQin, 'DS':cDS}

fig = plt.figure()

ax = fig.add_subplot(111)
ax.set_title(tstr)
ax2 = ax.twinx()
df['Qin'].plot(ax=ax, lw=lw, color='r', label=r'$Q_{in}$ (seaward end)')
df['Qout'].plot(ax=ax, lw=lw, color='b', label=r'$Q_{out}$ (landward end)')
df['Qefflux'].plot(ax=ax, lw=lw, color='m', label=r'$Q_{efflux}$ (up)')
df['Qreflux'].plot(ax=ax, lw=lw, color='g', label=r'$Q_{reflux}$ (down)')

df['Qprism0'].plot(ax=ax2, legend=False, lw=lw, color=cprism)
ax.legend(ncol=4)
ax.set_xlim(t0, t1)
ax2.set_xlim(t0, t1)
ax.set_ylim(-80,80)
ax.axhline()
ax2.set_ylim(0,200)
ax.grid(axis='x')
ax2.grid(axis='x')
ax2.set_ylabel(r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism)
ax.set_ylabel(r'$Transports\ [10^{3}m^{3}s^{-1}]$', color='k')


fig.tight_layout()
fig.savefig(out_dir / 'time_dependent_reflux.png')
plt.show()
pfun.end_plot()
