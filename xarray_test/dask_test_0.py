"""
Code to test the use of dask for arrays too large to fit in RAM.

NOTE 10^9 float64 values takes 8 GB, and I have 32 GB RAM on my mac.

Ryan Abernathy said to aim for  100 MB chunks.

Result comparing hdf5 vs. zarr write/read an array with 10^10 floats [80 GB]:
hdf5 took 54.3 sec [80 GB]
zarr took 16.9 sec [300 MB !wow!]

"""
import numpy as np
import pandas as pd
import xarray as xr
import dask.array as da
import h5py
from time import time

from lo_tools import Lfun
Ldir = Lfun.Lstart()
out_dir = Ldir['parent'] / 'LPM_output' / 'test_dask'
Lfun.make_dir(out_dir)

out5_fn = out_dir / 'test_0.hdf5'
out5_fn.unlink(missing_ok= True)

outz_dir = out_dir / 'test_0.zarr'
Lfun.make_dir(outz_dir, clean=True)
outz_dir.rmdir()


a = da.ones(shape=(10_000,1000,1000), chunks=(10,1000,1000))
b = a[:,1:,:] + a[:,:-1,:]

tt0 = time()
b.to_hdf5(out5_fn, '/x')
storage = h5py.File(out5_fn)['x']
c5 = da.from_array(storage)
print('hdf5 took %0.1f sec' % (time()-tt0))

tt0 = time()
b.to_zarr(outz_dir)
cz = da.from_zarr(str(outz_dir))
print('zarr took %0.1f sec' % (time()-tt0))

