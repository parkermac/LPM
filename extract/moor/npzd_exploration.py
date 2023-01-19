"""
Code to explore npzd things from a mooring. For example,
how does new water column remineralization compare with
benthic remineralization?

"""
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun
Ldir = Lfun.Lstart()

sn = 'CE02' # ['CE02', 'ORCA_Hoodsport', 'JdF_west','Willapa','dabob']
date_str = '2017.01.01_2017.12.31'

plt.close('all')
pfun.start_plot(figsize=(18,10))
fig1, axes1 = plt.subplots(nrows=4,ncols=1,squeeze=False)

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
    
    # make mean z and dz vectors
    zr = ds.z_rho.values.mean(axis=0)
    zw = ds.z_w.values.mean(axis=0)
    dz = np.diff(zw)
    N = len(dz)
    DZ = dz.reshape((1,N))
    H = dz.sum()
    
    # find index of top 20 m (or top half if too shallow)
    hh = min(20,H/2)
    iz = zfun.find_nearest_ind(zr,-hh)
    dzbot = dz[:iz]
    dztop = dz[iz:]
    Nbot = len(dzbot)
    Ntop = len(dztop)
    Hbot = dzbot.sum()
    Htop = dztop.sum()
    DZbot = dz[:iz].reshape((1,Nbot))
    DZtop = dz[iz:].reshape((1,Ntop))
    
    if old:
        sd_vn = 'detritus'
        ld_vn = 'Ldetritus'
    else:
        sd_vn = 'SdetritusN'
        ld_vn = 'LdetritusN'

    # estimate the model benthic fluxes
    sdet = ds[sd_vn][:,0].values
    ldet = ds[ld_vn][:,0].values
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

    # basic time series
    ii = 0
    vn_list = ['phytoplankton','DIN','Det','Net']
    for vn in vn_list:
        ax = axes1[ii,0]
        if vn == 'DIN':
            if old:
                v = ds.NO3.values
            else:
                v = ds.NO3.values + ds.NH4.values
        elif vn == 'Det':
                v = ds[sd_vn].values + ds[ld_vn].values
        elif vn == 'Net':
            if old:
                v = ds.NO3.values + ds[sd_vn].values + ds[ld_vn].values + ds.phytoplankton.values
            else:
                v = ds.NO3.values + ds.NH4.values + ds[sd_vn].values + ds[ld_vn].values + ds.phytoplankton.values
        else:
            v = ds[vn].values
        V = np.sum(v * DZ, axis=1)/H
        Vbot = np.sum(v[:,:iz] * DZbot, axis=1)/Hbot
        Vtop = np.sum(v[:,iz:] * DZtop, axis=1)/Htop
        ax.plot(T,Vbot,'--'+c)
        ax.plot(T,Vtop,'-'+c)
        if vn == 'DIN':
            ax.plot(T, V[0] - np.cumsum(f_no3)/H,':'+c)
        if not old:
            ax.grid(True)
            ax.text(.05,.9,vn, fontweight='bold', transform=ax.transAxes)
            ax.set_xlim(T[0],T[-1])
        ii += 1
    

fig1.suptitle(sn + ': Red = Old, Blue = New')
    
pfun.end_plot()
plt.show()
