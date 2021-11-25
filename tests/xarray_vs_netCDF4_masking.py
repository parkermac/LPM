"""
Code to compare xarray and netCDF4, especially in
relation to masked variables.

RESULTS:

CASE: If we pass a masked array
========================= ds4_by_4 =========================
[0.0 1.5 3.0 4.5 6.0 7.5 9.0 -- -- --]
========================= dsx_by_4 =========================
[0.0 1.5 3.0 4.5 6.0 7.5 9.0 -- -- --]
========================= ds4_by_x =========================
[0.  1.5 3.  4.5 6.  7.5 9.  nan nan nan]
========================= dsx_by_x =========================
[0.  1.5 3.  4.5 6.  7.5 9.  nan nan nan]

CASE: If we pass an array with nans
========================= ds4_by_4 =========================
[0.  1.5 3.  4.5 6.  7.5 9.  nan nan nan]
========================= dsx_by_4 =========================
[0.0 1.5 3.0 4.5 6.0 7.5 9.0 -- -- --]
========================= ds4_by_x =========================
[0.  1.5 3.  4.5 6.  7.5 9.  nan nan nan]
========================= dsx_by_x =========================
[0.  1.5 3.  4.5 6.  7.5 9.  nan nan nan]

The only difference is in ds4_by_4 which now returns an array with
nans instead of a masked array (if we passed it an array with nans).

NOTE: In order to get these to work nicely it was essential to explicitly set
the fill value in both cases.

"""

import numpy as np
import xarray as xr
import netCDF4 as nc
from pathlib import Path

from lo_tools import Lfun
Ldir = Lfun.Lstart()
dir0 = Ldir['parent'] / 'LPM_output' / 'tests'
Lfun.make_dir(dir0)

# create the data
N = 10
u = 1.5 * np.arange(N)
u[-3:] = np.nan

for ii in range(2):
    
    if ii == 0:
        uu = np.ma.masked_where(np.isnan(u), u)
        tsrt = 'a masked array'
    elif ii == 1:
        uu = u.copy()
        tsrt = 'an array with nans'

    fn4 = dir0 / 'n4.nc'
    fn4.unlink(missing_ok=True)
    a = nc.Dataset(fn4, 'w')
    a.createDimension('x', N)
    v = a.createVariable('u', float, ('x',), fill_value=1e20)
    v[:] = uu
    a.close()

    fnx = dir0 / 'xa.nc'
    fnx.unlink(missing_ok=True)
    a = xr.Dataset()
    a['u'] = (('x',), uu)
    a.to_netcdf(fnx, encoding={'u': {'_FillValue':1e20}})
    a.close()

    ds4_by_4 = nc.Dataset(fn4, 'r')
    dsx_by_4 = nc.Dataset(fnx, 'r')
    dsx_by_x = xr.open_dataset(fnx)
    ds4_by_x = xr.open_dataset(fn4)

    print('\nCASE: If we pass ' + tsrt)
    print(' ds4_by_4 '.center(60,'='))
    print(ds4_by_4['u'][:])
    print(' dsx_by_4 '.center(60,'='))
    print(dsx_by_4['u'][:])
    print(' ds4_by_x '.center(60,'='))
    print(ds4_by_x['u'].values)
    print(' dsx_by_x '.center(60,'='))
    print(dsx_by_x['u'].values)

    # clean up
    ds4_by_4.close()
    dsx_by_4.close()
    ds4_by_x.close()
    dsx_by_x.close()
    fn4.unlink(missing_ok=True)
    fnx.unlink(missing_ok=True)



