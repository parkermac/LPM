"""
Code to debug a problem in the plotting routine P_sect. The issue was
that it did not handle sections that cross land in a graceful way.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from lo_tools import Lfun, zrfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

fn = Ldir['roms_out'] / 'cas6_v00Stock_uu0mb' / 'f2021.07.04' / 'ocean_his_0002.nc'

G, S, T = zrfun.get_basic_info(fn)
ds = xr.open_dataset(fn)



# field to plot
vn = 'oxygen'
vmin = 100
vmax = 400
cmap = 'jet'

# load history file and info
G, S, T = zrfun.get_basic_info(fn)
ds = xr.open_dataset(fn)

# SECTION EXTRACTION CODE

"""
The section plotting concept is that we form fields:
    dist_se: array of distance along section [km] (layer, dist) on cell edges
    zw_se: array of z position along section [m] (layer, dist) on cell edges
    sv_s: array of field values in section (layer, dist), on cell centers
These are then what we use in pcolormesh.
"""

# Define the section to plot on (lon, lat, degrees) on cell edges.
x = np.linspace(-124, -123, 500)
y = 48.368 * np.ones(x.shape)
# Also make points between for interpolating the field onto, cell centers.
xx = x[:-1] + np.diff(x)/2
yy = y[:-1] + np.diff(y)/2

# Gather some fields.
lon = G['lon_rho']
lat = G['lat_rho']
mask = G['mask_rho']
h = G['h']
zeta = ds['zeta'].values.squeeze()
# Make sure we don't end up with nan's in our zw field.
h[mask==0] = 0
zeta[mask==0] = 0

# get zw field, used for cell edges.
zw = zrfun.get_z(h, zeta, S, only_w=True)
N = zw.shape[0]

# 3-D field that we will full the section from
sv = ds[vn].values.squeeze()

def get_dist(x,y):
    # Create a vector of distance [km] along a track
    # defined by lon, lat points (x and y in the arguments)
    earth_rad = zfun.earth_rad(np.mean(y)) # m
    xrad = np.pi * x /180
    yrad = np.pi * y / 180
    dx = earth_rad * np.cos(yrad[1:]) * np.diff(xrad)
    dy = earth_rad * np.diff(yrad)
    ddist = np.sqrt(dx**2 + dy**2)
    dist = np.zeros(len(x))
    dist[1:] = ddist.cumsum()/1000 # km
    return dist
    
dist_e = get_dist(x,y) # cell edges
dist = get_dist(xx,yy) # cell centers

# Make dist_e into a 2-D array for plotting.
dist_se = np.ones((N,1)) * dist_e.reshape((1,-1))
# the -1 means infer size from the array

def get_sect(x,y,fld, lon, lat):
    # Interpolate a 3-D field (fld) along a 2-D track
    # defined by lon and lat vectors x and y.
    # The 3-D field is assumed to be on the rho-grid vertically,
    # and we assume that the lon, lat arrays are plaid.
    # Note: if you were plotting a field like u or v then you would want
    # to pass the corresponding lon and lat arrays instead of the rho-grid
    # ones we use here.
    col0, col1, colf = zfun.get_interpolant(x, lon[1,:])
    row0, row1, rowf = zfun.get_interpolant(y, lat[:,1])
    colff = 1 - colf
    rowff = 1 - rowf
    if len(fld.shape) == 3:
        fld_s = (rowff*(colff*fld[:, row0, col0] + colf*fld[:, row0, col1])
            + rowf*(colff*fld[:, row1, col0] + colf*fld[:, row1, col1]))
    elif len(fld.shape) == 2:
        fld_s = (rowff*(colff*fld[row0, col0] + colf*fld[row0, col1])
            + rowf*(colff*fld[row1, col0] + colf*fld[row1, col1]))
    return fld_s

# Do the section extractions for zw (edges) and sv (centers)
zw_se = get_sect(x, y, zw, lon, lat)
sv_s = get_sect(xx, yy, sv, lon, lat )

# Also generate top and bottom lines
h_s = get_sect(xx, yy, h, lon, lat )
zeta_s = get_sect(xx, yy, zeta, lon, lat )
zeta_s[np.isnan(sv_s[-1,:])] = 0
h_s[np.isnan(sv_s[-1,:])] = 0

# END SECTION EXTRACTION CODE

# PLOTTING

plt.close('all')
pfun.start_plot(figsize=(12,8))
fig = plt.figure()

# map with section line
ax = fig.add_subplot(2,1,1)
plon, plat = pfun.get_plon_plat(G['lon_rho'], G['lat_rho'])
cs = ax.pcolormesh(plon,plat,ds[vn][0,-1,:,:],vmin=vmin,vmax=vmax,cmap=cmap)
pfun.add_coast(ax)
aaf = [-124.5, -122.3, 48.2, 48.6] # focus domain
ax.axis(aaf)
pfun.dar(ax)
# add section track
ax.plot(x, y, '-r', linewidth=2)

# section
ax = fig.add_subplot(2,1,2)
ax.plot(dist, -h_s, '-k', linewidth=2)
ax.plot(dist, zeta_s, '-b', linewidth=1)
ax.set_xlim(dist.min(), dist.max())
ax.set_ylim(-200, 5)
# plot section
cs = ax.pcolormesh(dist_se,zw_se,sv_s,vmin=vmin,vmax=vmax,cmap=cmap)

plt.show()
