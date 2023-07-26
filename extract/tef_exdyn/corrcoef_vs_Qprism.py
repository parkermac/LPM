"""
Find r for Qin, DS, and Qin*DS vs. Qprism for all sections.

"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
from time import time
from datetime import datetime, timedelta
import xarray as xr

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

year = 2018
g = 9.8
beta = 7.7e-4
year_str = str(year)

# limit the time range
if True:
    dt0 = datetime(year, 7, 1, 12)
    dt1 = datetime(year, 10, 31, 12)
else:
    dt0 = datetime(year, 1, 1, 12)
    dt1 = datetime(year, 12, 31, 12)

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

# specify bulk folder
dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
# ext_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('extractions_' + dates_string)
bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

# select input directory
in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef'
in_fn = in_dir / 'two_layer_mean_2018.08.01_2018.12.31.p'

# prep output location for plots
out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef_exdyn'
Lfun.make_dir(out_dir)

# calculate correlation coefficients
r_df = pd.DataFrame(index=sect_list)
for sect_name in sect_list:
    # get two-layer time series
    tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(bulk_in_dir, sect_name, 'cas6')
    
    # limit the time range
    tef_df = tef_df[dt0:dt1]
    
    # make derived variables
    tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
    tef_df['QinDS'] = tef_df['Qin'] * tef_df['DS']
    qp = tef_df['qabs'].to_numpy()/2
    tef_df['Qprism'] = qp
    
    # drop times with negative DS
    tef_df = tef_df[tef_df['DS']>0]
    
    # calculate r for log of properties
    x = np.log10(tef_df['Qprism'].to_numpy())
    y_qin = np.log10(tef_df['Qin'].to_numpy())
    y_ds = np.log10(tef_df['DS'].to_numpy())
    y_qinds = np.log10(tef_df['QinDS'].to_numpy())

    r_qin = np.corrcoef(x,y_qin)[0,1]
    r_ds = np.corrcoef(x,y_ds)[0,1]
    r_qinds = np.corrcoef(x,y_qinds)[0,1]

    r_df.loc[sect_name,'r_qin'] = r_qin
    r_df.loc[sect_name,'r_ds'] = r_ds
    r_df.loc[sect_name,'r_qinds'] = r_qinds
    
    # also save mean Qin
    r_df.loc[sect_name,'Qin'] = tef_df.Qin.mean()
    

# PLOTTING
plt.close('all')
pfun.start_plot(fs=16, figsize=(12,7.5))#(16,12))
fig = plt.figure()

# colors
clist = flux_fun.clist

channel_list = flux_fun.channel_list
channel_dict = flux_fun.channel_dict

lcol_dict = flux_fun.c_dict
channel_list.reverse() # makes overlaying colors look better

# load the two_layer_mean DataFrame
df = pd.read_pickle(in_fn)

# create all the distance vectors and save in a dict
dist_dict = {}
for ch_str in channel_list:
    sect_list = channel_dict[ch_str]
    x = df.loc[sect_list,'lon'].to_numpy(dtype='float')
    y = df.loc[sect_list,'lat'].to_numpy(dtype='float')
    dist_dict[ch_str] = flux_fun.make_dist(x,y)

# adjust the distance vectors to join at the correct locations
ind_ai = channel_dict['Juan de Fuca to Strait of Georgia'].index('jdf4')
dist0_ai = dist_dict['Juan de Fuca to Strait of Georgia'][ind_ai]
dist_dict['Admiralty Inlet to South Sound'] += dist0_ai
#
ind_hc = channel_dict['Admiralty Inlet to South Sound'].index('ai3')
dist0_hc = dist_dict['Admiralty Inlet to South Sound'][ind_hc]
dist_dict['Hood Canal'] += dist0_hc
#
ind_wb = channel_dict['Admiralty Inlet to South Sound'].index('ai4')
dist0_wb = dist_dict['Admiralty Inlet to South Sound'][ind_wb]
dist_dict['Whidbey Basin'] += dist0_wb

distmax = 420
aa1 = [-5, distmax, 0 ,200]

ax = fig.add_subplot(111)

for ch_str in channel_list:
    sect_list = channel_dict[ch_str]
    dist_list = dist_dict[ch_str]
    c = lcol_dict[ch_str]
    ii = 0
    for sect in sect_list:
        x = dist_list[ii]
        # x = np.log10(r_df.loc[sect,'Qin'])
        r_qin = r_df.loc[sect,'r_qin']
        r_ds = r_df.loc[sect,'r_ds']
        r_qinds = r_df.loc[sect,'r_qinds']
        rr = r_qin * r_ds
        ax.plot(x, r_qin,'o', c=c)#, alpha=.5)
        # ax.plot(x, r_ds,'^', c=c)
        # ax.plot(x, r_qinds,'*', c=c)
        # ax.text(x,np.sign(rr)*np.sqrt(np.abs(rr)),sect,ha='center',
        #     va='center', fontsize=3 + np.abs(r_qinds)*20)
        ax.text(x,r_qin,sect,ha='center',
            va='center', fontsize=3 + np.abs(r_qin)*20)
        ii+=1

ax.set_xlim(-5,420)
ax.set_ylim(-1.1,1.1)
ax.axhline()
ax.grid(True)
ax.set_xlabel('Distance from Mouth (km)')
ax.set_ylabel('Correlation Coefficient')

fig.tight_layout()
#
fig.savefig(out_dir / 'corrcoef_vs_Qprism.png')
#
plt.show()
pfun.end_plot()
