"""
Code to explore using very large arrays with zarr.

It took 11 seconds to write 25 hours of a 3-D cas6 field.
and 22 seconds for two variables.

"""

import numpy as np
import pandas as pd
import xarray as xr
import dask.array as da
import zarr
from time import time

from lo_tools import Lfun
Ldir = Lfun.Lstart()
out_dir = Ldir['parent'] / 'LPM_output' / 'test_zarr'
Lfun.make_dir(out_dir)

z_dir = out_dir / 'test_1.zarr'
Lfun.make_dir(z_dir, clean=True)
z_dir.rmdir()

in_dir = Ldir['parent'] / 'LiveOcean_roms' / 'output' / 'cas6_v3_lo8b' / 'f2019.07.04'
in_fn = in_dir / 'ocean_his_0001.nc'
ds = xr.open_dataset(in_fn)
junk, NZ, NR, NC = ds.salt.shape

root = zarr.open(str(z_dir), mode='w')
foo = root.create_group('foo')

NT = 3

# a = zarr.open(str(z_dir), mode='w', shape=(NT, NZ, NR, NC),
#             chunks=(1,NZ, NR, NC), dtype='f4')
sa = foo.create_dataset('s', shape=(NT, NZ, NR, NC), chunks=(1,NZ, NR, NC), dtype='f4')
ta = foo.create_dataset('t', shape=(NT, NZ, NR, NC), chunks=(1,NZ, NR, NC), dtype='f4')

tt0 = time()
for ii in range(NT):
    hnum = ('0000' + str(ii+1))[-4:]
    in_fn = in_dir / ('ocean_his_' + hnum +'.nc')
    ds = xr.open_dataset(in_fn)
    s = ds.salt.values.squeeze()
    t = ds.temp.values.squeeze()
    sa[ii,:,:,:] = s
    ta[ii,:,:,:] = t
    # a[ii,:,:,:] = s
print('initial write took %0.1f sec' % (time()-tt0))
# foo.s.info gives info about that array

# to do math on this zarr archive load it as a zarr array
aa = da.from_zarr(str(z_dir / 'foo' / 's'))
# b = 2*aa

