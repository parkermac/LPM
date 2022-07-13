"""
Code to plot time series for a list of moorings, comparing two
versions of the code, focusing on biogeochemistry.

This one is designed to compare:
old = cas6_v00_uu0kb (the new ROMS code)
new = cas6_v00_uu0kbatt (the new ROMS code but with light attenuation coded to
    replicate the original "BSD as coded" version)
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()


sn_list =  ['CE02', 'ORCA_Hoodsport']

year = 2021
dt00 = datetime(year,1,1)
dt0 = datetime(year,3,1)
dt1 = datetime(year,4,10)
dt11 = datetime(year,12,31)
dstr00 = dt00.strftime(Ldir['ds_fmt'])
dstr0 = dt0.strftime(Ldir['ds_fmt'])
dstr1 = dt1.strftime(Ldir['ds_fmt'])
dstr11 = dt11.strftime(Ldir['ds_fmt'])
date_str = dstr0 + '_' + dstr1
date_str_orig = dstr00 + '_' + dstr11

ex_old = 'uu0kb'
ex_new = 'uu0kbatt'
ex_new2 = 'uu0kbattopt'

plt.close('all')
for sn in sn_list:
    
    fn = sn + '_' + date_str + '.nc'
    dir_old = Ldir['LOo'] / 'extract' / ('cas6_v00_' + ex_old) / 'moor' / 'ROMS_update'
    dir_new = Ldir['LOo'] / 'extract' / ('cas6_v00_' + ex_new) / 'moor' / 'ROMS_update'
    dir_new2 = Ldir['LOo'] / 'extract' / ('cas6_v00_' + ex_new2) / 'moor' / 'ROMS_update'
    fn_old = dir_old / fn
    fn_new = dir_new / fn
    fn_new2 = dir_new2 / fn
    
    # and get the original one as well
    fn_orig = sn + '_' + date_str_orig + '.nc'
    dir_orig = Ldir['LOo'] / 'extract' / 'cas6_v0_live' / 'moor' / 'ROMS_update'
    fn_orig = dir_orig / fn_orig

    ds_old = xr.open_dataset(fn_old)
    ds_new = xr.open_dataset(fn_new)
    ds_new2 = xr.open_dataset(fn_new2)
    ds_orig = xr.open_dataset(fn_orig)

    # time
    ot = ds_old.ocean_time.values
    ot_dt = pd.to_datetime(ot)
    t = (ot_dt - dt00).total_seconds().to_numpy()
    T = t/86400 # time in days from start of year

    # time orig
    ot_orig = ds_orig.ocean_time.values
    ot_orig_dt = pd.to_datetime(ot_orig)
    t_orig = (ot_orig_dt - dt00).total_seconds().to_numpy()
    T_orig = t_orig/86400 # time in days from start of year

    # plotting
    pfun.start_plot()

    fig = plt.figure(figsize=(16,13))

    vn_list = ['salt', 'phytoplankton', 'zooplankton', 'oxygen',
        'NO3', 'NH4', 'TIC', 'alkalinity','SdetritusN','LdetritusN']

    ii = 1
    Nave = 15
    zbot = ds_new.z_w[0,0].values
    zmid_deep = ds_new.z_w[0,Nave].mean(axis=0).values
    zmid_shallow = ds_new.z_w[0,-(Nave+1)].mean(axis=0).values
    surf_str = '(0-%d m)' % (int(-zmid_shallow))
    bot_str = '(%d-%d m)' % (int(-zbot), int(-zmid_deep))

    for vn in vn_list:
        ax = fig.add_subplot(5,2,ii)
    
        ax.plot(T, ds_old[vn][:,-Nave:].mean(axis=1).values, '-r', label=ex_old+' Surface '+surf_str)
        ax.plot(T, ds_old[vn][:,:Nave].mean(axis=1).values, '--r', label=ex_old+' Bottom'+bot_str)
        ax.plot(T, ds_new[vn][:,-Nave:].mean(axis=1).values, '-b', label=ex_new+' Surface')
        ax.plot(T, ds_new[vn][:,:Nave].mean(axis=1).values, '--b', label=ex_new+' Bottom')
        ax.plot(T, ds_new2[vn][:,-Nave:].mean(axis=1).values, '-g', label=ex_new2+' Surface')
        ax.plot(T, ds_new2[vn][:,:Nave].mean(axis=1).values, '--g', label=ex_new2+' Bottom')
        
        if vn == 'phytoplankton':
            ax.plot(T_orig, ds_orig[vn][:,-Nave:].mean(axis=1).values, '-m')
            ax.plot(T_orig, ds_orig[vn][:,:Nave].mean(axis=1).values, '--m')
            ax.text(.05,.6,'live', c='m', transform=ax.transAxes)
        
        if vn in ['TIC', 'alkalinity']:
            ax.set_ylim(1000,2600)
        
        ax.set_xlim(T[0],T[-1])
        if ii == 1:
            ax.legend()
        ax.text(.05,.9,vn,transform=ax.transAxes)
        if ii in [9,10]:
            ax.set_xlabel('Days from ' + dstr0)
        else:
            #pass
            ax.set_xticklabels([])
        ii += 1
    fig.suptitle(fn)
    
    plt.show()
    pfun.end_plot()

