"""
Plot things vs. Qprism time series as a little scribble for each section.

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
    
plt.close('all')
for gtagex in ['cas6_v3_lo8b', 'cas6_v3t075_lo8', 'cas6_v3t110_lo8']:

    gridname, tag, ex_name = gtagex.split('_')
    Ldir = Lfun.Lstart(gridname=gridname, tag=tag, ex_name=ex_name)

    pth = Ldir['LO'] / 'extract' / 'tef'
    if str(pth) not in sys.path:
        sys.path.append(str(pth))
    import tef_fun
    import flux_fun

    if False:
        sect_df = tef_fun.get_sect_df(gridname)
        sect_list = list(sect_df.index)
    else:
        sect_list = ['ai1','ai4', 'tn2', 'sji1']

    # specify bulk folder
    dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
    # ext_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('extractions_' + dates_string)
    bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

    # prep output location for plots
    out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef'
    Lfun.make_dir(out_dir)

    # PLOTTING
    pfun.start_plot(fs=16, figsize=(18,6))

    fig = plt.figure()

    ax1 = fig.add_subplot(131)
    ax1.grid(True)
    ax1.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax1.set_ylabel(r'$Q_{in}\ [10^{3}\ m^{3}s^{-1}]$')

    ax2 = fig.add_subplot(132)
    ax2.grid(True)
    ax2.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax2.set_ylabel(r'$\Delta S\ [g\ kg^{-1}]$')

    ax3 = fig.add_subplot(133)
    ax3.grid(True)
    ax3.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax3.set_ylabel(r'$Q_{in} \Delta S\ [g\ kg^{-1}\ 10^{3}\ m^{3}s^{-1}]$')

    # ax4 = fig.add_subplot(224)
    # ax4.grid(True)
    # ax4.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    # ax4.set_ylabel(r'$Ri$')

    for sect_name in sect_list:
        # get two-layer time series
        tef_df, in_sign, dir_str, sdir = flux_fun.get_two_layer(bulk_in_dir, sect_name, 'cas6')
    
        # limit the time range
        tef_df = tef_df[dt0:dt1]
    
        # make derived variables
        tef_df['DS'] = tef_df['salt_in'] - tef_df['salt_out']
        qp = tef_df['qabs'].to_numpy()/2
        tef_df['Qprism'] = qp
    
        # drop times with negative DS
        tef_df[tef_df['DS']<=0] = np.nan
    
        # # get section info
        # ds = xr.open_dataset(ext_in_dir / (sect_name + '.nc'))
        # A = ds.DA0.sum().values
        # A2 = A*A
        # H = ds.h.max().values
        # ds.close()
        # # and calculate Ri
        # tef_df['Ri'] = g*beta*tef_df['DS']*A2*H/(32*tef_df['Qin']*tef_df['Qin'])
        # tef_df['Ri'][tef_df['Ri'] <= 0] = np.nan
    
        # and plot this section
        ax1.loglog(tef_df['Qprism'].to_numpy()/1000,tef_df['Qin'].to_numpy()/1000,'-', label=sect_name, alpha=.8)
        ax2.loglog(tef_df['Qprism'].to_numpy()/1000,tef_df['DS'].to_numpy(),'-', label=sect_name, alpha=.8)
        ax3.loglog(tef_df['Qprism'].to_numpy()/1000,(tef_df['Qin']*tef_df['DS']).to_numpy()/1000,'-', label=sect_name, alpha=.8)
        # ax4.loglog(tef_df['Qprism'].to_numpy()/1000,tef_df['Ri'],'-', label=sect_name, alpha=.8)
    
    ax1.legend()
    #ax1.set_title('lag = %d days' % (lag))
    fig.tight_layout()

    ax1.set_xlim(10,1000)
    ax2.set_xlim(10,1000)
    ax3.set_xlim(10,1000)
    ax1.set_ylim(3,300)
    ax2.set_ylim(.1,30)
    ax3.set_ylim(.5,500)

    fig.savefig(out_dir / ('scribble_vs_Qprism_' + gtagex + '.png'))

    plt.show()
    pfun.end_plot()
