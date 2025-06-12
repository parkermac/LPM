"""
One-off code to compare the results of x9b and x10ab.
"""

import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np
import gsw

from lo_tools import Lfun
Ldir = Lfun.Lstart()

from lo_tools import plotting_functions as pfun

ex_name = 'hoodsport_2017.01.01_2017.11.15.nc'
gtx_list = ['cas7_t0_x4b', 'cas7_t0_x9b', 'cas7_t1_x10ab']
gtx_colors = {'cas7_t0_x4b':'r', 'cas7_t0_x9b':'b', 'cas7_t1_x10ab':'g'}

plt.close('all')
pfun.start_plot(figsize=(22,8))
fig = plt.figure()

vn_list = ['NO3', 'oxygen' ,'TIC', 'alkalinity','Omega','pCO2']
nvn = len(vn_list)

def make_co2sys_vars(z,lon,lat,SA,CT,TIC,TA):
    import gsw
    # See LPM/co2sys_test/test0.py for info.
    import PyCO2SYS as pyco2
    # calculate and add Aragonite Saturation State

    # Calculate derived quantities
    p = gsw.p_from_z(z, lat)
    SP = gsw.SP_from_SA(SA, p, lon, lat)
    rho = gsw.rho(SA, CT, p) # in situ density
    temp = gsw.t_from_CT(SA, CT, p) # in situ temperature
    # convert from umol/L to umol/kg using in situ dentity
    TA1 = 1000 * TA / rho
    TA1[TA1 < 100] = np.nan
    TIC1 = 1000 * TIC / rho
    TIC1[TIC1 < 100] = np.nan
    CO2dict = pyco2.sys(par1=TA1, par2=TIC1, par1_type=1, par2_type=2,
        salinity=SP, temperature=temp, pressure=p,
        total_silicate=50, total_phosphate=2,
        opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)

    Omega = CO2dict['saturation_aragonite']
    pCO2 = CO2dict['pCO2'] # pCO2 (uatm)
    return Omega, pCO2

gg = 0
ax_dict = dict()
for gtx in gtx_list:
    fn = Ldir['LOo'] / 'extract' / gtx / 'moor' / ex_name
    ds = xr.open_dataset(fn)
    ot = ds.ocean_time.to_numpy()

    lon = float(ds.lon_rho.to_numpy())
    lat = float(ds.lat_rho.to_numpy())
    nz = 0
    z = float(ds.z_rho[0,nz].to_numpy().squeeze())
    SP = ds['salt'][:, nz].to_numpy().squeeze()
    PT = ds['temp'][:,nz].to_numpy().squeeze()
    TIC = ds['TIC'][:,nz].to_numpy().squeeze()
    TA = ds['alkalinity'][:,nz].to_numpy().squeeze()
    p = gsw.p_from_z(z, lat)
    SA = gsw.SA_from_SP(SP, p, lon, lat)
    CT = gsw.CT_from_pt(SA, PT)

    Omega, pCO2 = make_co2sys_vars(z,lon,lat,SA,CT,TIC,TA)

    ii = 0
    jj_list = [1,2,4,5,7,8]
    for vn in vn_list:

        if gtx == gtx_list[0]:
            ax_dict[ii] = fig.add_subplot(3,3,jj_list[ii])
        ax = ax_dict[ii]

        if vn in ['NO3', 'oxygen' ,'TIC', 'alkalinity']:
            ax.plot(ot,ds[vn][:, nz].to_numpy(),'-'+gtx_colors[gtx])
        elif vn == 'Omega':
            ax.plot(ot,Omega,'-'+gtx_colors[gtx])
        elif vn == 'pCO2':
            ax.plot(ot,pCO2,'-'+gtx_colors[gtx])


        if jj_list[ii] in [7,8]:
            pass
        else:
            ax.set_xticklabels([])

        ax.text(.05,.9,vn,transform=ax.transAxes,fontweight='bold')
        
        if vn == 'NO3':
            ax.text(.95,.9-gg*.1,gtx,color=gtx_colors[gtx],transform=ax.transAxes,fontweight='bold',ha='right')

        ii += 1
    gg += 1

# also make a map - could be spiffier
ax = fig.add_subplot(1,3,3)
gfn = Ldir['data'] / 'grids' / 'cas7' / 'grid.nc'
gds = xr.open_dataset(gfn)
x = gds.lon_rho.to_numpy()
y = gds.lat_rho.to_numpy()
h = gds.h.to_numpy()
m = gds.mask_rho.to_numpy()
h[m==0] = np.nan
px, py = pfun.get_plon_plat(x,y)
mx = float(ds.lon_rho.to_numpy())
my = float(ds.lat_rho.to_numpy())
cs = ax.pcolormesh(px,py,-h,cmap='terrain',vmin=-200, vmax = 0)
fig.colorbar(cs,ax=ax)
ax.contour(x,y,-h,[-200,-100],colors='w',linestyles='-')
pfun.add_coast(ax)
pad = .5
ax.axis([mx-pad, mx+pad, my-pad, my+pad])
pfun.dar(ax)
ax.plot(mx,my,'*r',markersize=20,markeredgecolor='k')
ax.set_title('Mooring Location')

plt.show()
pfun.end_plot()
