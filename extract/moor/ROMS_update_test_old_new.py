"""
Code to plot time series for a list of moorings, comparing two
versions of the code, focusing on biogeochemistry.

This one is designed to compare:
old = cas6_v0_live (the current run, using the old LiveOcean code)
new = cas6_v00[]_uu0kb (the new ROMS code, and variations thereof)
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

sn_list =  ['CE02', 'ORCA_Hoodsport', 'JdF_west','Willapa','dabob']
#sn_list =  ['Willapa']

gtx_old = 'cas6_v0_live'
date_str_old = '2017.01.01_2017.12.31'

gtx_new = 'cas6_v00_x0mb'
date_str_new = '2017.01.01_2017.12.31'

out_dir = Ldir['parent'] / 'LPM_output' / 'ROMS_update'
Lfun.make_dir(out_dir)

plt.close('all')
for sn in sn_list:
    
    dir_old = Ldir['LOo'] / 'extract' / gtx_old / 'moor' / 'ROMS_update'
    dir_new = Ldir['LOo'] / 'extract' / gtx_new / 'moor' / 'ROMS_update'

    fn_old = dir_old / (sn + '_' + date_str_old + '.nc')
    fn_new = dir_new / (sn + '_' + date_str_new + '.nc')

    ds_old = xr.open_dataset(fn_old)
    ds_new = xr.open_dataset(fn_new)

    # time
    ot = ds_old.ocean_time.values
    ot_dt = pd.to_datetime(ot)
    t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
    T = t/86400 # time in days from start
    
    ot = ds_new.ocean_time.values
    ot_dt = pd.to_datetime(ot)
    t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
    Tn = t/86400 # time in days from start

    # plotting
    pfun.start_plot()

    fig = plt.figure(figsize=(16,12))

    vn_list = ['salt', 'temp', 'phytoplankton', 'zooplankton', 'oxygen',
        'DIN', 'TIC', 'alkalinity','Sdet','Ldet']

    ii = 1
    Nave = 1 # number to deep or shallow s_rho layers to average over
    zbot = ds_new.z_w[0,0].values
    zmid_deep = ds_new.z_w[0,Nave].mean(axis=0).values
    zmid_shallow = ds_new.z_w[0,-(Nave+1)].mean(axis=0).values
    surf_str = '(0-%0.1f m)' % (int(-zmid_shallow))
    bot_str = '(%0.1f-%0.1f m)' % (int(-zbot), int(-zmid_deep))
    # NOTE: these are not proper volume-weighted averages!

    for vn in vn_list:
        ax = fig.add_subplot(5,2,ii)
    
        if vn == 'Sdet':
            ax.plot(T, ds_old['detritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old['detritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new['SdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new['SdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        elif vn == 'Ldet':
            ax.plot(T, ds_old['Ldetritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old['Ldetritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new['LdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new['LdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        elif vn == 'DIN':
            ax.plot(T, ds_old['NO3'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old['NO3'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new['NO3'][:,-Nave:].mean(axis=1).values + ds_new['NH4'][:,-Nave:].mean(axis=1).values,
                '-b', label='New Surface')
            ax.plot(Tn, ds_new['NO3'][:,:Nave].mean(axis=1).values + ds_new['NH4'][:,:Nave].mean(axis=1).values,
                '--b', label='New Bottom')
            ax.plot(Tn, ds_new['NH4'][:,-Nave:].mean(axis=1).values, '-c', label='New NH4 Surface')
            ax.plot(Tn, ds_new['NH4'][:,:Nave].mean(axis=1).values, '--c', label='New NH4 Bottom')
            ax.text(.05,.7,'New NH4', c='c', transform=ax.transAxes)
        else:
            ax.plot(T, ds_old[vn][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old[vn][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new[vn][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new[vn][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        
        
        if vn in ['TIC', 'alkalinity']:
            ax.set_ylim(1000,2500)
        
        ax.set_xlim(Tn[0],Tn[-1])
        if ii == 1:
            ax.legend(ncol=2)
        ax.text(.05,.9,vn,transform=ax.transAxes)
        if ii in [9,10]:
            ax.set_xlabel('Yearday')
        else:
            pass
            #ax.set_xticklabels([])
        ii += 1
    fig.suptitle('%s :: Old = %s, New = %s' % (sn, gtx_old, gtx_new))
    
    fig.savefig(out_dir / (sn + '.png'))
    
    plt.show()
    pfun.end_plot()

