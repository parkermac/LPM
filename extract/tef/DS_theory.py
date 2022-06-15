"""
Plot actual vs. predicted DS.
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

gtagex = 'cas6_v3_lo8b'
in_fn = Ldir['LOo'] / 'extract' / gtagex / 'tef' / 'two_layer_mean_2018.08.01_2018.12.31.p'
df = pd.read_pickle(in_fn)

# PLOTTING
alpha = 0.4
ms = 8
fs = 14
plt.close('all')

# Create the predicted DeltaS
df['DS_pred'] =  3.5 * (-df['Qfw']/1000) * df['salt_out'] / df['Qprism']

a = r'$\Delta S\ [g\ kg^{-1}]$'
    
pfun.start_plot(fs=fs, figsize=(16,8))
    
fig = plt.figure()

for ii in [1,2]:
    ax = fig.add_subplot(1,2,ii)
    
    df.plot(x='DS', y='DS_pred', linestyle='None', marker='o',
        color='orange', ax=ax, label='Original', alpha=alpha, markersize=ms, legend=False)
    ax.grid(True)

    for sect_name in sect_list:
        # add section names
        ax.text(df.loc[sect_name,'DS'], df.loc[sect_name,'DS_pred'], sect_name, fontsize=.7*(fs),
            color='k', ha='center', va='center')

    if ii == 1:
        hi = 11
        ax.text(.05,.8,'(a) Full Range', transform=ax.transAxes, fontweight='bold')
        pfun.draw_box(ax, [0,3,0,3], linestyle='-', color='gray', alpha=1, linewidth=2, inset=0)
    elif ii == 2:
        hi = 3
        ax.text(.05,.8,'(b) Close-up', transform=ax.transAxes, fontweight='bold')
    ax.set_xlabel(r'$\Delta S\ [g\ kg^{-1}]$')
    ax.set_ylabel(r'$\Delta S_{pred}\ [g\ kg^{-1}]$')
    ax.axis('square')
    ax.set_xlim(-.1,hi)
    ax.set_ylim(-.1,hi)
    ax.plot([0,hi],[0,hi],'-k')

fig.tight_layout()
fig.savefig(out_dir / 'DS_theory.png')

plt.show()
pfun.end_plot()

