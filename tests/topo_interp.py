"""
Code to help debug some interpolation issues I am having with the cleaned-up
topo data

Result: my homegrown zfun.interp2 is much faster (100x) than the scipy intp.interp2d,
and gives more reliable results for heavily masked things like willapa_bay.
"""

from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import scipy.interpolate as intp
from time import time

Ldir = Lfun.Lstart()

source_list = ['srtm15plus','cascadia','nw_pacific','psdem',
               'ttp_patch','grays_harbor','willapa_bay']

# grid to interpolate to
xx = np.linspace(-130,-122,120)
yy = np.linspace(42,52,200)
x, y = np.meshgrid(xx,yy)

plt.close('all')
pfun.start_plot(figsize=(16,8))
for source in source_list:
    
    fn = Ldir['data'] / 'topo' / source / 'topo.nc'
    ds = xr.open_dataset(fn)
    # get topo data
    lon = ds.lon.values
    lat = ds.lat.values
    Z = ds.z.values
    X, Y = np.meshgrid(lon,lat)
    ds.close()


    # (1) Interpolation scheme from lo_tools/plotting_functions.add_velocity_vectors()
    # create interpolant
    tt0 = time()
    ui = intp.interp2d(lon,lat,Z, fill_value=np.nan)
    # interpolate to new grid
    z1 = ui(xx, yy)
    dt1 = time()-tt0

    # (2) Home-grown interpolation scheme
    tt0 = time()
    z2 = zfun.interp2(x, y, X, Y, Z)
    dt2 = time()-tt0
    
    fig = plt.figure()
    ax = fig.add_subplot(121)
    ax.pcolormesh(z1)
    ax = fig.add_subplot(122)
    ax.pcolormesh(z2)
    fig.suptitle(source)
        
    print('\n%s' % (source))
    print('max diff = %0.2f' % (np.nanmax(z2-z1)))
    print('scipy takes %0.3f s, homegrown takes %0.3f s' % (dt1,dt2))
    
plt.show()