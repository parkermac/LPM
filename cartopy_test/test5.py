"""
Test of reading and plotting the CUSP coastline.

Data source:
shoreline.noaa.gov/data/datasheets/cusp.html

Spatial Reference: Geographic coordinate system (decimal degrees);
Horizontal Datum – North American Datum of 1983 (NAD83)

Tidal Datum: Where applicable, CUSP will reference a mean-high water shoreline
based on vertical modeling or image interpretation using both water level stations
and/or shoreline indicators.

Interesting issue: no coastline around Skagit River and that part of Whidbey basin.
It is listed as "in progress" on the CUSP site.

Performance:

Takes 20 sec for the initial reading, but after that the list append and plot
steps are very fast.  Final vector length is about 3.6 million point pairs.
"""


import numpy as np
import matplotlib.pyplot as plt
from time import time

import cartopy.io.shapereader as shpreader

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()
in_dir = Ldir['data'] / 'coast' / 'CUSP' / 'Western'

shp_fn = in_dir / 'Western.shp'

reader = shpreader.Reader(str(in_dir / 'Western.shp'))
recs = reader.records()

tt0 = time()
x_dict = dict()
y_dict = dict()
ii = 0
for cl in recs: # there are about 80k records in Western.shp!
    C = cl.geometry
    x_dict[ii] = np.array(C.xy[0])
    y_dict[ii] = np.array(C.xy[1])
    # if ii > 10000:
    #     break
    ii += 1
print('Time to fill dicts = %0.1f sec' % (time()-tt0))

tt0 = time()
# concatenate the dict entries into a single pair of vectors
x_list = []
y_list = []
for ii in x_dict.keys():
    x = list(x_dict[ii])
    y = list(y_dict[ii])
    x_list += x
    y_list += y
    x_list.append(np.nan)
    y_list.append(np.nan)
x_vec = np.array(x_list)
y_vec = np.array(y_list)
print('Time to concatenate into vectors = %0.1f sec' % (time()-tt0))
    
# PLOTTING
tt0 = time()
plt.close('all')
fig = plt.figure(figsize=(10,13))
ax = fig.add_subplot(111)
ax.plot(x_vec, y_vec, '-b')
# for ii in x_dict.keys():
#     x = x_dict[ii]
#     y = y_dict[ii]
#     ax.plot(x,y,'-b')
pfun.add_coast(ax)
pfun.dar(ax)
plt.show()
print('Time to plot = %0.1f sec' % (time()-tt0))

