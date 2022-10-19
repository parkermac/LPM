"""
Code to plot time series for a list of moorings, comparing two
versions of the code, focusing on biogeochemistry.

This one is designed to compare:
old = cas6_v0_live (the current run, using the old LiveOcean code)
new = cas6_v00_uu0kb (the new ROMS code)
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

sn_list =  ['CE02', 'ORCA_Hoodsport', 'JdF_west']
date_str = '2021.01.01_2021.07.29'

plt.close('all')
for sn in sn_list:
    
    fn = sn + '_' + date_str + '.nc'
    dir_old = Ldir['LOo'] / 'extract' / 'cas6_v0_live' / 'moor' / 'ROMS_update'
    dir_new = Ldir['LOo'] / 'extract' / 'cas6_v00_uu0mb' / 'moor' / 'ROMS_update'
    fn_old = dir_old / fn
    fn_new = dir_new / fn

    if False:
        # smooth in time
        Ds_old = xr.open_dataset(fn_old)
        Ds_new = xr.open_dataset(fn_new)
        ds_old = Ds_old.resample(ocean_time='M').mean()
        ds_new = Ds_new.resample(ocean_time='M').mean()
    else:
        ds_old = xr.open_dataset(fn_old)
        ds_new = xr.open_dataset(fn_new)

    # time
    ot = ds_old.ocean_time.values
    ot_dt = pd.to_datetime(ot)
    t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
    T = t/86400 # time in days from start

    # plotting
    pfun.start_plot()

    fig = plt.figure(figsize=(16,12))

    vn_list = ['salt', 'temp', 'phytoplankton', 'zooplankton', 'oxygen',
        'NO3', 'TIC', 'alkalinity','Sdet','Ldet']

    ii = 1
    Nave = 5 # number to deep or shallow s_rho layers to average over
    zbot = ds_new.z_w[0,0].values
    zmid_deep = ds_new.z_w[0,Nave].mean(axis=0).values
    zmid_shallow = ds_new.z_w[0,-(Nave+1)].mean(axis=0).values
    surf_str = '(0-%d m)' % (int(-zmid_shallow))
    bot_str = '(%d-%d m)' % (int(-zbot), int(-zmid_deep))

    for vn in vn_list:
        ax = fig.add_subplot(5,2,ii)
    
        if vn == 'Sdet':
            ax.plot(T, ds_old['detritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old['detritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(T, ds_new['SdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(T, ds_new['SdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        elif vn == 'Ldet':
            ax.plot(T, ds_old['Ldetritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old['Ldetritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(T, ds_new['LdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(T, ds_new['LdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        else:
            ax.plot(T, ds_old[vn][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old[vn][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(T, ds_new[vn][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(T, ds_new[vn][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
    
        if vn == 'NO3':
            ax.plot(T, ds_new['NH4'][:,-Nave:].mean(axis=1).values, '-g', label='New NH4 Surface')
            ax.plot(T, ds_new['NH4'][:,:Nave].mean(axis=1).values, '--g', label='New NH4 Bottom')
        
            ax.plot(T, ds_new['NO3'][:,-Nave:].mean(axis=1).values + ds_new['NH4'][:,-Nave:].mean(axis=1).values,
                '-c', label='New NO3+NH4 Surface')
            ax.plot(T, ds_new['NO3'][:,:Nave].mean(axis=1).values + ds_new['NH4'][:,:Nave].mean(axis=1).values,
                '--c', label='New NO3+NH4 Bottom')
        
            ax.text(.05,.7,'New NH4', c='g', transform=ax.transAxes)
            ax.text(.05,.8,'New NO3+NH4', c='c', transform=ax.transAxes)
        
        if vn in ['TIC', 'alkalinity']:
            ax.set_ylim(1000,2600)
        
        ax.set_xlim(T[0],T[-1])
        if ii == 1:
            ax.legend(ncol=2)
        ax.text(.05,.9,vn,transform=ax.transAxes)
        if ii in [9,10]:
            ax.set_xlabel('Yearday')
        else:
            pass
            #ax.set_xticklabels([])
        ii += 1
    fig.suptitle(fn)
    
    plt.show()
    pfun.end_plot()

