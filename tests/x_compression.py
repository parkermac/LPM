"""
Test of compressing an existing NetCDF file.

RESULT: this works well!  On my mac it took 17 seconds for a full cas6 history file,
and compressed it from 1940 MB to 754 MB (38% of its original size)
"""

import xarray as xr
from lo_tools import Lfun
from time import time

# get or make file names
Ldir = Lfun.Lstart()
in_fn = Ldir['parent'] / 'LiveOcean_roms' / 'output' / 'cas6_v3_lo8b' / 'f2019.07.04' / 'ocean_his_0001.nc'
out_dir = Ldir['parent'] / 'LPM_output' / 'tests'
Lfun.make_dir(out_dir)
out_fn = out_dir / 'small_his.nc'
out_fn.unlink(missing_ok=True)

# save a compressed version
tt0 = time()
ds0 = xr.open_dataset(in_fn)
ds1 = ds0.copy(deep=True)
enc_dict = {'zlib':True, 'complevel':1}
Enc_dict = {vn:enc_dict for vn in ds1.data_vars if 'ocean_time' in ds1[vn].dims}
# and save to NetCDF
ds1.to_netcdf(out_fn, encoding=Enc_dict)
ds1.close()
ds0.close()
print('Took %0.1f sec to compress' % (time()-tt0))

