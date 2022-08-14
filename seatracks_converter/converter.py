"""
Code to convert the json format of tracks files for use by seaTracks.
"""

import json

from lo_tools import Lfun
Ldir = Lfun.Lstart()

in_dir = Ldir['parent'] / 'PM_Web_8' / 'LO' / 'tracks'

for tag in ['PS', 'full']:
    
    in_fn = in_dir / ('tracks_' + tag + '.json')

    out_fn = in_dir / ('tracks_' + tag + '_restructured.json')

    data = json.load(open(in_fn))
    # data is a list of dicts. Each list item is a single drifter track stored as a dict with
    # keys x and y
    ndrifters = len(data)
    ntimes = len(data[0]['x'])

    newjson = [{'track':j, 'point':i,'x':data[j]['x'][i],'y':data[j]['y'][i]}
        for i in range(ntimes) for j in range(ndrifters)]

    with open(out_fn, 'w') as ff:
        json.dump(newjson, ff)