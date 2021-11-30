"""
Further tests of direct access to the NetCDF files.
"""

import xarray as xr
import netCDF4 as nc

url = ('https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.20211129' +
    '/medium_range_mem1/nwm.t00z.medium_range.channel_rt_1.f001.conus.nc')
    
#ds = xr.open_dataset(url)
ds = nc.Dataset(url)