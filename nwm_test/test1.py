"""
Automation!
"""

from subprocess import Popen as Po
from subprocess import PIPE as Pi
from lo_tools import Lfun
import xarray as xr
import fsspec

Ldir = Lfun.Lstart()

# automate
url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.20211123/medium_range_mem1/'
r = 'nwm.t00z.medium_range.channel_rt_1.f238.conus.nc'
# a = url + r

#a = 'http://thredds.hydroshare.org/thredds/dodsC/nwm/medium_range/20211123/nwm.t00z.medium_range.channel_rt.f003.conus.nc'

#a = 'ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.20211124/medium_range_mem1/nwm.t00z.medium_range.channel_rt_1.f001.conus.nc'

a = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.20211124/medium_range_mem1/nwm.t00z.medium_range.channel_rt_1.f001.conus.nc'

#ds = xr.open_dataset(a)

ds = xr.open_zarr(fsspec.get_mapper('s3://pangeo-data-uswest2/esip/NWM2/2017', anon=False, requester_pays=True))

# out_dir = Ldir['parent'] / 'LPM_output' / 'NWM'
# Lfun.make_dir(out_dir)
# out_fn = out_dir / 'test1.nc'
#
# cmd_list = ['ncks',
#     '-v', 'streamflow',
#     '-d', 'feature_id,23989319','-O', a, str(out_fn)]
# proc = Po(cmd_list, stdout=Pi, stderr=Pi)
# stdout, stderr = proc.communicate()
#
# if len(stdout) > 0:
#     print('\n'+stdout.decode())
# if len(stderr) > 0:
#     print('\n'+stderr.decode())
