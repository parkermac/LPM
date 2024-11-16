"""
Code to convert bottle obsmod data to json format.

This relies on dicts of dataframes that have been previously
created by LPM/obsmod/combin_obs_mod.py.
"""

from lo_tools import Lfun
import pandas as pd
import numpy as np
from lo_tools import obs_functions

Ldir = Lfun.Lstart()

# input and output locations
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'

out_dir = Ldir['parent'] / 'LPM' / 'd3pm' / 'obs'
Lfun.make_dir(out_dir)

# load data
#year_list = range(2013,2024)
year_list = [2017]

source = 'combined'
otype = 'bottle'
gtagex = 'cas7_t0_x4b'

for year in year_list:

    # load data
    in_fn = in_dir / (source + '_' + otype + '_' + str(year) + '_' + gtagex + '.p')
    df_dict = pd.read_pickle(in_fn)

    # save parts to json

    # data columns to include
    info_list = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'source']
    fld_list = ['CT', 'SA', 'DO (uM)', 'NO3 (uM)', 'DIC (uM)', 'TA (uM)']
    full_list = info_list + fld_list

    obs_df = df_dict['obs']
    for fld in fld_list:
        if fld not in obs_df.columns:
            obs_df[fld] = np.NaN
    obs_df = obs_df[full_list]
    # make sure we have all required columns, even if there is no data
    out_obs_fn = out_dir / (source + '_' + otype + '_' + str(year) + '_' + gtagex + '_obs.json')
    obs_df.to_json(out_obs_fn, double_precision=3)

    mod_df = df_dict[gtagex]
    for fld in fld_list:
        if fld not in mod_df.columns:
            mod_df[fld] = np.NaN
    mod_df = mod_df[full_list]
    out_mod_fn = out_dir / (source + '_' + otype + '_' + str(year) + '_' + gtagex + '_mod.json')
    mod_df.to_json(out_mod_fn, double_precision=3)

    # also pull out station locations with cid as index
    info_df = obs_functions.make_info_df(obs_df)
    info_df['cid'] = info_df.index.to_numpy()
    info_df.index = info_df.index.astype(int)
    out_info_fn = out_dir / (source + '_' + otype + '_' + str(year) + '_' + gtagex + '_info.json')
    info_df.to_json(out_info_fn, double_precision=3)

    # output looks like:
    # 
