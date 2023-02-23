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

def get_sect(fn, vn, x_e, y_e):
    """
    Code to extract a section of any variable from a history file and return
    fields useful for plotting.
    
    The section plotting concept is that we form fields:
        dist_se: array of distance along section [km] (layer, dist) on cell edges
        zw_se: array of z position along section [m] (layer, dist) on cell edges
        fld_s: array of field values in section (layer, dist), on cell centers
    These are then what we use in pcolormesh.

    Naming conventions:
        [] is a vector on cell centers
        []_e is a vector on cell edges
        []_s is an array on cell centers
        []_se is an array on cell edges

    This should work for variables on any of the horizontal grids (u, v, rho).
    """
    
    G, S, T = zrfun.get_basic_info(fn)
    ds = xr.open_dataset(fn)

    # Make points x_e, y_e between for interpolating the field onto, on cell centers.
    x = x_e[:-1] + np.diff(x_e)/2
    y = y_e[:-1] + np.diff(y_e)/2

    # Gather some fields, making sure we use the appropriate lon, lat grids.
    if 'eta_u' in ds[vn].dims:
        lon = G['lon_u']
        lat = G['lat_u']
    elif 'eta_v' in ds[vn].dims:
        lon = G['lon_v']
        lat = G['lat_v']
    elif 'eta_rho' in ds[vn].dims:
        lon = G['lon_rho']
        lat = G['lat_rho']
    mask = G['mask_rho']
    h = G['h']
    zeta = ds['zeta'].values.squeeze()
    # Do this to make sure we don't end up with nan's in our zw field.
    h[mask==0] = 0
    zeta[mask==0] = 0

    # get zw field, used for cell edges.
    zw = zrfun.get_z(h, zeta, S, only_w=True)
    N = zw.shape[0]

    # Get 3-D field that we will full the section from
    fld = ds[vn].values.squeeze()
    # Force fld to be on the s_rho grid in the vertical if it is not already.
    if 's_w' in ds[vn].dims:
        fld = fld[:-1,:,:] + np.diff(fld,axis=0)/2

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
    
    dist_e = get_dist(x_e,y_e) # cell edges
    dist = get_dist(x,y) # cell centers

    # Make dist_e into a 2-D array for plotting.
    dist_se = np.ones((N,1)) * dist_e.reshape((1,-1))
    # the -1 means infer size from the array

    def get_sect(x, y, fld, lon, lat):
        # Interpolate a 2-D or 3-D field along a 2-D track
        # defined by lon and lat vectors x and y.
        # We assume that the lon, lat arrays are plaid.
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
    zw_se = get_sect(x_e, y_e, zw, lon, lat)
    fld_s = get_sect(x, y, fld, lon, lat )

    # Also generate top and bottom lines, with appropriate masking
    zbot = -get_sect(x, y, h, lon, lat )
    ztop = get_sect(x, y, zeta, lon, lat )
    zbot[np.isnan(fld_s[-1,:])] = 0
    ztop[np.isnan(fld_s[-1,:])] = 0
    
    return x, y, dist, dist_e, zbot, ztop, dist_se, zw_se, fld_s, lon, lat

# field to plot (any 3-D field should work)
vn = 'oxygen'

# Define the section to plot on (lon, lat, degrees) on cell edges.
x_e = np.linspace(-124, -123, 500)
y_e = 48.368 * np.ones(x_e.shape)

# do the section extraction
x, y, dist, dist_e, zbot, ztop, dist_se, zw_se, fld_s, lon, lat = get_sect(fn, vn, x_e, y_e)

# PLOTTING

# load history file and info
ds = xr.open_dataset(fn)

plt.close('all')
pfun.start_plot(figsize=(14,8))
fig = plt.figure()
cmap = 'jet'

# map with section line
ax = fig.add_subplot(2,1,1)
plon, plat = pfun.get_plon_plat(lon,lat)
cs = ax.pcolormesh(plon,plat,ds[vn][0,-1,:,:],cmap=cmap)
fig.colorbar(cs, ax=ax)
pfun.add_coast(ax)
aaf = [-124.5, -122.3, 48.2, 48.6] # focus domain
ax.axis(aaf)
pfun.dar(ax)
try:
    units_str = ds[vn].units
    ax.set_title('Field = %s [%s]' % (vn, units_str))
except AttributeError:
    ax.set_title('Field = %s' % (vn))
# add section track
ax.plot(x, y, '-k', linewidth=2)
ax.plot(x[0], y[0], 'ok', markersize=10, markerfacecolor='w')
ax.set_xlabel('Longitude [deg]')
ax.set_ylabel('Latitude [deg]')

# section
ax = fig.add_subplot(2,1,2)
ax.plot(dist, zbot, '-k', linewidth=2)
ax.plot(dist, ztop, '-b', linewidth=1)
ax.set_xlim(dist.min(), dist.max())
ax.set_ylim(-200, 5)
cs = ax.pcolormesh(dist_se,zw_se,fld_s,cmap=cmap)
fig.colorbar(cs, ax=ax)
ax.set_xlabel('Distance along Section [km]')
ax.set_ylabel('Z [m]')

plt.show()
