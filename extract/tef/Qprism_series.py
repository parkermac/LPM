"""
Plot the exchange flow in a dynamical context.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
from time import time

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

# specify section and bulk folder
sect_name = 'ai1'
in_dir = Path('/Users/pm8/Documents/LO_output/extract/cas6_v3_lo8b/tef/bulk_2018.01.01_2018.12.31')

# get two-layer time series
tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(in_dir, sect_name, 'cas6')

# make derived variables
tef_df['Qe'] = ((tef_df['Qin'] - tef_df['Qout'])/2)/1000
tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
tef_df['QeDS'] = tef_df['Qe'] * tef_df['DS']
tef_df['Sbar'] = (tef_df['salt_in'] + tef_df['salt_out'])/2
tef_df['Qprism'] = (tef_df['qabs']/2)/1000
# use Freshwater Flux as an alternate way to calculate Qr
Socn = 34
tef_df['Qfw'] = (tef_df['Qin']*(Socn-tef_df['salt_in']) + tef_df['Qout']*(Socn-tef_df['salt_out']))/Socn
# also calculate the related Saltwater Flux
tef_df['Qsw'] = (tef_df['Qin']*tef_df['salt_in'] + tef_df['Qout']*tef_df['salt_out'])/Socn

# PLOTTING
c1 = 'darkred'
c2 = 'dodgerblue'

plt.close('all')
fs = 14
pfun.start_plot(fs=fs, figsize=(14,12))
fig = plt.figure()

vn_list = ['Qe', 'DS', 'QeDS', 'Qfw', 'Qsw']
label_list = [r'$Q_{E}\ [10^{3}\ m^{3}s^{-1}]$', r'$\Delta S$', r'$Q_{E}\Delta S\ [10^{3}\ m^{3}s^{-1}]$',
    r'$Q_{FW}\ [m^{3}s^{-1}]$', r'$Q_{SW}\ [m^{3}s^{-1}]$']
label_dict = dict(zip(vn_list, label_list))

# limit list
vn_list = vn_list[:3]

# time limits
t0 = tef_df.index[0]
t1 = tef_df.index[-1]

nvn = len(vn_list)
ii = 1
for vn in vn_list:
    ax = fig.add_subplot(nvn,1,ii)
    ax2 = ax.twinx()
    tef_df[[vn]].plot(ax=ax, legend=False, lw=3, color=c2)
    tef_df['Qprism'].plot(ax=ax2, legend=False, color=c1)
    if ii == 1:
        ax.set_title(in_dir.parent.parent.name + ' : ' + sect_name + ' : ' + 'positive inflow ' + dir_str)
    if ii < nvn:
        ax.set_xticklabels([])
        ax.set_xlabel('')
    ax.axhline(c='gray')
    ax2.set_ylim(bottom = 0)
    ax.set_ylabel(label_dict[vn], color=c2)
    ax2.set_ylabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$', c=c1)
    ax.set_xlim(t0, t1)
    ax2.set_xlim(t0, t1)
    ii += 1
        
#fig.tight_layout()
plt.show()
pfun.end_plot()