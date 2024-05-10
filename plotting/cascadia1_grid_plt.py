"""
Code to plot aspects of the cascadia1 grid, for a "dead birds" paper
by Tim Jones. 2024.03.25
"""

import xarray as xr
from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
import numpy as np
import cmocean.cm as cm

Ldir = Lfun.Lstart()
in_dir = Ldir['parent'] / 'LiveOcean_OLD' / 'LiveOcean_data' / 'grids' / 'cascadia1'
grid_fn = in_dir / 'grid.nc'
s_fn = in_dir / 'S_COORDINATE_INFO.csv'
s_dict = Lfun.csv_to_dict(s_fn)
S = zrfun.get_S(s_dict)
G = zrfun.get_basic_info(grid_fn, only_G=True)
DXY = np.sqrt(G['DX']*G['DX'] + G['DY']*G['DY'])
DXY[G['mask_rho']==0] = np.nan
plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
zr, zw = zrfun.get_z(G['h'], 0*G['h'], S)
dz = np.diff(zw,axis=0)
dz0 = dz[-1,:,:]
dz0[G['mask_rho']==0] = np.nan
ds = xr.open_dataset(grid_fn)
aa = pfun.get_aa(ds)

out_dir = out_fn = Ldir['parent'] / 'LPM_output' / 'plotting'
Lfun.make_dir(out_dir)
out_fn = out_dir / 'cascadia1_grid_info.png'


# plotting
plt.close('all')
pfun.start_plot(figsize=(15,10))
fig = plt.figure()

ax = fig.add_subplot(121)
cs = ax.pcolormesh(plon,plat,DXY,vmin=2500,vmax=5000,cmap=cm.speed_r)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_xlabel('Longitude (deg)')
ax.set_ylabel('Latitude (deg)')
ax.text(.05,.05,'(a) Grid Resolution\nHypotenuse [m]',fontweight='bold',va='bottom',ha='left',
    transform=ax.transAxes, bbox = pfun.bbox)
pfun.add_coast(ax)
ax.axis(aa)

ax = fig.add_subplot(122)
cs = ax.pcolormesh(plon,plat,dz0,vmin=2,vmax=14,cmap=cm.deep_r)
fig.colorbar(cs, ax=ax)
pfun.dar(ax)
ax.set_yticklabels([])
ax.set_xlabel('Longitude (deg)')
ax.text(.05,.05,'(b) Top Layer\nThickness [m]',fontweight='bold',va='bottom',ha='left',
    transform=ax.transAxes, bbox = pfun.bbox)
pfun.add_coast(ax)
ax.axis(aa)


plt.show()
pfun.end_plot()

fig.savefig(out_fn)