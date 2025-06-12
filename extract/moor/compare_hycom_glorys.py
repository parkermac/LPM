"""
One-off code to compare the results of hycom vs. glorys forcing.
"""

import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np

from lo_tools import Lfun
Ldir = Lfun.Lstart()

from lo_tools import plotting_functions as pfun

ex_name = 'test_2017.01.01_2017.06.21.nc'
fn0 = Ldir['LOo'] / 'extract' / 'cas7_t0_x4b' / 'moor' / ex_name
fn1 = Ldir['LOo'] / 'extract' / 'cas7_t1_x4a' / 'moor' / ex_name

ds0 = xr.open_dataset(fn0)
ds1 = xr.open_dataset(fn1)
ot = ds0.ocean_time.to_numpy()

plt.close('all')
pfun.start_plot(figsize=(22,8))
fig = plt.figure()

vn_list = ['zeta', 'salt', 'temp', 'u', 'v']
nvn = len(vn_list)

ii = 0
jj_list = [1,2,4,5,7,8]
for vn in vn_list:
    ax = fig.add_subplot(3,3,jj_list[ii])

    if vn == 'zeta':
        ax.plot(ot,ds0[vn].to_numpy(),'--r')
        ax.plot(ot,ds1[vn].to_numpy(),'-r')
    else:
        ax.plot(ot,ds0[vn][:, -1].to_numpy(),'--r')
        ax.plot(ot,ds0[vn][:, 0].to_numpy(),'--b')
        ax.plot(ot,ds1[vn][:, -1].to_numpy(),'-r')
        ax.plot(ot,ds1[vn][:, 0].to_numpy(),'-b')

    if jj_list[ii] in [7,8]:
        pass
    else:
        ax.set_xticklabels([])

    ax.text(.05,.9,vn,transform=ax.transAxes,fontweight='bold')

    if vn == 'temp':
        ax.text(.95,.5,'Surface',color='r',transform=ax.transAxes,fontweight='bold',ha='right',bbox=pfun.bbox)
        ax.text(.95,.2,'Bottom',color='b',transform=ax.transAxes,fontweight='bold',ha='right',bbox=pfun.bbox)
    
    if vn == 'salt':
        ax.text(.3,.1,'Dashed = Old, Solid = New',color='m',transform=ax.transAxes,fontweight='bold',bbox=pfun.bbox)

    ii += 1

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
mx = float(ds0.lon_rho.to_numpy())
my = float(ds0.lat_rho.to_numpy())
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
