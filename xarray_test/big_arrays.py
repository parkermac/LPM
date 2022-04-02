"""
Code to test working with xarray DataArrays that are too big to fit in RAM.

Result: I was able to initialize an array with a scalar broadcast into several
large dimensions, but it was slow used more than available RAM.  Trying to
subsequently do mat with the array was even slower.

So this is not a solution.

"""

import numpy as np
import xarray as xr
import pandas as pd
from time import time

#NT, NR, NC = (10, 10, 10)
NT, NR, NC = (10000, 1000, 1000)

tt0 = time()

a = xr.DataArray(1, coords={'t': np.arange(NT), 'y': np.arange(NR), 'x': np.arange(NC)}, dims=['t', 'y', 'x'])

print('took %0.1f sec' % (time()-tt0))
