"""
Code to explore benthic flux from a mooring extraction.

"""
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

sn = 'ORCA_Hoodsport' # 'CE02', 'ORCA_Hoodsport', 'JdF_west','Willapa','dabob'
date_str = '2017.01.01_2017.12.31'

plt.close('all')
pfun.start_plot(figsize=(18,10))
fig1, axes1 = plt.subplots(nrows=4,ncols=1,squeeze=False)
fig2, axes2 = plt.subplots(nrows=4,ncols=1,squeeze=False)

for old in [False, True]:

    if old:
        gtx = 'cas6_v0_live'
        c = 'r'
    else:
        gtx = 'cas6_v00_uu0mb'
        c = 'b'
    

    in_dir = Ldir['LOo'] / 'extract' / gtx / 'moor' / 'ROMS_update'
    fn = in_dir / (sn + '_' + date_str + '.nc')
    ds = xr.open_dataset(fn)

    # time
    ot = ds.ocean_time.values
    ot_dt = pd.to_datetime(ot)
    t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
    T = t/86400 # time in days from start

    if old:
        sdet = ds['detritus'][:,0].values
        ldet = ds['Ldetritus'][:,0].values
    else:
        sdet = ds['SdetritusN'][:,0].values
        ldet = ds['LdetritusN'][:,0].values

    ox = ds['oxygen'][:,0].values

    # estimate the model benthic fluxes

    # particle flux to bottom [mmol N m-2 d-1]
    f_det = (8*sdet + 80*ldet)

    # loss of NO3 to denitrification (positive = loss)
    # (assume we are not anoxic)
    if old:
        f_no3 = 0 * f_det.copy()
        f_no3[f_det > 1.2] = 1.2
        
    else:
        f_no3 = f_det.copy()
        f_no3[f_det > 1.2] = 1.2

    # gain of NH4 due to remineralization
    f_nh4 = f_det-f_no3
    f_nh4[f_nh4<0] = 0

    # loss of oxygen due to remineralization
    if old:
        f_ox = (106/16) * f_nh4
    else:
        f_ox = (118/16) * f_nh4

    f_dict = {'f_det':f_det, 'f_no3':f_no3, 'f_nh4':f_nh4, 'f_ox':f_ox}

    # basic time series
    ii = 0
    if old:
        vn_list = ['DIN','oxygen','detritus','Ldetritus']
    else:
        vn_list = ['DIN','oxygen','SdetritusN','LdetritusN']
    for vn in vn_list:
        ax = axes1[ii,0]
        if vn == 'DIN':
            if old:
                v = ds.NO3[:,0].values
            else:
                v = ds.NO3[:,0].values + ds.NH4[:,0].values
        else:
            v = ds[vn][:,0].values
        ax.plot(T,v,'-'+c)
        if not old:
            ax.grid(True)
            ax.text(.05,.9,vn, fontweight='bold', transform=ax.transAxes)
            ax.set_xlim(T[0],T[-1])
        ii += 1
    
    # benthic fluxes
    ii = 0
    for vn in f_dict.keys():
        ax = axes2[ii,0]
        v = f_dict[vn]
        ax.plot(T,v,'-'+c)
        if not old:
            ax.grid(True)
            ax.text(.05,.9,vn, fontweight='bold', transform=ax.transAxes)
            ax.set_xlim(T[0],T[-1])
        ii += 1

fig1.suptitle('Red = Old, Blue = New')
fig2.suptitle('Red = Old, Blue = New')
    
pfun.end_plot()
plt.show()
