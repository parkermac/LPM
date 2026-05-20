"""
Code to test my ability to access a zarr file on kopah from my laptop.

Result: it works!

Questions:
- did I need to set the CORS policy in that bucket?
- I set the access to --acl public-read, but an anomymous version of
  the code below does not work. Why?
"""
import xarray as xr
import os

s3_url = 's3://liveocean-test/test18.zarr'
ds = xr.open_zarr(
    s3_url,
    storage_options={
        "key": os.environ['AWS_ACCESS_KEY_ID'],
        "secret": os.environ['AWS_SECRET_ACCESS_KEY'],
        "client_kwargs": {
            "endpoint_url": "https://s3.kopah.uw.edu"
        }
    }
)

# This version does not work on either klone or my mac, throwing the error:
# PermissionError: An error occurred (AccessDenied) when calling the GetObject operation: Unknown
# I set the --acl to public-read for this bucket and all objects in it.
# ds1 = xr.open_zarr(
#     's3://liveocean-test/test18.zarr',
#     storage_options={
#         "anon": True,
#         "client_kwargs": {"endpoint_url": "https://s3.kopah.uw.edu"}
#     }
# )
