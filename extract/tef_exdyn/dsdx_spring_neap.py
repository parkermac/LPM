"""
Code to make s(z) on multiple sections.

run section_maker -gtx cas6_v0_live -ctag c0 -0 2018.01.01 -1 2018.12.31

"""

import sys
import xarray as xr
import numpy as np
import pickle
from time import time
import pandas as pd
from scipy.stats import binned_statistic
import seawater as sw

import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

from lo_tools import Lfun, zrfun, zfun
from lo_tools import extract_argfun as exfun
Ldir = exfun.intro() # this handles the argument passing

# gctag and location of tef2 section definitions
gctag = Ldir['gridname'] + '_' + Ldir['collection_tag']
tef2_dir = Ldir['LOo'] / 'extract' / 'tef2'

# get sect_df with the section point locations
sect_df_fn = tef2_dir / ('sect_df_' + gctag + '.p')
sect_df = pd.read_pickle(sect_df_fn)

# get the grid file
gds = xr.open_dataset(Ldir['grid'] / 'grid.nc')
lou = gds.lon_u[0,:].values
lau = gds.lat_u[:,0].values
lov = gds.lon_v[0,:].values
lav = gds.lat_v[:,0].values

# create the dict S
S_info_dict = Lfun.csv_to_dict(Ldir['grid'] / 'S_COORDINATE_INFO.csv')
S = zrfun.get_S(S_info_dict)

# where to find the extracted sections
in_dir0 = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'tef2'
in_dir = in_dir0 / ('extractions_' + Ldir['ds0'] + '_' + Ldir['ds1'])

# define the list of sections to work on
sect_list = [item.name for item in in_dir.glob('*.nc')]
sect_list = [item.replace('.nc','') for item in sect_list]

# Define sections to work on.
# Generally choose [seaward, landward]
sect_list = ['ai1','ai2','ai4','ai5','ai6','ai7'] # AI North to South
#sect_list = ['sog7','sog6','sog5','sog4','sog3','sog2'] # SoG North to South
#sect_list = ['jdf1','jdf2','jdf3','jdf4','sji1','sji4'] # JdF to Haro Strait
    
# make vn_list by inspecting the first section
ds = xr.open_dataset(in_dir / (sect_list[0] + '.nc'))
vn_list = [item for item in ds.data_vars \
    if (len(ds[item].dims) == 3) and (item not in ['vel','DZ'])]
ds.close()

print('\nCalculating s(z) on mutiple sections')
print(str(in_dir))

tt00 = time()

stz_dict = dict()
lon_dict = dict()
lat_dict = dict()
lon_vec_dict = dict()
lat_vec_dict = dict()
H_dict = dict()
Qprism_dict = dict()

for sn in sect_list:
    tt0 = time()
    print(sn)

    # load fields
    ds = xr.open_dataset(in_dir / (sn + '.nc'))
    salt_hourly = ds.salt.values
    pad = 36
    salt = zfun.lowpass(salt_hourly, f='godin')[pad:-pad+1:24, :]
    NT, N, P = salt.shape
    
    # # make Qprism
    q = ds['dd'].values * ds['DZ'].values * ds['vel'].values
    qnet = np.nan * np.ones(q.shape[0])
    for tt in range(q.shape[0]):
        qnet[tt] = q[tt,:,:].squeeze().sum()
    qabs = np.abs(qnet)
    qabs_lp = zfun.lowpass(qabs, f='godin')[pad:-pad+1:24]
    Qprism = qabs_lp/2
    Qprism_dict[sn] = Qprism
    
    sdf = sect_df.loc[sect_df.sn==sn,:]
    
    h = ds.h.values
    zr, zw = zrfun.get_z(h, 0*h, S) # packed (z,p)
    zf = zr.flatten() # Note: this does not change with time
    # what if there is only one p?
    H_dict[sn] = h.mean()
    
    # get section area (ssh=0)
    dz = np.diff(zw,axis=0)
    A = np.sum(ds['dd'].values * dz)
    
    # Find mean lat and lon (more work than it should be!).
    lon_vec = np.concatenate((lou[sdf.loc[(sdf.uv=='u'),'i']],lov[sdf.loc[(sdf.uv=='v'),'i']]))
    lat_vec = np.concatenate((lau[sdf.loc[(sdf.uv=='u'),'j']],lav[sdf.loc[(sdf.uv=='v'),'j']]))
    lon_vec_dict[sn] = lon_vec
    lat_vec_dict[sn] = lat_vec
    lo = np.mean(lon_vec)
    la = np.mean(lat_vec)
    lon_dict[sn] = lo
    lat_dict[sn] = la
    
    # Then we want to form a time series of s(z)
    NZ = 100
    s_vs_z = np.nan * np.ones((NT,NZ))
    for tt in range(NT):
        sf = salt[tt,:,:].squeeze().flatten()
        # scipy.stats.binned_statistic(x, values, statistic='mean', bins=10, range=None)
        bs = binned_statistic(zf, sf, statistic='mean', bins=NZ, range=(-500,0))
        s_vs_z[tt,:] = bs.statistic
    bin_edges = bs.bin_edges
    
    ot = ds['time'].to_numpy()
    # do a little massaging of ot
    dti = pd.to_datetime(ot) # a pandas DatetimeIndex with dtype='datetime64[ns]'
    dt = dti.to_pydatetime() # an array of datetimes
    ot = np.array([Lfun.datetime_to_modtime(item) for item in dt])
    ot = ot[pad:-pad+1:24]
    # also make an array of datetimes to save as the ot variable
    otdt = np.array([Lfun.modtime_to_datetime(item) for item in ot])
    
    stz_dict[sn] = s_vs_z
    
# z for plotting
z = bin_edges[:-1] + np.diff(bin_edges)/2

# trim to only use overlapping z range
mask = z == z
Stz_dict = dict() # trimmed version of stz
# mask is initialized as all True
for sn in sect_list:
    s0z = stz_dict[sn][0,:]
    mask = mask & ~np.isnan(s0z)
for sn in sect_list:
    stz = stz_dict[sn]
    Stz_dict[sn] = stz[:,mask]
Z = z[mask] # trimmed version of z
    
Sz_dict = dict() # time-mean of each section s(z)
St_dict = dict() # depth-mean of each section s(t)
for sn in sect_list:
    # Stz is a trimmed array of s(t,z), daily
    Stz = Stz_dict[sn]
    Sz_dict[sn] = np.mean(Stz,axis=0)
    St_dict[sn] = np.nanmean(Stz,axis=1)

# useful time vectors
dti = pd.DatetimeIndex(otdt)
yd = dti.dayofyear
year = otdt[0].year
    
# plotting
plt.close('all')
pfun.start_plot(figsize=(18,12))
fig = plt.figure()

c_list = ['m','r','orange','g','b','violet']
c_dict = dict(zip(sect_list,c_list))

# map
ax = fig.add_subplot(321)
lon0 = lon_vec_dict[sect_list[0]]
lat0 = lat_vec_dict[sect_list[0]]
lon1 = lon_vec_dict[sect_list[-1]]
lat1 = lat_vec_dict[sect_list[-1]]
lonmin = np.min(np.concatenate((lon0,lon1)))
lonmax = np.max(np.concatenate((lon0,lon1)))
latmin = np.min(np.concatenate((lat0,lat1)))
latmax = np.max(np.concatenate((lat0,lat1)))
for sn in sect_list:
    ax.plot(lon_vec_dict[sn], lat_vec_dict[sn], '.',color=c_dict[sn])
pfun.add_coast(ax,color='gray',linewidth=2)
mpad = .2
ax.axis([lonmin-mpad, lonmax+mpad, latmin-mpad, latmax+mpad])
pfun.dar(ax)
ax.text(.05,.9,'(a) Section Locations',color='k',fontweight='bold',
    transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

ax = fig.add_subplot(322)
if False:
    for sn in sect_list:
        ax.plot(Sz_dict[sn],Z,'-',color=c_dict[sn])
    ax.text(.05,.1,'(b) Time-Mean S(z)',color='k',fontweight='bold',
        transform=ax.transAxes,bbox=pfun.bbox)
else:
    # selected spring and neap; hard coded for 2018 Admiralty Inlet
    it_neap = zfun.find_nearest_ind(yd,233)
    it_spring = zfun.find_nearest_ind(yd,253)
    for sn in sect_list:
        ax.plot(Stz_dict[sn][it_neap,:],Z,'-',color=c_dict[sn])
        ax.plot(Stz_dict[sn][it_spring,:],Z,'--',color=c_dict[sn])
    ax.text(.05,.1,'(b) Neap and Spring S(z)',color='k',fontweight='bold',
        transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlabel('Salinity')
ax.set_ylabel('Z [m]')

ax = fig.add_subplot(312)
for sn in sect_list:
    ax.plot(yd,St_dict[sn],'-',color=c_dict[sn])
ax.text(.05,.9,'(c) Depth-Mean S(t)',color='k',fontweight='bold',
    transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlim(0,365)
# ax.set_xlabel('Yearday ' + str(year))
ax.grid(axis='x')
if True:
    ax.axvline(x=yd[it_neap],linestyle='-',color='gray',linewidth=2)
    ax.axvline(x=yd[it_spring],linestyle='--',color='gray',linewidth=2)

ax = fig.add_subplot(313)
dti = pd.DatetimeIndex(otdt)
yd = dti.dayofyear
year = otdt[0].year
ax.plot(yd,St_dict[sect_list[0]]-St_dict[sect_list[-1]],'-',color='k')
ax.text(.05,.9,'(d) Total Along-Section Change in Depth-Mean Salinity',
    color='k',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlim(0,365)
ax.set_xlabel('Yearday ' + str(year))
ax.grid(axis='x')
# add Qprism
ax2 = ax.twinx()
ax2.plot(yd,0.5*(Qprism_dict[sect_list[0]]+Qprism_dict[sect_list[-1]])/1000,'-',
    color='c',linewidth=3,alpha=.4)
ax2.text(.95,.9,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color='c', 
    transform=ax.transAxes, ha='right',
    bbox=pfun.bbox)
ax2.set_ylim(bottom=0)
ax2.xaxis.label.set_color('c')
ax2.tick_params(axis='y', colors='c')
ax.set_xlim(0,365)
if True:
    ax.axvline(x=yd[it_neap],linestyle='-',color='gray',linewidth=2)
    ax.axvline(x=yd[it_spring],linestyle='--',color='gray',linewidth=2)

plt.show()




