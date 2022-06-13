"""
Plot the exchange flow in a dynamical context.

Similar to some axes in salt_budget.py but better for focusing on one
section at a time.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
from time import time

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart(gridname='cas6', tag='v3', ex_name='lo8b')

# output location
out_dir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef' / 'Qprism_series'
Lfun.make_dir(out_dir)

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

# get the DataFrame of all sections
sect_df = tef_fun.get_sect_df(Ldir['gridname'])

sect_list = sect_df.index
#sect_list = ['ai1'] # testing

for sect_name in sect_list:
    
    year = 2018
    year_str = str(year)
    date_str = '_' + year_str + '.01.01_' + year_str + '.12.31'

    tef_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk' + date_str)

    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(tef_dir, sect_name, Ldir['gridname'])

    # make derived variables
    tef_df['Qin'] = tef_df['Qin']/1000
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    tef_df['QinDS'] = tef_df['Qin'] * tef_df['DS']
    tef_df['Qprism'] = (tef_df['qabs']/2)/1000

    # PLOTTING
    plt.close('all')

    cprism = 'c'
    cQinDS = 'r'
    cQin = 'm'
    cDS = 'violet'
    c_dict = {'QinDS': cQinDS, 'Qin': cQin, 'DS':cDS}

    fs = 16
    lw=3
    pfun.start_plot(fs=fs, figsize=(14,10))
    fig = plt.figure()

    vn_list = ['QinDS', 'Qin', 'DS']
    label_list = [r'$Q_{in}\Delta S\ [g\ kg^{-1}\ 10^{3}m^{3}s^{-1}]$',
                r'$Q_{in}\ [10^{3}m^{3}s^{-1}]$',
                r'$\Delta S\ [g\ kg^{-1}]$']
    label_dict = dict(zip(vn_list, label_list))

    # time limits
    t0 = tef_df.index[0]
    t1 = tef_df.index[-1]

    nvn = len(vn_list)
    ii = 1
    for vn in vn_list:
        ax = fig.add_subplot(nvn,1,ii)
        ax2 = ax.twinx()
        tef_df[[vn]].plot(ax=ax, legend=False, lw=lw, color=c_dict[vn])
        tef_df['Qprism'].plot(ax=ax2, legend=False, lw=lw, color=cprism)
        if ii == 1:
            ax.set_title(sect_name + ' : ' + 'positive inflow ' + dir_str)
        if ii < nvn:
            ax.set_xticklabels([])
            ax.set_xlabel('')
        
        ax.text(.05,.1,label_dict[vn], color=c_dict[vn], transform=ax.transAxes,
            bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
        ax2.text(.95,.1,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism, transform=ax.transAxes, ha='right',
            bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
        ax.set_xlim(t0, t1)
        ax2.set_xlim(t0, t1)
        ax.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)
        ax.grid(axis='x')
        ax2.grid(axis='x')
    
        ii += 1
        
    fig.tight_layout()
    fig.savefig(out_dir / (sect_name + '.png'))

    #plt.show()
    pfun.end_plot()