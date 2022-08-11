"""
Plot a time series (pcolormesh) of transport vs. salinity.
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

year = 2018

sn = 'hc2'

salt_lims_dict = {
    'ai1': (30,33),
    'ai4': (29,33),
    'tn2': (30,32),
    'dp': (26,33),
    'sog5': (26,33),
    'mb2': (30,32),
    'hc2': (30,32),
    }
    

time_lims = (275,300)

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

p_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('processed_' + dates_string)
b_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

p_in_fn = p_in_dir / (sn + '.p')
b_in_fn = b_in_dir / (sn + '.p')

p = pickle.load(open(p_in_fn,'rb'))
b = pickle.load(open(b_in_fn,'rb'))
tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(b_in_dir, sn, 'cas6')

dt0 = datetime(year,1,1)
t0 = Lfun.datetime_to_modtime(dt0)

t = (p['ot'].data - t0)/86400
q = p['q'].T/1e3
sb = p['sbins']

S = b['salt']
NT, NS = S.shape
T = ((b['ot'].data - t0)/86400).reshape((NT,1)) * np.ones((1,NS))
Qprism = b['qabs']/(2*1e3)
Q = b['q']/1e3

T2 = tef_df.index.to_pydatetime()
TT = [(item-dt0).total_seconds()/86400 for item in T2]
Qin = tef_df['Qin'].to_numpy()/1000

plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(20,10))

ax = fig.add_subplot(211)
# cs = ax.pcolormesh(t,sb,q, shading='nearest', cmap='bwr', vmin=-Qin.mean(), vmax=Qin.mean())
cs = ax.pcolormesh(t,sb,q, shading='nearest', cmap='bwr', vmin=-10*q.std(), vmax=10*q.std())
mask = Q > 0
ax.scatter(T[mask], S[mask], s=40*Q[mask]/Qin.mean(), c='m')
mask = Q < 0
ax.scatter(T[mask], S[mask], s=-40*Q[mask]/Qin.mean(), c='c')
ax.set_ylim(salt_lims_dict[sn])
ax.set_xlim(time_lims)
ax.grid(True)
ax.set_title('Section ' + sn)
ax.set_ylabel('Salinity')

ax = fig.add_subplot(212)
ax.plot((b['ot'].data - t0)/86400, Qprism, '-g')
ax.plot(TT, Qin, '-r')
ax.set_xlim(time_lims)
ax.set_ylim(bottom=0)
ax.grid(True)
ax.set_xlabel('Days since start of ' + str(year))
ax.text(.05,.9,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$',c='g',transform=ax.transAxes)
ax.text(.05,.1,r'$Q_{in}\ [10^{3}m^{3}s^{-1}]$',c='r',transform=ax.transAxes)




plt.show()
pfun.end_plot()
