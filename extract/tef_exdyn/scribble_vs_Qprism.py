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
    
def add_label(ax, lab):
    xlab=.03; ylab=.95
    ax.text(xlab,ylab,lab,ha='left',va='top',fontweight='bold',
        transform=ax.transAxes,bbox=pfun.bbox)

plt.close('all')
for gtagex in ['cas6_v3_lo8b', 'cas6_v3t075_lo8', 'cas6_v3t110_lo8']:

    gridname, tag, ex_name = gtagex.split('_')
    Ldir = Lfun.Lstart(gridname=gridname, tag=tag, ex_name=ex_name)
    
    pth = Ldir['LO'] / 'extract' / 'tef'
    if str(pth) not in sys.path:
        sys.path.append(str(pth))
    import tef_fun
    
    # get the DataFrame of all sections
    sect_df = tef_fun.get_sect_df(gridname)
    
    # output location for plots
    out_dir = Ldir['parent'] / 'LPM_output' / 'extract' / 'tef_exdyn' / 'scribble_plots'
    Lfun.make_dir(out_dir)

    pth = Ldir['LO'] / 'extract' / 'tef'
    if str(pth) not in sys.path:
        sys.path.append(str(pth))
    import tef_fun
    import flux_fun

    sect_list = ['ai1','ai4', 'tn2', 'sji1']
        
    c_list = ['r','g','b','m']
    c_dict = dict(zip(sect_list,c_list))

    # specify bulk folder
    dates_string = str(year) + '.01.01_' + str(year) + '.12.31'
    bulk_in_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk_' + dates_string)

    # PLOTTING
    pfun.start_plot(fs=18, figsize=(12,12))

    fig = plt.figure()
    
    axm = fig.add_subplot(221) # section map
    add_label(axm,'(a)')
    
    ax1 = fig.add_subplot(222)
    add_label(ax1,'(b)')
    ax1.grid(True)
    ax1.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax1.set_ylabel(r'$Q_{in}\ [10^{3}\ m^{3}s^{-1}]$')

    ax2 = fig.add_subplot(223)
    add_label(ax2,'(c)')
    ax2.grid(True)
    ax2.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax2.set_ylabel(r'$\Delta S\ [g\ kg^{-1}]$')

    ax3 = fig.add_subplot(224)
    add_label(ax3,'(d)')
    ax3.grid(True)
    ax3.set_xlabel(r'$Q_{prism}\ [10^{3}\ m^{3}s^{-1}]$')
    ax3.set_ylabel(r'$Q_{in} \Delta S\ [g\ kg^{-1}\ 10^{3}\ m^{3}s^{-1}]$')

    for sect_name in sect_list:
        
        # add section line on map
        x0, x1, y0, y1 = sect_df.loc[sect_name,:]
        axm.plot([x0,x1],[y0,y1],'-',c=c_dict[sect_name],lw=3)
        
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
        
        # and plot this section
        c=c_dict[sect_name]
        ax1.loglog(tef_df['Qprism'].to_numpy()/1000,tef_df['Qin'].to_numpy()/1000,'-', label=sect_name, alpha=.8, c=c)
        ax2.loglog(tef_df['Qprism'].to_numpy()/1000,tef_df['DS'].to_numpy(),'-', label=sect_name, alpha=.8, c=c)
        ax3.loglog(tef_df['Qprism'].to_numpy()/1000,(tef_df['Qin']*tef_df['DS']).to_numpy()/1000,'-', label=sect_name, alpha=.8, c=c)
    
    pfun.add_coast(axm, color='gray')
    pfun.dar(axm)
    axm.axis([-124, -122, 47, 48.8])
    axm.set_xticks([-124,-123,-122])
    axm.set_yticks([47, 48])
    axm.set_xlabel('Longitude')
    axm.set_ylabel('Latitude')
    
    ax1.legend()
    fig.tight_layout()

    ax1.set_xlim(10,1000)
    ax2.set_xlim(10,1000)
    ax3.set_xlim(10,1000)
    ax1.set_ylim(3,300)
    ax2.set_ylim(.1,30)
    ax3.set_ylim(.5,500)
    
    # add some reference slopes
    xx = np.logspace(np.log10(10),np.log10(1000),100)
    ax1.plot(xx,2000/xx,'-k', label=r'$Q_{prism}^{-1}$',alpha=.5,linewidth=2)
    ax1.plot(xx,xx/3,'--k', label=r'$Q_{prism}^{-1}$',alpha=.5,linewidth=2)
    ax2.plot(xx,5000/xx**2,'-k', label=r'$Q_{prism}^{-2}$',alpha=.5,linewidth=2)
    ax3.plot(xx,1e7/xx**3,'-k', label=r'$Q_{prism}^{-2}$',alpha=.5,linewidth=2)
        
    bb = {'facecolor': 'w', 'edgecolor': 'None', 'alpha': 0.8}
    ax1.text(.83,.9,r'~$Q_{prism}^{+1}$',transform=ax1.transAxes,
        fontweight='bold',alpha=.5,ha='center',bbox=bb)
    ax1.text(.8,.05,r'~$Q_{prism}^{-1}$',transform=ax1.transAxes,
        fontweight='bold',alpha=.5,ha='center',bbox=bb)
    ax2.text(.67,.05,r'~$Q_{prism}^{-2}$',transform=ax2.transAxes,
        fontweight='bold',alpha=.5,ha='center',bbox=bb)
    ax3.text(.63,.05,r'~$Q_{prism}^{-3}$',transform=ax3.transAxes,
        fontweight='bold',alpha=.5,ha='center',bbox=bb)
    

    fig.savefig(out_dir / ('scribble_vs_Qprism_' + gtagex + '.png'))

    plt.show()
    pfun.end_plot()
