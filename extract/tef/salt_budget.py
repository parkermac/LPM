"""
Makes a salt budget for user-specified volumes.  The goal is to
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

#vol_list = ['Puget Sound']
vol_list = ['South Sound', 'Puget Sound']
#vol_list = ['Salish Sea', 'Puget Sound', 'Hood Canal', 'South Sound']

plt.close('all')

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
    elif which_vol == 'Puget Sound':
        seg_list = (flux_fun.ssA + flux_fun.ssM + flux_fun.ssT
            + flux_fun.ssS + flux_fun.ssW + flux_fun.ssH)
        sect_sign_dict = {'ai1':1, 'dp':1}
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
    vn = 'salt'
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
    QSin = 0
    Qout = 0
    QSout = 0
    Qprism = 0
    # sum over all the open sections
    for sect_name in sect_list:
        df = tef_df_dict[sect_name]
        # quantities we use below for derived quantities
        Qin += df['Qin']
        QSin += df['Qin']*df['salt_in']
        Qout += df['Qout']
        QSout += df['Qout']*df['salt_out']
        Qprism += df['qabs']/2
    # derived 
    Sin = QSin / Qin
    Sout = QSout / Qout
    DS = Sin - Sout
    Qr = vol_df['Qr']
    
    # Fill the budget Dataframe
    c_df = pd.DataFrame(index=indall)
    c_df['QinDS'] = Qin * DS / 1000
    c_df['-QrSout'] = - Qr * Sout / 1000
    # We include the time-varying volume term in the storage term
    c_df['Storage'] = cvt_lp / 1000 - vol_df['dV_dt'] * Sout / 1000
    
    # The residual of the budget is the error (Sink is negative)
    c_df['Error'] = c_df['Storage'] - c_df['QinDS'] - c_df['-QrSout']
    
    # add Qprism and Qr, for plotting
    c_df['Qprism'] = Qprism /1000
    c_df['Qr'] = Qr / 1000
    
    # Plotting
    pfun.start_plot()
    fig = plt.figure()
    dt0 = datetime(year,1,1)
    dt1 = datetime(year,12,31)
    lw = 3
    
    ax = fig.add_subplot(211)
    tstr = which_vol + ' Salt Budget'
    c_df[['Storage','QinDS','-QrSout','Error']].plot(ax=ax, title=tstr,
        style={'Storage':'-b', 'QinDS':'-r', '-QrSout':'-g', 'Error':'-c'}, linewidth=lw)
    ax.legend(labels=[r'$Storage^{adj}$', r'$Q_{in}\Delta S$', r'$-Q_{R}S_{out}$', r'$Error$'], ncol=4)
    ax.set_ylabel(r'$[g\ kg^{-1}\ 10^{3}m^{3}s^{-1}]$')
    ax.set_xticklabels([])
    ax.set_xlim(dt0, dt1)
    ax.grid(True)
    
    ax = fig.add_subplot(212)
    ax2 = ax.twinx()
    c_df[['QinDS']].plot(ax=ax, c='r', legend=False, linewidth=lw)
    c_df[['Qprism']].plot(ax=ax2, c='purple', legend=False, linewidth=lw)
    # ax.set_xticklabels([])
    ax.set_xlim(dt0, dt1)
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    ax.grid(axis='x')
    ax2.grid(axis='x')
    ax.set_ylabel(r'$Q_{in}\Delta S\ [g\ kg^{-1}\ 10^{3}m^{3}s^{-1}]$', color='r')
    ax2.set_ylabel(r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color='purple')
    
    # ax = fig.add_subplot(313)
    # ax2 = ax.twinx()
    # c_df[['-QrSout']].plot(ax=ax, c='g')
    # c_df[['Qr']].plot(ax=ax2, style='--g')
    # ax.set_xlim(dt0, dt1)
    # ax2.set_ylim(bottom=0)
    # ax.grid(axis='x')
    # ax2.grid(axis='x')
    
    plt.show()
    pfun.end_plot()

