"""
Code to test accessing kopah files.
"""

# Examples from Rich Signell
# https://nbviewer.org/gist/rsignell/971668353d7b16465d95a37830cf3f67
# This worked perfectly after I added requests and aiohttp modules to loenv.
# Rich also suggests using https://earthmover.io/blog/icechunk
# the latest miracle from Ryan Abernathy.

import fsspec
import xarray as xr

if False:
    # https version
    fs = fsspec.filesystem('https')
    url = 'https://s3.kopah.orci.washington.edu/f2025.02.25/layers_hour_0000.nc'
    ds = xr.open_dataset(fs.open(url))

else:
    # s3 version
    url = 's3://f2025.02.25/layers_hour_0000.nc'
    fs = fsspec.filesystem('s3', anon=True, endpoint_url='https://s3.kopah.uw.edu')
    ds = xr.open_dataset(fs.open(url))

