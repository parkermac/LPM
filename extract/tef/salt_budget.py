"""
Makes a salt budget for user-specified volumes.  The goal is to
explore the Spring-Neap variability of terms, and eventually to
understand the physical control on the exchange flow.

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

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--gridname', type=str, default='cas6')
parser.add_argument('-t', '--tag', type=str, default='v3')
parser.add_argument('-x', '--ex_name', type=str, default='lo8b')
parser.add_argument('-yr', '--year', type=int, default=2018)
parser.add_argument('-test', '--testing', type=zfun.boolean_string, default=True)
args = parser.parse_args()
testing = args.testing
year = args.year

# Get Ldir
Ldir = Lfun.Lstart(gridname=args.gridname, tag=args.tag, ex_name=args.ex_name)

# more imports
sys.path.append(str(Ldir['LO'] / 'extract' /'tef'))
import tef_fun
import flux_fun

if testing:
    vol_list = ['Puget Sound']
else:
    vol_list = ['Salish Sea', 'Puget Sound', 'Hood Canal']

for which_vol in vol_list:

    year_str = str(year)
    date_str = '_' + year_str + '.01.01_' + year_str + '.12.31'

    # out_dir = (Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef' /
    #     ('Budgets_' + which_vol.replace(' ','_') + '_' + year_str))
    # Lfun.make_dir(out_dir, clean=True)
    
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

    # SECTION INFO
    sect_df = tef_fun.get_sect_df(Ldir['gridname'])

    # RIVERS
    """
    These are now stored in an xr.Dataset:
    time = daily, noon of each day
    riv = river names
    variable names: transport + all the tracers in tef_fun.vn_list
    """
    river_list = []
    for seg_name in seg_list:
        seg = flux_fun.segs[seg_name]
        river_list = river_list + seg['R']
    riv_ds = xr.load_dataset(riv_fn)
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
    These are now stored in an xr.Dataset:
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
    for vn in ['salt']:#tef_fun.vn_list:
        cvt = nanvec.copy()
        cvt[1:-1] = (seg_ds.volume[2:].values*seg_ds[vn][2:].values
            - seg_ds.volume[:-2].values*seg_ds[vn][:-2].values).sum(axis=1)/(2*3600)
        cvt_lp_dict[vn] = zfun.lowpass(cvt, f='godin')[pad:-pad+1:24]
        
    # volume- and time-averaged tracer
    vmean_dict = dict()
    for vn in ['salt']:#tef_fun.vn_list:
        vmean_dict[vn] = ((seg_ds.volume*seg_ds[vn]).sum(axis=1)/V).mean().values
        
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

    # Tracer budgets
    # F is the "flux" of a tracer, with units [tracer units]*m3/s
    # Ftot, Fin, and Fout are at the ocen boundaries of the volume.  Fout is negative.
    C = dict()
    # The "normalized" budgets are averaged over a year, multiplied by a year of seconds,
    # and divided by the mean volume, so they have units [tracer units].  So Cnorm['NO3']['dFnet_dt']
    # is the change in total mean Nitrate over the year, and the other terms in Cnorm['NO3'] tell you where
    # that change came from.  I'm not sure this is the right normalization to use.
    # Cnorm = dict()
    for vn in ['salt']:#tef_fun.vn_list:
        c_df = pd.DataFrame(0, index=indall, columns=['Ftot','Fin','Fout', 'QinDS', 'QrSout'])
        Qin = 0
        QSin = 0
        Qout = 0
        QSout = 0
        for sect_name in sect_list:
            df = tef_df_dict[sect_name]
            c_df['Ftot'] = c_df['Ftot'] + df['Qin']*df[vn+'_in'] + df['Qout']*df[vn+'_out']
            c_df['Fin'] = c_df['Fin'] + df['Qin']*df[vn+'_in']
            c_df['Fout'] = c_df['Fout'] + df['Qout']*df[vn+'_out']
            
            # custom salt budget things
            Qin += df['Qin']
            QSin += df['Qin']*df['salt_in']
            Qout += df['Qout']
            QSout += df['Qout']*df['salt_out']
            
        Sin = QSin / Qin
        Sout = QSout / Qout
        DS = Sin - Sout
        Qr_adj = vol_df['Qr'] - vol_df['dV_dt']
        c_df['QinDS'] = Qin * DS
        c_df['QrSout'] = Qr_adj * Sout
            
        c_df['Fr'] = (riv_ds.transport * riv_ds[vn]).sum(axis=1)[1:-1]
        c_df.loc[:, 'dFnet_dt'] = cvt_lp_dict[vn]
        # the residual of the budget is assumed to be an unresolved Source or Sink (Sink is negative)
        # e.g. due to air-sea gas transfer, denitrification, or internal conversion to another tracer.
        #c_df['Source/Sink'] = c_df['dFnet_dt'] - c_df['Ftot'] - c_df['Fr']
        c_df['Source/Sink'] = c_df['dFnet_dt'] - c_df['QinDS'] + c_df['QrSout']
        C[vn] = c_df.copy()
        
        # cn = c_df.mean()*(365*86400)/V
        # cn = cn.rename({'dFnet_dt':'Change in Concentration', 'Ftot':'Inflow+Outflow',
        #     'Fin':'Inflow', 'Fout':'Outflow', 'Fr':'River'})
        # cn = cn[['Change in Concentration', 'Inflow', 'Outflow', 'Inflow+Outflow', 'River','Source/Sink']]
        # cn['Mean Concentration'] = vmean_dict[vn]
        # Cnorm[vn] = cn
        
    # C['Ntot'] = C['NO3']+C['phytoplankton']+C['zooplankton']+C['detritus']+C['Ldetritus']
    # Cnorm['Ntot'] = Cnorm['NO3']+Cnorm['phytoplankton']+Cnorm['zooplankton']+Cnorm['detritus']+Cnorm['Ldetritus']
    
    plt.close('all')
    pfun.start_plot()
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    tstr = which_vol + ' Volume Budget [m3/s]'
    vol_df.plot(ax=ax, grid=True, title=tstr)
    if testing:
        plt.show()
    else:
        fig.savefig(out_dir / 'volume.png')
        
    for vn in C.keys():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        tstr = which_vol + ' ' + vn + ' Budget [g/kg m3/s]'
        # C[vn][['dFnet_dt','Ftot','Fr','Source/Sink']].plot(ax=ax, grid=True, title=tstr)
        C[vn][['dFnet_dt','QinDS','QrSout','Source/Sink']].plot(ax=ax, grid=True, title=tstr)
        if testing:
            #pass
            plt.show()
        else:
            fig.savefig(out_dir / (vn + '.png'))

    # # text output
    # with open(out_dir / ('Annual_Mean_' + which_vol.replace(' ','_') + '_' + year_str + '.txt'), 'w') as fout:
    #     for vn in C.keys():
    #         tstr = ' ' + which_vol + ' ' + vn + ' Annual Mean [' + units_dict[vn] + '] '
    #         fout.write(tstr.center(51,'=') + '\n')
    #         for k in Cnorm[vn].keys():
    #             fout.write('%25s %25.3f\n' % (k, Cnorm[vn][k]))
        
    pfun.end_plot()

