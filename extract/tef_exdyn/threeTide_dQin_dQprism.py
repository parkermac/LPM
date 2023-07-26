"""
Plot dQin/dQprism vs. Qprism, using the time mean
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
out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef_exdyn' / 'threeTide_scatter'
Lfun.make_dir(out_dir)

gridname = 'cas6'
sect_df = tef_fun.get_sect_df(gridname)
sect_list = list(sect_df.index)

ii = 0
for gtagex in ['cas6_v3_lo8b', 'cas6_v3t075_lo8', 'cas6_v3t110_lo8']:
    in_fn = Path('/Users/pm8/Documents/LO_output/extract/' + gtagex +
        # '/tef/two_layer_mean_2018.08.01_2018.12.31.p')
        '/tef/two_layer_mean_2018.01.01_2018.12.31.p')
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

# Modify or create some columns
df0['Qin'] = df0['Qin']/1000
df1['Qin'] = df1['Qin']/1000
df2['Qin'] = df2['Qin']/1000

df0['QinDS'] = df0['Qin'] * df0['DS']
df1['QinDS'] = df1['Qin'] * df1['DS']
df2['QinDS'] = df2['Qin'] * df2['DS']

df0['Sout'] = df0['salt_out']
df1['Sout'] = df1['salt_out']
df2['Sout'] = df2['salt_out']

# make a DataFrame with dQin/dQprism (110% - 75%)
dfd = pd.DataFrame(index=df0.index,columns=['Qprism','dQin','dDS','dQinDS','dQprism'])
dfd.Qprism = df0.Qprism
dfd.dQin = df2.Qin - df1.Qin
dfd.dDS = df2.DS - df1.DS
dfd.dQinDS = df2.QinDS - df1.QinDS
dfd.dQprism = df2.Qprism - df1.Qprism
dfd['dQin_dQprism'] = dfd.dQin/dfd.dQprism
dfd['dDS_dQprism'] = dfd.dDS/dfd.dQprism
dfd['dQinDS_dQprism'] = dfd.dQinDS/dfd.dQprism

# plotting
plt.close('all')
pfun.start_plot(fs=fs, figsize=(8,8))
fig = plt.figure()
ax = fig.add_subplot(111)
vn = 'dQin_dQprism'
# vn = 'dDS_dQprism'
# vn = 'dQinDS_dQprism'
dfd.plot(x='Qprism', y=vn, linestyle='None', marker='o', alpha=.3,
    logx=True, ax=ax, legend=False)
for sn in dfd.index:
    # add section names
    ax.text(dfd.loc[sn,'Qprism'], dfd.loc[sn,vn], sn, fontsize=1*(fs), fontweight='bold',
        color='k', ha='center', va='center')

ax.axhline(c='k',lw=3)
ax.axhline(y=1/3,c='gray',ls='--',lw=2)
ax.axhline(y=1/4,c='gray',ls='-',lw=2)
ax.grid(True)

ax.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')

yax_dict = {'dQin_dQprism': r'$dQ_{in}/dQ_{prism}$',
            'dDS_dQprism': r'$d\Delta S/dQ_{prism}$',
            'dQinDS_dQprism': r'$d(Q_{in}\Delta S)/dQ_{prism}$'}
ax.set_ylabel(yax_dict[vn])

fig.tight_layout()
plt.show()
fig.savefig(out_dir / (vn + '.png'))

