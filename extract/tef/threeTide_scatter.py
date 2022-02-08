"""
Plot TEF properties vs Qprism, using the time mean
of all sections, for the three tidal manipulation experiments.
"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
from time import time

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

# prep output location for plots
out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef'
Lfun.make_dir(out_dir)

gridname = 'cas6'
sect_df = tef_fun.get_sect_df(gridname)
sect_list = list(sect_df.index)

ii = 0
for gtagex in ['cas6_v3_lo8b', 'cas6_v3t075_lo8', 'cas6_v3t110_lo8']:
    in_fn = Path('/Users/pm8/Documents/LO_output/extract/' + gtagex +
        '/tef/two_layer_mean_2018.08.01_2018.12.31.p')
    df = pd.read_pickle(in_fn)
    if ii == 0:
        df0 = df.copy()
    elif ii == 1:
        df1 = df.copy()
    elif ii == 2:
        df2 = df.copy()
    ii += 1

# PLOTTING
c0 = 'g'
c1 = 'dodgerblue'
c2 = 'darkred'
alpha = 0.4
ms = 8
fs = 14

plt.close('all')
pfun.start_plot(fs=fs, figsize=(8,8))

# Modify or create some columns
df0['Qin'] = df0['Qin']/1000
df1['Qin'] = df1['Qin']/1000
df2['Qin'] = df2['Qin']/1000

df0['QinDS'] = df0['Qin'] * df0['DS']
df1['QinDS'] = df1['Qin'] * df1['DS']
df2['QinDS'] = df2['Qin'] * df2['DS']


yax_dict = {'Qin': r'$Q_{in}\ [10^{3}\ m^{3}s^{-1}]$',
            'QinDS': r'$Qin\Delta S\ [10^{3}\ m^{3}s^{-1}\ g\ kg^{-1}]$',
            'DS': r'$\Delta S\ [g\ kg^{-1}]$',
            'salt_out': r'$Sout\ [g\ kg^{-1}]$',
            'Sbar': r'$(Sin + Sout)/2\ [g\ kg^{-1}]$'}
            
for yax in yax_dict.keys():
    if yax in ['Qin', 'QinDS']:
        loglog = True; logx = False
    elif yax in ['DS', 'Sbar']:
        loglog = False; logx = True
        
    yax_text = yax_dict[yax]
    fig = plt.figure()
    ax = fig.add_subplot(111)

    df0.plot(x='Qprism', y=yax, linestyle='None', marker='o',
        color=c0, ax=ax, label='Original', alpha=alpha, loglog=loglog, logx=logx, markersize=ms)
    df1.plot(x='Qprism', y=yax, linestyle='None', marker='o',
        color=c1, ax=ax, label='75% tide', alpha=alpha, loglog=loglog, logx=logx, markersize=ms)
    df2.plot(x='Qprism', y=yax, linestyle='None', marker='o',
        color=c2, ax=ax, label='110% tide', alpha=alpha, loglog=loglog, logx=logx, markersize=ms)
    ax.legend()
    ax.grid(True)
    ax.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax.set_ylabel(yax_text)
    for sect_name in sect_list:
        # add section names
        ax.text(df0.loc[sect_name,'Qprism'], df0.loc[sect_name,yax], sect_name, fontsize=.7*(fs),
            color='k', ha='center', va='center')
        # add lines connecting the experiments for each section
        ax.plot([df0.loc[sect_name,'Qprism'], df1.loc[sect_name,'Qprism']],
                [df0.loc[sect_name,yax], df1.loc[sect_name,yax]], '-', c='gray')
        ax.plot([df0.loc[sect_name,'Qprism'], df2.loc[sect_name,'Qprism']],
                [df0.loc[sect_name,yax], df2.loc[sect_name,yax]], '-', c='gray')
                
    fig.savefig(out_dir / (yax + '_vs_Qprism.png'))

plt.show()
pfun.end_plot()

