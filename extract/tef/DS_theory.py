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
c0 = 'g'
c1 = 'dodgerblue'
c2 = 'darkred'
alpha = 0.4
ms = 8
fs = 14

plt.close('all')

df['DS_pred'] =  3.5 * (-df['Qfw']/1000) * df['salt_out'] / df['Qprism']

a = r'$\Delta S\ [g\ kg^{-1}]$'
    
pfun.start_plot(fs=fs, figsize=(9,9))
    
fig = plt.figure()
ax = fig.add_subplot(111)

df.plot(x='DS', y='DS_pred', linestyle='None', marker='*',
    color='b', ax=ax, label='Original', alpha=alpha, markersize=ms, legend=False)
ax.legend()
ax.grid(True)

for sect_name in sect_list:
    # add section names
    ax.text(df.loc[sect_name,'DS'], df.loc[sect_name,'DS_pred'], sect_name, fontsize=.7*(fs),
        color='k', ha='center', va='center')

ax.set_xlim(-.1,3)
ax.set_ylim(-.1,3)

ax.plot([0,3],[0,3],'-k')
ax.axis('square')

fig.tight_layout()
fig.savefig(out_dir / 'DS_theory.png')

plt.show()
pfun.end_plot()

