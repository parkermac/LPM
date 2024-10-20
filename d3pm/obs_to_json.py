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
source = 'ecology_nc'
otype = 'bottle'
year = '2017'

data_fn = in_dir0 / source / otype / (year + '.p')
info_fn = in_dir0 / source / otype / ('info_' + year + '.p')

data = pd.read_pickle(data_fn)
info = pd.read_pickle(info_fn)

# convert info to json and save
data_out_fn = out_dir / (otype + '_' + source.replace('_','') + '_' + year + '_data.json' )
data.to_json(data_out_fn, double_precision=3)
info_out_fn = out_dir / (otype + '_' + source.replace('_','') + '_' + year + '_info.json' )
info.to_json(info_out_fn, double_precision=3)
# output looks like:
# {"lon":{"0":-122.917,"1":-122.708,...
