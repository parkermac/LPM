"""
Test of the speed of different ways of accessing data using xarray.

RESULT: when we are asking for just a small part of the array, like one
z level, the results are VERY different:

Indices before values takes 0.006 sec
Values before indices takes 0.154 sec

If we are asking for the whole array it makes no difference at all.

"""

from pathlib import Path
import xarray as xr
import numpy as np
from time import time

fn = Path('/Users/pm8/Documents/LiveOcean_roms/output/cas6_v3_lo8b/f2019.07.04/ocean_his_0001.nc')

ds = xr.open_dataset(fn)

tt0 = time()
a = ds.salt[0,-1,:,:].values
print('Indices before values takes %0.3f sec' % (time()-tt0))

tt0 = time()
a = ds.salt.values[0,0,:,:]
print('Values before indices takes %0.3f sec' % (time()-tt0))

ds.close()