"""
Code to make a nice plot for intro figures of the first LiveOcean paper.

"""

from lo_tools import Lfun, zfun,zrfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

from datetime import datetime, timedelta
import numpy as np
import xarray as xr
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import cmocean.cm as cm
import cmcrameri.cm as cmr

# output location
out_dir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef'
Lfun.make_dir(out_dir)

# plotting choices
fs = 18
fs2 = 0.8*fs
fs3 = 0.6*fs2
vn = 'salt'; vmin=24; vmax=34
cmap = cmr.nuuk
aaf = [-125.3, -122.1, 46.8, 50.3] # focus domain

# river colors
rc1 = 'dodgerblue'
rc2 = 'seagreen'

# get map fields
dstr = '2019.07.04'
fn = Ldir['roms_out'] / 'cas6_v0_live' / ('f' + dstr) / 'ocean_his_0020.nc'
ds = xr.open_dataset(fn)
lon, lat = pfun.get_plon_plat(ds.lon_rho.values, ds.lat_rho.values)
v = ds[vn][0,-1,:,:].values

# get river time series
r_df = pd.DataFrame(index=pd.date_range(start='1/1/2017 12:00:00', end='12/31/2019 12:00:00'),
    columns=['fraser','skagit'])
for year in [2017, 2018, 2019]:
    rfn = (Ldir['LOo'] / 'pre'/ 'river' / 'cas6_v3' / 'Data_roms' /
        ('extraction_'+str(year)+'.01.01_'+str(year)+'.12.31.nc'))
    rds = xr.open_dataset(rfn)
    # convert to 1000 m3/s
    rds = rds/1000
    rdt0 = datetime(year,1,1,12)
    rdt1 = datetime(year,12,31,12)
    # and save selected river(s) to the three year DataFrame
    r_df.loc[rdt0:rdt1, 'fraser'] = rds.transport.sel(riv='fraser')
    r_df.loc[rdt0:rdt1, 'skagit'] = rds.transport.sel(riv='skagit')

# PLOTTING
plt.close('all')

pfun.start_plot(fs=fs)
fig = plt.figure(figsize=(13,13))

# -------------- FULL MAP -----------------------------------------------

ax = plt.subplot2grid((4,2), (0,0), rowspan=3)
# cs = ax.pcolormesh(lon[6:-6,6:],lat[6:-6,6:],v[6:-6,6:], cmap=cmap, vmin=vmin, vmax=vmax)
cs = ax.pcolormesh(lon,lat,v, cmap=cmap, vmin=vmin, vmax=vmax)
# nudge_alpha = .1
# ax.pcolormesh(lon[:,:6],lat[:,:6],v[:,:5], cmap=cmap, vmin=vmin, vmax=vmax, alpha=nudge_alpha)
# ax.pcolormesh(lon[:6,:],lat[:6,:],v[:5,:], cmap=cmap, vmin=vmin, vmax=vmax, alpha=nudge_alpha)
# ax.pcolormesh(lon[-6:,:],lat[-6:,:],v[-5:,:], cmap=cmap, vmin=vmin, vmax=vmax, alpha=nudge_alpha)
pfun.add_bathy_contours(ax, ds, txt=False)
pfun.add_coast(ax)
ax.axis(pfun.get_aa(ds))
pfun.dar(ax)

# Inset colorbar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
cbaxes = inset_axes(ax, width="4%", height="40%", loc='lower left', borderpad=3) 
cb = fig.colorbar(cs, cax=cbaxes, orientation='vertical')

ax.text(.08, .53, r'Salinity $[g\ kg^{-1}]$', transform=ax.transAxes)
ax.text(.08, .03, dstr, size=fs2, transform=ax.transAxes, style='italic')

ax.set_xticks([-130, -126, -122])
ax.set_yticks([42, 44, 46, 48, 50, 52])

# # add ticks for grid spacing
# x = lon[0,::10]
# y = lat[::10,0]
# for xx in x:
#     ax.plot([xx,xx],[42,42.12],'-k',alpha=.5)
# for yy in y:
#     ax.plot([-122.18, -122],[yy,yy],'-k',alpha=.5)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

pfun.draw_box(ax, aaf, linestyle='-', color='k', alpha=.3, linewidth=3, inset=0)

ax.text(.93,.97,'(a) Full Model Domain', ha='right', va='top', weight='bold',
    transform=ax.transAxes, bbox=dict(facecolor='w', edgecolor='None', alpha=.6))

ax.text(-123.072,46.7866,'Washington', size=fs2,
    style='italic',ha='center',va='center',rotation=-45)
ax.text(-122.996,44.5788,'Oregon', size=fs2,
    style='italic',ha='center',va='center',rotation=-45)
    
ah = ax.text(-125.3,49.4768,'Vancouver\nIsland', size=fs2,
    style='italic',ha='center',va='center',rotation=-45)
ax.text(-126.3,50.2,'Johnstone\nStrait', size=.7*fs2,
    style='italic',ha='center',va='center',rotation=-10)

# -------------- FOCUS MAP -----------------------------------------------

ax = ax = plt.subplot2grid((4,2), (0,1), rowspan=3)
ax.pcolormesh(lon,lat,v, cmap=cmap, vmin=vmin, vmax=vmax)
pfun.add_coast(ax)
ax.axis(aaf)
pfun.dar(ax)

ax.set_xticks([-125, -124, -123])
ax.set_yticks([47, 48, 49, 50])

# # add ticks for grid spacing
# x = lon[0,::4]
# y = lat[::4,0]
# for xx in x:
#     ax.plot([xx,xx],[aaf[2],aaf[2]+.06],'-k',alpha=.5)
# for yy in y:
#     hh = ax.plot([aaf[1]-.08, aaf[1]],[yy,yy],'-k',alpha=.5)

ax.set_xlabel('Longitude')

ax.text(.93,.97,'(b) Salish Sea', ha='right', va='top', size=fs,
    transform=ax.transAxes, weight='bold')

# add labels
ax.text(-122.682,49.335,'Fraser\nRiver',size=fs2,
    style='italic',ha='center',va='center',rotation=0,
    fontweight='bold',color=rc1)
ax.text(-123.7,49.2528,'Strait of Georgia',size=fs2,
    style='italic',ha='center',va='center',rotation=-30,
    color='w')
ax.text(-123.5,48.28,'Strait of Juan de Fuca',size=fs2,
    style='italic',ha='center',va='center',rotation=0,
    color='k')
ax.text(-123.3,47.6143,'Puget\nSound',size=fs2,
    style='italic',ha='center',va='center',rotation=+55)
ax.text(-122.3,48.48,'Skagit\nRiver',size=fs3,
    style='italic',ha='center',va='center',
    bbox=dict(facecolor='w', edgecolor='None',alpha=.5),
    fontweight='bold',color=rc2)
ax.text(-123.173,48.44,'Haro\nStrait',size=fs3,
    style='italic',ha='center',va='center',
    color='k')
    
ds.close()

# -------------- RIVER TIME SERIES --------------------------------------

dt0 = datetime(2017,1,1,0)
dt1 = datetime(2020,1,1,0)


ax = fig.add_subplot(414)

r_df.plot(y='fraser', ax=ax, legend=False,
    xlim=(dt0,dt1), ylim=(0,12), grid=False, linestyle='-', lw=3, color=rc1)
r_df.plot(y='skagit', ax=ax, legend=False,
    xlim=(dt0,dt1), ylim=(0,12), grid=False, linestyle='-', lw=3, color=rc2)

ax.set_xticks([])
ax.set_xticks([], minor=True)
ax.vlines([datetime(2018,1,1),datetime(2019,1,1)],0,15, alpha=.5)

ax.text(.18,.5,'Fraser',color=rc1, transform=ax.transAxes, weight='bold')
ax.text(.12,.14,'Skagit',color=rc2, transform=ax.transAxes, weight='bold')

ax.set_xticks([datetime(2017,1,1),datetime(2017,7,1),datetime(2018,1,1),
    datetime(2018,7,1),datetime(2019,1,1),datetime(2019,7,1),datetime(2019,12,31)])
ax.set_xticklabels(['','2017','','2018','','2019',''], rotation=0,
    fontdict={'horizontalalignment':'center'})

ax.text(.95, .8, '(c) River Flow [$10^{3}\ m^{3}s^{-1}$]',
    transform=ax.transAxes, weight='bold', ha='right',
    bbox=dict(facecolor='w', edgecolor='None'))

fig.tight_layout()
# fig.savefig(out_dir / 'New_Fig1.png')

plt.show()





