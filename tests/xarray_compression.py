"""
Test of compressing an existing NetCDF file.

RESULT: this works well!  On my mac it took 20 seconds for a full cas6 history file,
and compressed it from 1940 MB to 754 MB (38% of its original size)
"""

import xarray as xr
from lo_tools import Lfun
from time import time
import shutil

# get or make file names
Ldir = Lfun.Lstart()
in_fn = Ldir['parent'] / 'LiveOcean_roms' / 'output' / 'cas6_v3_lo8b' / 'f2019.07.04' / 'ocean_his_0001.nc'
out_dir = Ldir['parent'] / 'LPM_output' / 'tests'
Lfun.make_dir(out_dir)
out_fn = out_dir / 'small_his.nc'
out_fn.unlink(missing_ok=True)

# make a copy
tt0 = time()
shutil.copyfile(in_fn, out_fn)
print('Took %0.1f sec to copy' % (time()-tt0))

# compress that copy in place
tt0 = time()
ds0 = xr.open_dataset(out_fn)
enc_dict = {'zlib':True, 'complevel':1}
Enc_dict = {vn:enc_dict for vn in ds0.data_vars if 'ocean_time' in ds0[vn].dims}
ds0.to_netcdf(out_fn, encoding=Enc_dict)
ds0.close()
print('Took %0.1f sec to compress' % (time()-tt0))

