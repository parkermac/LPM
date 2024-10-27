"""
Code to convert bottle observational data to json format.
"""

from lo_tools import Lfun
import pandas as pd
import json

Ldir = Lfun.Lstart()

# input and output locations
in_dir0 = Ldir['LOo'] / 'obs'

out_dir = Ldir['parent'] / 'LPM' / 'd3pm' / 'obs'
Lfun.make_dir(out_dir)

# load data
source_list = ['dfo1', 'ecology_nc', 'nceiSalish', 'nceiCoastal',
    'LineP', 'nceiPNW', 'NHL', 'WOD', 'ocnms_ctd']
# source_list = ['ecology_nc', 'nceiSalish']
otype = 'bottle'
year = '2017'

counter = 0
for source in source_list:

    data_fn = in_dir0 / source / otype / (year + '.p')
    info_fn = in_dir0 / source / otype / ('info_' + year + '.p')

    try:
        data = pd.read_pickle(data_fn)
        info = pd.read_pickle(info_fn)
        info['cid'] = info.index
        if counter == 0:
            data_combined = data.copy()
            info_combined = info.copy()
            cid0 = data_combined.cid.max() + 1
        else:
            data['cid'] += cid0
            data_combined = pd.concat((data_combined, data.copy()), ignore_index=True)
            info['cid'] += cid0
            info_combined = pd.concat((info_combined, info.copy()), ignore_index=True)
            cid0 = data_combined.cid.max() + 1
        counter += 1
    except Exception as e:
        print(source)
        print(e)
        continue

# convert info to json and save
data_out_fn = out_dir / (otype + '_combined_' + year + '_data.json' )
data_combined.to_json(data_out_fn, double_precision=3)
info_out_fn = out_dir / (otype + '_combined_' + year + '_info.json' )
info_combined.to_json(info_out_fn, double_precision=3)
# output looks like:
# {"lon":{"0":-122.917,"1":-122.708,...
