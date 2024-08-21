"""
One-off code to compare the results of cas6_v1_live with cas7_t0_x4b.
"""

import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np

from lo_tools import Lfun
Ldir = Lfun.Lstart()

from lo_tools import plotting_functions as pfun

ex_name = 'JdF_mouth_2024.01.01_2024.08.16.nc'
fn6 = Ldir['LOo'] / 'extract' / 'cas6_v1_live' / 'moor' / ex_name
fn7 = Ldir['LOo'] / 'extract' / 'cas7_t0_x4b' / 'moor' / ex_name

ds6 = xr.open_dataset(fn6)
ds7 = xr.open_dataset(fn7)
ot = ds6.ocean_time.values


plt.close('all')
pfun.start_plot(figsize=(22,8))
fig = plt.figure()

vn_list = ['salt', 'temp', 'NO3', 'oxygen', 'TIC', 'alkalinity']
nvn = len(vn_list)

ii = 0
jj_list = [1,2,4,5,7,8]
for vn in vn_list:
    ax = fig.add_subplot(3,3,jj_list[ii])

    v6_bot = ds6[vn][:, 0].values
    v6_top = ds6[vn][:, -1].values
    v7_bot = ds7[vn][:, 0].values
    v7_top = ds7[vn][:, -1].values

    ax.plot(ot,v6_bot,'--b')
    ax.plot(ot,v6_top,'--r')
    ax.plot(ot,v7_bot,'-b')
    ax.plot(ot,v7_top,'-r')

    if jj_list[ii] in [7,8]:
        pass
    else:
        ax.set_xticklabels([])

    ax.text(.05,.9,vn,transform=ax.transAxes,fontweight='bold')

    if vn == 'temp':
        ax.text(.95,.5,'Surface',color='r',transform=ax.transAxes,fontweight='bold',ha='right',bbox=pfun.bbox)
        ax.text(.95,.2,'Bottom',color='b',transform=ax.transAxes,fontweight='bold',ha='right',bbox=pfun.bbox)
    
    if vn == 'salt':
        ax.text(.3,.1,'Solid = New, Dashed = Old',color='m',transform=ax.transAxes,fontweight='bold',bbox=pfun.bbox)


    ii += 1


# also make a map - could be spiffier
ax = fig.add_subplot(1,3,3)
gfn = Ldir['data'] / 'grids' / 'cas7' / 'grid.nc'
gds = xr.open_dataset(gfn)
x = gds.lon_rho.values
y = gds.lat_rho.values
h = gds.h.values
m = gds.mask_rho.values
h[m==0] = np.nan
px, py = pfun.get_plon_plat(x,y)
mx = float(ds6.lon_rho.values)
my = float(ds6.lat_rho.values)
cs = ax.pcolormesh(px,py,-h,cmap='terrain',vmin=-1000, vmax = 200)
fig.colorbar(cs,ax=ax)
ax.contour(x,y,-h,[-200,-100],colors='w',linestyles='-')
pfun.add_coast(ax)
pad = 1
ax.axis([mx-pad, mx+pad, my-pad, my+pad])
pfun.dar(ax)
ax.plot(mx,my,'*r',markersize=20,markeredgecolor='k')
ax.set_title('Mooring Location')

plt.show()
pfun.end_plot()
