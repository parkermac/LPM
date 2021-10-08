"""
Make a grid plot for the MURI Proposal.
2021.09.14
"""
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()
# model output
fn = Ldir['parent'] / 'LiveOcean_roms' / 'output' / 'cas6_v3_lo8b' / 'f2019.07.04' / 'ocean_his_0020.nc'

g2 = Ldir['data'] / 'grids' / 'hc0' / 'grid.nc'

# PLOTTING
plt.close('all')

# START
fs = 14
pfun.start_plot(fs=fs, figsize=(12,9))
fig = plt.figure()
ds = xr.open_dataset(fn)

# PREPARING FIELDS
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

T = zrfun.get_basic_info(fn, only_T=True)
x = ds.lon_psi.values
y = ds.lat_psi.values
th = ds['temp'][0,-1,1:-1,1:-1].values
H = ds.h.values
mask = ds.mask_rho.values
H[mask==0] = np.nan

# topography
tfn = (Ldir['data'] / 'topo' / 'srtm15' / 'topo15.nc')
tds = xr.open_dataset(tfn)
step = 3
tx = tds['lon'][::step].values
ty = tds['lat'][::step].values
tz = tds['z'][::step,::step].values
tz[tz<0] = np.nan

ds.close()
tds.close()

# LARGE MAP
ax = fig.add_subplot(121)
cmap = 'RdYlBu_r'
cs = ax.pcolormesh(x,y,th, cmap=cmap, vmin=11, vmax=20)
# Inset colorbar
cbaxes = inset_axes(ax, width="4%", height="40%", loc='lower left')
fig.colorbar(cs, cax=cbaxes, orientation='vertical')
cmap = 'gist_earth'
cs = ax.pcolormesh(tx,ty,tz, cmap=cmap, shading='nearest', vmin=-1000, vmax=2000)
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis([-130, -122, 42, 52])
ax.set_xticks([-129, -127, -125, -123])
ax.set_yticks([42, 44, 46, 48, 50, 52])
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
tstr = T['dt'][0].strftime(Lfun.ds_fmt)
ax.text(.98,.99,'LiveOcean', size=fs*1.2,
     ha='right', va='top', weight='bold', transform=ax.transAxes)
ax.text(.98,.95,'Surface water\nTemperature $[^{\circ}C]$\n'+tstr,
     ha='right', va='top', weight='bold', transform=ax.transAxes,
     bbox=dict(facecolor='w', edgecolor='None',alpha=.5))

# box for Hood Canal
aa = [-123.2, -122.5, 47.25, 48]
# draw box on the large map
pfun.draw_box(ax, aa, linestyle='-', color='m', alpha=1, linewidth=2, inset=0)

# SMALL MAP
ds = xr.open_dataset(g2)
plon,plat = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)
h = ds.h.values
mask = ds.mask_rho.values
h[mask==0] = np.nan

ax = fig.add_subplot(122)
ax.pcolormesh(x,y,-H[1:-1,1:-1], cmap='rainbow', vmin=-200, vmax=0, alpha=.3)
cs = ax.pcolormesh(plon, plat,-h, cmap='rainbow', vmin=-200, vmax=0)
# Inset colorbar
cbaxes = inset_axes(ax, width="4%", height="40%", loc='upper left')
fig.colorbar(cs, cax=cbaxes, orientation='vertical')
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis(aa)
ax.set_xticks([ -123, -122.5])
ax.set_yticks([47.5, 48])
ax.set_xlabel('Longitude')
ax.text(.98,.99,'Hood Canal\nBathymetry [m]',
     ha='right', va='top', weight='bold', transform=ax.transAxes,
     bbox=dict(facecolor='w', edgecolor='None',alpha=.5))

fig.tight_layout()

plt.show()