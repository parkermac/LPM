"""
Code to calculate and save tidal phase and amplitude for both
observations and a list of model runs.

NOTE: This assumes all the extractions we are working on are the same length, like
a month or a year. The input file names just have the year at this point.

"""


import pandas as pd
import tide_fun as tfun
from lo_tools import Lfun

from importlib import reload
reload(tfun)

Ldir = Lfun.Lstart()

year_str = '2022'
out_dir = Ldir['parent'] / 'LPM_output' / 'tide'
Lfun.make_dir(out_dir)

# MODEL RUNS

gtagex_list = ['cas7_t0_x4b', 'cas7_t1_x4', 'cas7_t1_x4tf']

for gtagex in gtagex_list:
    print('\n' + gtagex)
    mod_fn = Ldir['LOo'] / 'extract' / gtagex / 'tide' / ('ssh_df_' + year_str + '.p')
    sn_fn = Ldir['LOo'] / 'extract' / gtagex / 'tide' / ('sn_df_' + year_str + '.p')
    mod_df = pd.read_pickle(mod_fn)
    sn_df = pd.read_pickle(sn_fn)
    sn_df.drop(columns=['jgood','igood'], inplace=True)
    # remove means
    mod_df -= mod_df.mean()
    # add harmonic analysis columns to sn_df
    for sn in sn_df.index:
        lat = sn_df.loc[sn,'lat']
        mod_ser = mod_df[sn]
        h = tfun.get_harmonics(mod_ser, lat)
        for hn in tfun.hn_list:
            A, G, F = tfun.get_AG(hn, h)
            sn_df.loc[sn,hn+'_A'] = A
            sn_df.loc[sn,hn+'_G'] = G
    out_fn = out_dir / (gtagex + '_' + year_str + '_harmonics_sn_df.p')
    sn_df.to_pickle(out_fn)

# OBSERVATIONS

obs_dir = Ldir['LOo'] / 'obs' / 'tide'

# Combine all the observed Series into a single DataFrame in the same format
# as the model extractions. Here we are reusing the index and columns from the last
# "mod_df" in the section above

obs_df = pd.DataFrame(index = mod_df.index, columns = mod_df.columns)
for sn in mod_df.columns:
    if sn[0] == '0':
        source = 'dfo'
    else:
        source = 'noaa'
    fn = obs_dir / ('tide_' + source + '_' + str(sn) + '_' + year_str + '.p')
    ser = pd.read_pickle(fn)
    obs_df.loc[:,sn] = ser
# remove means
obs_df -= obs_df.mean()

# We will also use one of the model sn_df DataFrames to store the harmonics
# from the observations.

sn_df = pd.read_pickle(sn_fn)
sn_df.drop(columns=['jgood','igood'], inplace=True)
# add harmonic analysis columns to sn_df
print('\n' + 'obs')
for sn in sn_df.index:
    lat = sn_df.loc[sn,'lat']
    obs_ser = obs_df[sn]
    h = tfun.get_harmonics(obs_ser, lat)
    for hn in tfun.hn_list:
        A, G, F = tfun.get_AG(hn, h)
        sn_df.loc[sn,hn+'_A'] = A
        sn_df.loc[sn,hn+'_G'] = G
out_fn = out_dir / ('obs_' + year_str + '_harmonics_sn_df.p')
sn_df.to_pickle(out_fn)

