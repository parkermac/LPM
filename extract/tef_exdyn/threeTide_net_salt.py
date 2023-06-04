"""
Compare net salt vs. time in different basins for the threeTide experiments.

"""

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import sys

Ldir = Lfun.Lstart()

# output location
out_dir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef_exdyn'
Lfun.make_dir(out_dir)

out_fn = out_dir / 'threeTide_net_salt.png'

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun
import flux_fun

year = 2018

plt.close('all')
pfun.start_plot()

vol_list = ['Salish Sea', 'Puget Sound', 'South Sound', 'Hood Canal']

g_list = ['cas6_v3t075_lo8', 'cas6_v3_lo8b', 'cas6_v3t110_lo8']
t_list = ['75% Tide', '100% Tide', '110% Tide']
t_dict = dict(zip(g_list,t_list))

fig = plt.figure(figsize=(14,8))

c0 = 'dodgerblue'
c1 = 'g'
c2 = 'darkred'
clist = [c0,c1,c2]

ii = 1

for which_vol in vol_list:

    for gtagex in g_list:
        year_str = str(year)
        date_str = '_' + year_str + '.01.01_' + year_str + '.12.31'
        # get paths to all required data
        seg_fn = Ldir['LOo'] / 'extract' / gtagex / 'tef' / ('segments' + date_str + '.nc')
        vol_dir = Ldir['LOo'] / 'extract' / 'tef' / 'volumes_cas6'

        # Info specific to each volume
        # The sign for each section indicates which direction is INTO the volume.
        if which_vol == 'Salish Sea':
            seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
                + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH
                + flux_fun.ssJ + flux_fun.ssG)
        elif which_vol == 'Puget Sound':
            seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
                + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH)
        elif which_vol == 'Puget Sound no AI':
            seg_list = (flux_fun.ssM + flux_fun.ssT
                + flux_fun.ssS + flux_fun.ssW)
        elif which_vol == 'Hood Canal':
            seg_list = flux_fun.ssH
        elif which_vol == 'South Sound':
            seg_list = flux_fun.ssT + flux_fun.ssS

            
        # SEGMENT TIME SERIES
        """
        These are now stored in an xr.Dataset:
        time = hourly (so we lowpass, subsample, and clip the ends)
        seg = segment names
        variable names = volume + all the tracers in tef_fun.vn_list
        - note that the tracers are the average in each volume
        """
        pad = 36
    
        seg_ds = xr.load_dataset(seg_fn)
        seg_ds = seg_ds.sel(seg=seg_list)
            
        if gtagex == g_list[0]:
            df = pd.DataFrame(index=seg_ds.time[pad:-pad+1:24], columns=t_list)
        
        # volume
        v = zfun.lowpass(seg_ds.volume.values, f='godin')[pad:-pad+1:24]
        vnet = v.sum(axis=1)
        V = vnet.mean() # average total volume
        
        # volume-averaged salt
        s = (seg_ds.volume*seg_ds.salt).sum(axis=1)/V
        S = zfun.lowpass(s.values, f='godin')[pad:-pad+1:24]
        
        df[t_dict[gtagex]] = S

    ax = fig.add_subplot(2,2,ii)
    if ii == 1:
        df.plot(ax=ax,color=clist)
    else:
        df.plot(ax=ax, legend=False, color=clist)
    
    ax.set_xlim(df.index[0],df.index[-1])
    ax.set_ylim(29,32)
    
    ax.text(.95,.05,['(a)','(b)','(c)','(d)',][ii-1] + ' ' + which_vol,
        ha='right',transform=ax.transAxes, fontweight='bold')
    
    if ii in [3,4]:
        ax.set_xlabel('Time')
        
    if ii in [1,3]:
        ax.set_ylabel('Mean Salinity')
        
    if ii in [1,2]:
        ax.set_xticklabels([])
        
    if ii in [2,4]:
        ax.set_yticklabels([])
        
    ii += 1
    
plt.show()
pfun.end_plot()

fig.savefig(out_fn)

