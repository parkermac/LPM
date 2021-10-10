"""
Code to experiment with writing things to xarray datasets, especially
regarding coordinates.

"""

import numpy as np
import xarray as xr
import pandas as pd

NT, NR, NC = (4,5,6)
Lon = np.linspace(-130,-122,NC)
Lat = np.linspace(42,52,NR)
lon, lat = np.meshgrid(Lon,Lat)
time = pd.date_range(start='1/1/2021', periods=NT)

u = np.arange(NT*NR*NC).reshape((NT,NR,NC))
coords={'lon':(('y','x'), lon), 'lat':(('y','x'), lat), 'time':(('time'), time)}
attrs={'units':'m/s', 'long_name':'velocity'}

# different ways of adding this to a Dataset: all give identical results

# make a DataArray then load it into a Dataset
da = xr.DataArray(u, dims=('time','y','x'), coords=coords, attrs=attrs)
ds0 = xr.Dataset({'u':da})

# alternate way
ds1 = xr.Dataset()
ds1['u'] = da
ds1.u.attrs = attrs

# alternate way
ds2 = xr.Dataset({'u':(('time','y','x'), u)})
ds2.coords['lat'] = (('y','x'), lat)
ds2.coords['lon'] = (('y','x'), lon)
ds2.coords['time'] = time # not clear how it knows this is also a dimension
ds2.u.attrs = attrs

# alternate way
ds3 = xr.Dataset({'u':(('time','y','x'), u)}, coords=coords)
ds3.u.attrs = attrs

