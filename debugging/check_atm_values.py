"""
Custom code to plot Tair and Qair time series from atm forcing
over some time range. This is for debugging blowups.
"""

import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
from lo_tools import Lfun
import sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-g', '--gridname', type=str, default='cas7')
parser.add_argument('-0', '--ds0', type=str, default='2015.09.22')
parser.add_argument('-1', '--ds1', type=str, default='2015.09.23')
args = parser.parse_args()
gridname = args.gridname

Ldir = Lfun.Lstart()

if '_mac' in Ldir['lo_env']: # mac version
    pass
else: # remote linux version
    import matplotlib as mpl
    mpl.use('Agg')
import matplotlib.pyplot as plt

dt0 = datetime.strptime(args.ds0, Lfun.ds_fmt)
dt1 = datetime.strptime(args.ds1, Lfun.ds_fmt)

dr = pd.date_range(dt0,dt1)

df = pd.DataFrame(index=dr,columns=['Tair_max','Tair_min','Qair_max','Qair_min'])

in_dir_dict = dict()
for dt in dr:
    in_dir_dict[dt] = Ldir['LOo'] / 'forcing' / gridname / ('f' + dt.strftime(Lfun.ds_fmt)) / 'atm00'

for dt in dr:
    print(str(dt))
    sys.stdout.flush()
    in_dir = in_dir_dict[dt]
    for vn in ['Tair','Qair']:
        fn = in_dir / (vn + '.nc')
        a = xr.open_dataset(fn)
        aa = a[vn].to_numpy()
        df.loc[dt,vn+'_max'] = aa.max()
        df.loc[dt,vn+'_min'] = aa.min()
        a.close()

plt.close('all')
out_dir = Ldir['parent'] / 'LPM_output' / 'debugging'
Lfun.make_dir(out_dir)
df.to_pickle(out_dir / 'check_atm_values.p')
ax = df.plot()
fig = ax.get_figure()
fig.savefig(out_dir / 'check_atm_values.png')