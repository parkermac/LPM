"""
Code to convert a tracker run to json.
"""

import xarray as xr
import numpy as np
import json

from lo_tools import Lfun
Ldir = Lfun.Lstart()

gtagex = 'wgh2_t0_xn0b'
exp = 'wgh0_3d'
rel = '2024.08.23'

dir0 = Ldir['parent'] / 'LPM' / 'd3pm' / 'data'
in_fn = dir0 / gtagex / exp / ('release_' + rel + '.nc')
out_fn = dir0 / 'tracks.json'

ds = xr.open_dataset(in_fn)
# packed time, particle
lon = ds['lon'].values
lat = ds['lat'].values
NT, NP = lon.shape

if False:
    # try removing out-of-bounds points

    # RESULT: this worked, but it threw so many errors that it degraded performance.
    # The problem was reading nans.

    # make a mask that is False from the time a particle first leaves the domain
    # and onwards
    fng = dir0 / gtagex / exp / 'grid.nc'
    dsg = xr.open_dataset(fng)

    AA = [dsg.lon_rho.values[0,0], dsg.lon_rho.values[0,-1],
            dsg.lat_rho.values[0,0], dsg.lat_rho.values[-1,0]]
    ib_mask = np.ones(lon.shape, dtype=bool)
    ib_mask[lon < AA[0]] = False
    ib_mask[lon > AA[1]] = False
    ib_mask[lat < AA[2]] = False
    ib_mask[lat > AA[3]] = False
    NTS, NPS = lon.shape
    for pp in range(NPS):
        tt = np.argwhere(ib_mask[:,pp]==False)
        if len(tt) > 0:
            ib_mask[tt[0][0]:, pp] = False

    # and apply the mask to lon and lat
    lon[~ib_mask] = np.nan
    lat[~ib_mask] = np.nan

# original json
xy = []
for pp in range(NP):
    xy.append({'x': [('%0.3f' % (item)) for item in lon[:,pp]], 'y': [('%0.3f' % (item)) for item in lat[:,pp]]})
json.dump(xy, open(out_fn, 'w'))
