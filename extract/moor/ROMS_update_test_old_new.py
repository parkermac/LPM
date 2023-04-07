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
#sn_list =  ['dabob']

# gtx_old = 'cas6_v0_live'
# date_str_old = '2017.01.01_2017.12.31'

gtx_old = 'cas6_v00_x0mb'
date_str_old = '2017.01.01_2017.12.31'

gtx_new = 'cas6_traps2_x0mb'
date_str_new = '2017.01.01_2017.08.28'

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
    pfun.start_plot(fs=10, figsize=(20,12))

    fig = plt.figure()

    vn_list = ['salt', 'temp', 'phytoplankton', 'zooplankton', 'oxygen',
        'DIN', 'TIC', 'alkalinity','Sdet','Ldet']

    ii = 0
    ax_list = [1,2,4,5,7,8,10,11,13,14]
    Nave = 1 # number to deep or shallow s_rho layers to average over
    zbot = ds_new.z_w[0,0].values
    zmid_deep = ds_new.z_w[0,Nave].mean(axis=0).values
    zmid_shallow = ds_new.z_w[0,-(Nave+1)].mean(axis=0).values
    surf_str = '(0-%0.1f m)' % (int(-zmid_shallow))
    bot_str = '(%0.1f-%0.1f m)' % (int(-zbot), int(-zmid_deep))
    # NOTE: these are not proper volume-weighted averages!
    
    # decide if the "old" files are from the updated bio code or not
    if 'NH4' in ds_old.data_vars:
        old_old = False
    else:
        old_old = True

    for vn in vn_list:
        ax = fig.add_subplot(5,3,ax_list[ii])
    
        if vn == 'Sdet':
            if old_old:
                ax.plot(T, ds_old['detritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
                ax.plot(T, ds_old['detritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            else:
                ax.plot(T, ds_old['SdetritusN'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
                ax.plot(T, ds_old['SdetritusN'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new['SdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new['SdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        elif vn == 'Ldet':
            if old_old:
                ax.plot(T, ds_old['Ldetritus'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
                ax.plot(T, ds_old['Ldetritus'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            else:
                ax.plot(T, ds_old['LdetritusN'][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
                ax.plot(T, ds_old['LdetritusN'][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new['LdetritusN'][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new['LdetritusN'][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        elif vn == 'DIN':
            if old_old:
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
                ax.plot(T, ds_old['NO3'][:,-Nave:].mean(axis=1).values + ds_old['NH4'][:,-Nave:].mean(axis=1).values,
                    '-r', label='Old Surface '+surf_str)
                ax.plot(T, ds_old['NO3'][:,:Nave].mean(axis=1).values + ds_old['NH4'][:,:Nave].mean(axis=1).values,
                    '--r', label='Old Bottom'+bot_str)
                ax.plot(Tn, ds_new['NO3'][:,-Nave:].mean(axis=1).values + ds_new['NH4'][:,-Nave:].mean(axis=1).values,
                    '-b', label='New Surface')
                ax.plot(Tn, ds_new['NO3'][:,:Nave].mean(axis=1).values + ds_new['NH4'][:,:Nave].mean(axis=1).values,
                    '--b', label='New Bottom')
                ax.plot(T, ds_old['NH4'][:,-Nave:].mean(axis=1).values, '-g', label='Old NH4 Surface')
                ax.plot(T, ds_old['NH4'][:,:Nave].mean(axis=1).values, '--g', label='Old NH4 Bottom')
                ax.plot(Tn, ds_new['NH4'][:,-Nave:].mean(axis=1).values, '-c', label='New NH4 Surface')
                ax.plot(Tn, ds_new['NH4'][:,:Nave].mean(axis=1).values, '--c', label='New NH4 Bottom')
                ax.text(.05,.6,'Old NH4', c='g', transform=ax.transAxes)
                ax.text(.05,.7,'New NH4', c='c', transform=ax.transAxes)
                
        else:
            ax.plot(T, ds_old[vn][:,-Nave:].mean(axis=1).values, '-r', label='Old Surface '+surf_str)
            ax.plot(T, ds_old[vn][:,:Nave].mean(axis=1).values, '--r', label='Old Bottom'+bot_str)
            ax.plot(Tn, ds_new[vn][:,-Nave:].mean(axis=1).values, '-b', label='New Surface')
            ax.plot(Tn, ds_new[vn][:,:Nave].mean(axis=1).values, '--b', label='New Bottom')
        
        
        if vn in ['TIC', 'alkalinity']:
            ax.set_ylim(1000,2500)
        
        ax.set_xlim(Tn[0],Tn[-1])
        if ii == 0:
            ax.legend(ncol=2)
        ax.text(.05,.9,vn,transform=ax.transAxes)
        if ax_list[ii] in [13,14]:
            ax.set_xlabel('Yearday')
        else:
            pass
        ii += 1
        
    # map for station location
    ax = fig.add_subplot(1,3,3)
    lon = ds_old.lon_rho.values
    lat = ds_old.lat_rho.values
    ax.plot(lon,lat,'*',mfc='y',mec='k',markersize=15)
    pfun.add_coast(ax)
    pad = .5
    ax.axis([lon-pad,lon+pad,lat-pad,lat+pad])
    pfun.dar(ax)
    
    ax.set_title('%s\nOld = %s\nNew = %s' % (sn, gtx_old, gtx_new))
    
    fig.savefig(out_dir / (sn + '.png'))
    
    plt.show()
    pfun.end_plot()

