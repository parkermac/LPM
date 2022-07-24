"""
Makes an NO3 budget for user-specified volumes.  The goal is to
explore the Spring-Neap variability of terms, and eventually to
understand the physical control on the exchange flow.

An important step here is that we "adjust" the storage term to
absorb the dV/dt term, which makes the results clearer.

Modified from LO/extract/tef/tracer_budget.py.

"""

import sys
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

import matplotlib.pyplot as plt
import numpy as np
import pickle
import pandas as pd
import argparse
import xarray as xr
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--gridname', type=str, default='cas6')
parser.add_argument('-t', '--tag', type=str, default='v3')
parser.add_argument('-x', '--ex_name', type=str, default='lo8b')
parser.add_argument('-yr', '--year', type=int, default=2018)
parser.add_argument('-test', '--testing', type=zfun.boolean_string, default=False)
args = parser.parse_args()
testing = args.testing
year = args.year

# Get Ldir
Ldir = Lfun.Lstart(gridname=args.gridname, tag=args.tag, ex_name=args.ex_name)

# more imports
pth = str(Ldir['LO'] / 'extract' /'tef')
if pth not in sys.path:
    sys.path.append(pth)
import tef_fun
import flux_fun

if args.testing:
    vol_list = ['Puget Sound']
else:
    vol_list = ['Salish Sea', 'Strait of Georgia', 'Puget Sound',
        'Puget Sound no AI', 'Hood Canal', 'South Sound']

# output location
out_dir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef' / 'no3_budgets'
Lfun.make_dir(out_dir)

plt.close('all')

vn = 'NO3'

for which_vol in vol_list:

    year_str = str(year)
    date_str = '_' + year_str + '.01.01_' + year_str + '.12.31'
    
    # get paths to all required data [For cas6_v3_lo8b I have 2017-2020]
    riv_fn = Ldir['LOo'] / 'pre' / 'river' / Ldir['gtag'] / 'Data_roms' / ('extraction' + date_str + '.nc')
    tef_dir = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('bulk' + date_str)
    seg_fn = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' / ('segments' + date_str + '.nc')
    vol_dir = Ldir['LOo'] / 'extract' / 'tef' / ('volumes_' + Ldir['gridname'])

    # Info specific to each volume
    # The sign for each section indicates which direction is INTO the volume.
    if which_vol == 'Salish Sea':
        seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
            + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH
            + flux_fun.ssJ + flux_fun.ssG)
        sect_sign_dict = {'jdf1':1, 'sog5':-1}
    elif which_vol == 'Strait of Georgia':
        seg_list = (flux_fun.ssG)
        sect_sign_dict = {'sji1':1, 'sog5':-1}
    elif which_vol == 'Puget Sound':
        seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
            + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH)
        sect_sign_dict = {'ai1':1, 'dp':1}
    elif which_vol == 'Puget Sound no AI':
        seg_list = (flux_fun.ssM + flux_fun.ssT
            + flux_fun.ssS + flux_fun.ssW)
        sect_sign_dict = {'ai4':1, 'dp':1}
    elif which_vol == 'Hood Canal':
        seg_list = flux_fun.ssH
        sect_sign_dict = {'hc1':-1}
    elif which_vol == 'South Sound':
        seg_list = flux_fun.ssT + flux_fun.ssS
        sect_sign_dict = {'tn1':-1}

    # SECTION INFO
    sect_df = tef_fun.get_sect_df(Ldir['gridname'])

    # RIVERS
    """
    These are stored in an xr.Dataset:
    time = daily, noon of each day
    riv = river names
    variable names: transport + all the tracers in tef_fun.vn_list
    """
    river_list = []
    for seg_name in seg_list:
        seg = flux_fun.segs[seg_name]
        river_list = river_list + seg['R']
    riv_ds = xr.open_dataset(riv_fn)
    riv_ds = riv_ds.sel(riv=river_list)

    # TEF at SECTIONS
    tef_df_dict = dict()
    sect_list = list(sect_sign_dict.keys())
    for sn in sect_list:
        tef_df_dict[sn], in_sign, _, _ = flux_fun.get_two_layer(tef_dir, sn, Ldir['gridname'])
        if in_sign != sect_sign_dict[sn]:
            print('WARNING: potential sign error!!')
            
    # SEGMENT TIME SERIES
    """
    These are stored in an xr.Dataset:
    time = hourly (so we lowpass, subsample, and clip the ends)
    seg = segment names
    variable names = volume + all the tracers in tef_fun.vn_list
    - note that the tracers are the average in each volume
    """
    pad = 36
    
    seg_ds = xr.open_dataset(seg_fn)
    seg_ds = seg_ds.sel(seg=seg_list)
    
    seg_NT = len(seg_ds.coords['time'])
    nanvec = np.nan * np.ones(seg_NT)
    
    # rate of change of volume
    vt = nanvec.copy()
    vt[1:-1] = (seg_ds.volume[2:].values - seg_ds.volume[:-2].values).sum(axis=1)/(2*3600)
    vt_lp = zfun.lowpass(vt, f='godin')[pad:-pad+1:24]
    
    # volume
    v = zfun.lowpass(seg_ds.volume.values, f='godin')[pad:-pad+1:24]
    vnet = v.sum(axis=1)
    V = vnet.mean() # average total volume
        
    # rate of change of volume-integrated tracer (sum(C*v)/sec)
    cvt_lp_dict = {}
    cvt = nanvec.copy()
    cvt[1:-1] = (seg_ds.volume[2:].values*seg_ds[vn][2:].values
        - seg_ds.volume[:-2].values*seg_ds[vn][:-2].values).sum(axis=1)/(2*3600)
    cvt_lp = zfun.lowpass(cvt, f='godin')[pad:-pad+1:24]
                
    # BUDGETS
    
    # time index to use
    indall = tef_df_dict[sect_list[0]].index

    # Volume budget
    vol_df = pd.DataFrame(0, index=indall, columns=['Qin','Qout'])
    for sect_name in sect_list:
        df = tef_df_dict[sect_name]
        vol_df['Qin'] = vol_df['Qin'] + df['Qin']
        vol_df['Qout'] = vol_df['Qout'] + df['Qout']
    vol_df['Qr'] = riv_ds.transport.sum(axis=1)[1:-1]
    vol_df.loc[:, 'dV_dt'] = vt_lp
    vol_df['Error'] = vol_df['dV_dt'] - vol_df.loc[:,'Qin'] - vol_df.loc[:,'Qout'] - vol_df.loc[:,'Qr']
    vol_rel_err = vol_df['Error'].mean()/vol_df['Qr'].mean()

    # Tracer budget
    Qin = 0
    QCin = 0
    Qout = 0
    QCout = 0
    Qprism = 0
    # sum over all the open sections
    for sect_name in sect_list:
        df = tef_df_dict[sect_name]
        # quantities we use below for derived quantities
        Qin += df['Qin']
        QCin += df['Qin']*df[vn+'_in']
        Qout += df['Qout']
        QCout += df['Qout']*df[vn+'_out']
        Qprism += df['qabs']/2
    # derived 
    Cin = QCin / Qin
    Cout = QCout / Qout
    DC = Cin - Cout
    Qr = vol_df['Qr']
    QrCr = (riv_ds.transport * riv_ds[vn]).sum(axis=1)[1:-1]
    
    # Fill the budget Dataframe
    c_df = pd.DataFrame(index=indall)
    c_df['QinDC'] = Qin * DC / 1000
    c_df['-QrCout'] = - Qr * Cout / 1000
    c_df['QrCr'] = QrCr / 1000
    # We include the time-varying volume term in the storage term
    c_df['Storage'] = cvt_lp / 1000 - vol_df['dV_dt'] * Cout / 1000
    
    # The residual of the budget is the error (Sink is negative)
    c_df['Source/Sink'] = c_df['Storage'] - c_df['QinDC'] - c_df['-QrCout'] - c_df['QrCr']
    
    # add other things for plotting
    c_df['Qprism'] = Qprism /1000
    c_df['Qr'] = Qr / 1000
    c_df['Qin'] = Qin / 1000
    c_df['DC'] = DC
    c_df['QCin'] = QCin / 1000
    c_df['QCout'] = QCout / 1000
    
    c_df['OceanNet'] = c_df['QinDC'] + c_df['-QrCout']
    c_df['OceanNet_check'] = c_df['QCin'] + c_df['QCout']
    
    # print some annual means
    uMkm3s_to_kgd = 1209.6 # convert uM N 10^3 m3/s to kg/d
    print('\n' + which_vol)
    for term in ['Storage','OceanNet','OceanNet_check','QrCr','Source/Sink','QCin','QCout']:
        print('Annual mean %s = %d [kg d-1]' % (term, int(c_df[term].mean()*uMkm3s_to_kgd)) )
    
    
    # Plotting
    pfun.start_plot(fs=18, figsize=(18,12))
    
    fig = plt.figure()
    dt0 = datetime(year,1,1)
    dt1 = datetime(year,12,31)
    lw = 3
    
    cSto = 'b'
    cON = 'r'
    cQrCr = 'darkorange'
    cSS = 'g'
    
    cprism = 'c'
    cQCin = 'k'
    cQCout = 'gray'
    
    Nrow = 2
    
    ax = fig.add_subplot(Nrow,1,1)
    tstr = which_vol + ' DIN Budget'
    c_df[['Storage','OceanNet','QrCr','Source/Sink']].plot(ax=ax, title=tstr,
        style={'Storage':cSto, 'OceanNet':cON, 'QrCr':cQrCr, 'Source/Sink':cSS}, linewidth=lw)
    ax.legend(labels=['Storage Rate', 'Net Ocean DIN Flux', 'Net River DIN Flux', 'Source/Sink'],
        loc='lower right', ncol=4)
    ax.set_ylabel(r'$[uM\ N\ 10^{3}m^{3}s^{-1}]$')
    ax.set_xticklabels([])
    ax.set_xlim(dt0, dt1)
    ax.grid(True)
    ax.axhline(color='k')
    
    ax = fig.add_subplot(Nrow,1,2)
    c_df[['QCin','OceanNet','QCout']].plot(ax=ax,
        style={'QCin':cQCin, 'OceanNet':cON, 'QCout':cQCout}, linewidth=lw)
    ax.legend(labels=['Ocean Import Flux', 'Net Ocean Flux', 'Ocean Export Flux'],
        loc='lower center', ncol=4)
    ax.set_ylabel(r'$[uM\ N\ 10^{3}m^{3}s^{-1}]$')
    ax.set_xlim(dt0, dt1)
    ax.grid(True)
    ax.axhline(color='k')
    
    # ax = fig.add_subplot(Nrow,1,2)
    # ax2 = ax.twinx()
    # c_df[['OceanNet']].plot(ax=ax, c=cON, legend=False, linewidth=lw)
    # c_df[['Qprism']].plot(ax=ax2, c=cprism, legend=False, linewidth=lw)
    # ax.set_xticklabels([])
    # ax.set_xlim(dt0, dt1)
    # # ax.set_ylim(bottom=0)
    # ax2.set_ylim(bottom=0)
    # ax.grid(axis='x')
    # ax2.grid(axis='x')
    # ax.text(.05,.1,r'$Q_{in}\Delta C-Q_{R}C_{out}\ [uM\ 10^{3}m^{3}s^{-1}]$', color=cON, transform=ax.transAxes,
    #     bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    # ax2.text(.95,.1,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism, transform=ax.transAxes, ha='right',
    #     bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    # ax.axhline(color=cQinDC)
    #
    # if True:
    #     ax = fig.add_subplot(Nrow,1,3)
    #     ax2 = ax.twinx()
    #     c_df[['Qin']].plot(ax=ax, c=cQin, legend=False, linewidth=lw)
    #     c_df[['Qprism']].plot(ax=ax2, c=cprism, legend=False, linewidth=lw)
    #     # ax.set_xticklabels([])
    #     ax.set_xlim(dt0, dt1)
    #     ax.set_ylim(bottom=0)
    #     ax2.set_ylim(bottom=0)
    #     ax.grid(axis='x')
    #     ax2.grid(axis='x')
    #     ax.text(.05,.1,r'$Q_{in}\ [10^{3}m^{3}s^{-1}]$', color=cQin, transform=ax.transAxes,
    #         bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    #     ax2.text(.95,.1,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism, transform=ax.transAxes, ha='right',
    #         bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    # else:
    #     ax = fig.add_subplot(Nrow,1,3)
    #     ax2 = ax.twinx()
    #     c_df[['Source/Sink']].plot(ax=ax, c=cSS, legend=False, linewidth=lw)
    #     c_df[['Qprism']].plot(ax=ax2, c=cprism, legend=False, linewidth=lw)
    #     # ax.set_xticklabels([])
    #     ax.set_xlim(dt0, dt1)
    #     #ax.set_ylim(bottom=0)
    #     ax2.set_ylim(bottom=0)
    #     ax.grid(axis='x')
    #     ax2.grid(axis='x')
    #     ax.text(.05,.1,r'$Source/Sink\ [uM\ 10^{3}m^{3}s^{-1}]$', color=cSS, transform=ax.transAxes,
    #         bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    #     ax2.text(.95,.1,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism, transform=ax.transAxes, ha='right',
    #         bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    #     ax.axhline(color=cSS)
    
    # ax = fig.add_subplot(Nrow,1,4)
    # ax2 = ax.twinx()
    # c_df[['DC']].plot(ax=ax, c=cDC, legend=False, linewidth=lw)
    # c_df[['Qprism']].plot(ax=ax2, c=cprism, legend=False, linewidth=lw)
    # # ax.set_xticklabels([])
    # ax.set_xlim(dt0, dt1)
    # ax.set_ylim(bottom=0)
    # ax2.set_ylim(bottom=0)
    # ax.grid(axis='x')
    # ax2.grid(axis='x')
    # ax.text(.05,.1,r'$\Delta C\ [uM]$', color=cDC, transform=ax.transAxes,
    #     bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    # ax2.text(.95,.1,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color=cprism, transform=ax.transAxes, ha='right',
    #     bbox=dict(facecolor='w', edgecolor='None', alpha=.6))
    
    fig.tight_layout()
    fig.savefig(out_dir / (which_vol.replace(' ','_') + '.png'))
    
    plt.show()
    pfun.end_plot()

