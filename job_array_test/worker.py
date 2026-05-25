"""
Worker code that is called as a member of the job array.
"""

from datetime import datetime, timedelta
import argparse
import xarray as xr
from lo_tools import Lfun

parser = argparse.ArgumentParser()
parser.add_argument('-tid', type=str) # task id from the job array (sbatch_worker.sh)
parser.add_argument('-gtx', type=str) # gtagex
parser.add_argument('-dstr', type=str) # date string for start, e.g. 2026.05.10
parser.add_argument('-lt', type=str) # list type (hourly or average)
parser.add_argument('-out_dir', type=str)
args = parser.parse_args()

tid0 = int(args.tid) - 1 # zero-based tid

# time_format = '%Y.%m.%d %H:%M:%S'
# time_str = datetime.now().strftime(time_format)
# out_fn = args.out_dir + '/' + args.tid + '.txt'
# with open(out_fn, 'w') as ffout:
#     ffout.write(time_str)

# generate the input file name
dt0 = datetime.strptime(args.dstr, Lfun.ds_fmt) # or '%Y.%m.%d'
if args.lt == 'hourly':
    this_dt = dt0 + timedelta(hours=tid0)
elif args.lt == 'average':
    this_dt = dt0 + timedelta(days=tid0)
this_ds = this_dt.strftime(Lfun.ds_fmt)
if args.lt == 'hourly':
    his_str = ('000' + str(int(this_dt.hour + 1)))[-4:]
    his_name = 'f' + this_ds + '/' + 'ocean_his_' + his_str + '.nc'
elif args.lt == 'average':
    his_name = 'f' + this_ds + '/' + 'ocean_avg_0001.nc'
in_fn = 's3://liveocean-pmacc/LO_roms/' + args.gtx + '/' + his_name

# generate the output file name
out_fn = args.out_dir + '/' + str(args.tid) + '.nc'

time_format = '%Y.%m.%d %H:%M:%S'
time_str = datetime.now().strftime(time_format)
tout_fn = args.out_dir + '/' + args.tid + '.txt'

# write time test lines
lines = [time_str, in_fn, out_fn, tout_fn]
with open(tout_fn, 'w') as ffout:
    for line in lines:
        ffout.write(f"{line}\n")

# extract something from a history file
storage_options = {'client_kwargs': {'endpoint_url': 'https://s3.kopah.uw.edu'}, 'anon': True}
ds_in = xr.open_dataset(in_fn, engine='h5netcdf', storage_options=storage_options)
ds1 = ds_in['salt'][0,0,:,10,10]
ds1.to_netcdf(out_fn)
