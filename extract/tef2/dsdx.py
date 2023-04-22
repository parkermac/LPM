"""
Experimental code to calculate ds/dx between two sections.

run dsdx -gtx cas6_v00_uu0m -ctag c0 -0 2022.01.01 -1 2022.12.31

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

# You have to select just two sections.
# Generally choose [seaward, landward]
sect_list = ['ai6','ai7'] # south end of AI
#sect_list = ['ai1','ai2'] # north end of AI
#sect_list = ['ai1','ai7'] # full AI
#sect_list = ['mb1','mb4'] # northern Main Basin
#sect_list = ['hc1','hc3'] # northern Hood Canal
#sect_list = ['jdf2','jdf4'] # Juan de Fuca
#sect_list = ['tn1','tn3'] # Tacoma Narrows
    
# make vn_list by inspecting the first section
ds = xr.open_dataset(in_dir / (sect_list[0] + '.nc'))
vn_list = [item for item in ds.data_vars \
    if (len(ds[item].dims) == 3) and (item not in ['vel','DZ'])]
ds.close()

print('\nCalculating ds/dx:')
print(str(in_dir))

tt00 = time()

svz_dict = dict()
lon_dict = dict()
lat_dict = dict()
lon_vec_dict = dict()
lat_vec_dict = dict()
ustar2_lp_dict = dict()
H_dict = dict()

for sn in sect_list:
    tt0 = time()
    print(sn)

    # load fields
    ds = xr.open_dataset(in_dir / (sn + '.nc'))
    salt_hourly = ds.salt.values
    pad = 36
    salt = zfun.lowpass(salt_hourly, f='godin')[pad:-pad+1:24, :]
    NT, N, P = salt.shape
    
    # make Qprism
    q = ds['dd'].values * ds['DZ'].values * ds['vel'].values
    qnet = np.nan * np.ones(q.shape[0])
    for tt in range(q.shape[0]):
        qnet[tt] = q[tt,:,:].squeeze().sum()
    qabs = np.abs(qnet)
    qabs_lp = zfun.lowpass(qabs, f='godin')[pad:-pad+1:24]
    Qprism = qabs_lp/2
    
    sdf = sect_df.loc[sect_df.sn==sn,:]
    
    h = ds.h.values
    zr, zw = zrfun.get_z(h, 0*h, S) # packed (z,p)
    zf = zr.flatten() # Note: this does not change with time
    # what if there is only one p?
    H_dict[sn] = h.mean()
    
    # get section area (ssh=0)
    dz = np.diff(zw,axis=0)
    A = np.sum(ds['dd'].values * dz)
    
    # and then form time series of ustar^2
    u = qnet/A
    Cd = 3e-3
    ustar2 = Cd * u * u
    # The factor of 2 implies that we are using the amplitude of the
    # tidal velocity.
    # To see this, assume u = Ut * cos(om*t), then
    # <u^2> = 1/2 Ut^2, and so Ut^2 = 2 * <u^2>.
    ustar2_lp = 2 * zfun.lowpass(ustar2, f='godin')[pad:-pad+1:24]
    ustar2_lp_dict[sn] = ustar2_lp
    
    # find mean lat and lon (more work than it should be!)
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
    
    svz_dict[sn] = s_vs_z
    
dx, ang = sw.dist([lat_dict[sect_list[0]],lat_dict[sect_list[1]]],
    [lon_dict[sect_list[0]],lon_dict[sect_list[1]]],
    units='km')
dx = dx[0]

# z for plotting
z = bin_edges[:-1] + np.diff(bin_edges)/2

# arrays of s(t,z), daily
ss0 = svz_dict[sect_list[0]]
ss1 = svz_dict[sect_list[1]]

# form time series with overlapping data
mask = np.isnan(ss0) | np.isnan(ss1)
SS0 = ss0[:,~mask[0,:]]
SS1 = ss1[:,~mask[0,:]]
SSm0 = np.mean(SS0,axis=1)
SSm1 = np.mean(SS1,axis=1)

# dsdx time series
DSS = SSm0 - SSm1
dssdx = DSS / (dx*1000)

# form time averages with overlapping data
s0 = np.mean(ss0, axis=0)
s1 = np.mean(ss1, axis=0)
mask = np.isnan(s0) | np.isnan(s1)
S0 = s0[~mask]
S1 = s1[~mask]
Z = z[~mask]
Sm0 = S0.mean()
Sm1 = S1.mean()
DS = Sm0 - Sm1
dsdx = DS / (dx*1000)

# select an H for the Simpson number
if False:
    H = -Z[0]
else:
    H = (H_dict[sect_list[0]] + H_dict[sect_list[1]])/2

# form the Simpson number
g = 9.8
beta = 7.7e-4
Ustar2 = (ustar2_lp_dict[sect_list[0]] + ustar2_lp_dict[sect_list[1]])/2
Si = g * beta * dssdx * H * H / Ustar2
    
# plotting
plt.close('all')
pfun.start_plot(figsize=(18,12))
fig = plt.figure()

# map
ax = fig.add_subplot(231)
lon0 = lon_vec_dict[sect_list[0]]
lat0 = lat_vec_dict[sect_list[0]]
lon1 = lon_vec_dict[sect_list[1]]
lat1 = lat_vec_dict[sect_list[1]]
lonmin = np.min(np.concatenate((lon0,lon1)))
lonmax = np.max(np.concatenate((lon0,lon1)))
latmin = np.min(np.concatenate((lat0,lat1)))
latmax = np.max(np.concatenate((lat0,lat1)))
ax.plot(lon0, lat0, '.r')
ax.plot(lon1, lat1, '.b')
pfun.add_coast(ax,color='gray',linewidth=2)
mpad = .2
ax.axis([lonmin-mpad, lonmax+mpad, latmin-mpad, latmax+mpad])
pfun.dar(ax)
ax.text(.05,.9,'(a) Section Locations',color='k',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.text(.05,.8,sect_list[0],color='r',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.text(.05,.7,sect_list[1],color='b',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

ax = fig.add_subplot(232)
ax.plot(S0,Z,'-or', S1,Z,'-ob')
ax.text(.05,.1,'(b) Time-Mean s(z)',color='k',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlabel('Salinity')
ax.set_ylabel('Z [m]')

ax = fig.add_subplot(233)
dti = pd.DatetimeIndex(otdt)
yd = dti.dayofyear
year = otdt[0].year
ax.plot(yd,SSm0,'-r', yd,SSm1,'-b')
ax.text(.05,.9,'(c) Depth-Mean s(t)',color='k',fontweight='bold',transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlim(0,365)
ax.set_xlabel('Yearday ' + str(year))

ax = fig.add_subplot(212)
ax.plot(yd,dssdx*1e5,'-k',linewidth=2)
ax.plot(yd,np.log10(np.abs(Si)),'-y',linewidth=2)
ax.set_xlabel('Yearday ' + str(year))
ax.text(.05,.9,r'(d) $ds/dx\ [psu\ (100\ km)^{-1}]$',color='k',fontweight='bold',
    transform=ax.transAxes,bbox=pfun.bbox)
ax.text(.05,.8,'log10(Simpson Number)',color='y',fontweight='bold',
    transform=ax.transAxes,bbox=pfun.bbox)
ax.set_xlim(0,365)
ax.axhline(color='gray')
ax.grid(axis='x')
# add Qprism
ax2 = ax.twinx()
ax2.plot(yd,Qprism/1000,'-g',linewidth=3,alpha=.4)
ax2.text(.95,.9,r'$Q_{prism}\ [10^{3}m^{3}s^{-1}]$', color='g', transform=ax.transAxes, ha='right',
    bbox=pfun.bbox)
ax2.set_ylim(0,3*np.max(Qprism/1000))
ax2.xaxis.label.set_color('g')
ax2.tick_params(axis='y', colors='g')
ax.set_xlim(0,365)




plt.show()




