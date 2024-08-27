"""
Code to convert a tracker run to json.
"""

import xarray as xr
import numpy as np
import json
from datetime import datetime, timedelta

from lo_tools import Lfun
Ldir = Lfun.Lstart()

gtagex = 'wgh2_t0_xn0b'
exp = 'wgh0_3d'
rel = '2024.08.23'

in_dir0 = Ldir['parent'] / 'LPM_data' / 'd3pm'
in_fn = in_dir0 / gtagex / exp / ('release_' + rel + '.nc')
out_dir0 = Ldir['parent'] / 'LPM' / 'd3pm' / 'data'
out_fn = out_dir0 / 'tracks.json'
out2_fn = out_dir0 / 'times.json'

ds = xr.open_dataset(in_fn)
# packed time, particle
lon = ds['lon'].values
lat = ds['lat'].values
NT, NP = lon.shape

# Make a time vector (Note the Time is hours from the start of the release)
dt0 = datetime.strptime(rel, Ldir['ds_fmt'])
Time = ds.Time.values
dt_list = []
for h in Time:
    dt_list.append(dt0 + timedelta(days=h/24))

# Create and save jsons.
xy = []
for pp in range(NP):
    xy.append({'x': [('%0.3f' % (item)) for item in lon[:,pp]], 'y': [('%0.3f' % (item)) for item in lat[:,pp]]})
json.dump(xy, open(out_fn, 'w'))


tt_list = []
for tt in range(NT):
    tt_list.append(datetime.strftime(dt_list[tt],'%Y-%m-%d %H:%M'))
tt = [{'t': tt_list}]
json.dump(tt, open(out2_fn, 'w'))
