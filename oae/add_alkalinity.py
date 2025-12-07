"""
Code to add alkalinity to a grid cell from a history file.
"""

import xarray as xr
import numpy as np
import sys, shutil
from lo_tools import Lfun, zfun, zrfun
from time import time
Ldir = Lfun.Lstart()

# >>>>>>>>>>> OAE Code <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# import xarray as xr
# import numpy as np
# import sys
# from lo_tools import Lfun, zfun, zrfun
# Will need to run in loenv!!
# dt_y = dt - timedelta(days=1) # y is for yesterday
# f_string_y = 'f' + dt_y.strftime(Lfun.ds_fmt)
f_string_y = 'f2013.07.01'
gtagex = 'cas7_t1_x11abc'
roms_out_dir_y = Ldir['roms_out'] / gtagex / f_string_y
orig_fn = roms_out_dir_y / 'ORIG_ocean_his_0002.nc'
spiked_fn = roms_out_dir_y / 'ocean_his_0002.nc'

if orig_fn.is_file():
    # assume we have already spiked this day, AND that
    # ORIG_ocean_his_0002.nc is UNSPIKED
    pass
else:
    # assume we have NOT already spiked this day, AND that
    # ocean_his_0002.nc is UNSPIKED
    tt0 = time()
    shutil.move(str(spiked_fn),str(orig_fn))
    print('Time to move file = %0.1f sec' % (time()-tt0))
# In either case we now have the ORIG_ file and we assume it is unspiked.
# I need to think carefully if there are cases where these assumptions might
# be incorrect, e.g. if I run an experiment multiple times.

tt0 = time()
# carry on with the spiking
ds = xr.open_dataset(orig_fn)
# Columbia River mouth
lon = -124.11
lat = 46.245
# Amount to increase alkalinity concentration
dalk = 2000 # mmol m-3, same as ROMS units
# find cell location
G, S, T = zrfun.get_basic_info(orig_fn)
Lon = G['lon_rho'][0,:]
Lat = G['lat_rho'][:,0]
# error checking
if (lon < Lon[0]) or (lon > Lon[-1]):
    print('ERROR: lon out of bounds')
    sys.exit()
if (lat < Lat[0]) or (lat > Lat[-1]):
    print('ERROR: lat out of bounds')
    sys.exit()
ix = zfun.find_nearest_ind(Lon, lon)
iy = zfun.find_nearest_ind(Lat, lat)
# error checking
if G['mask_rho'][iy,ix] == 0:
    print('ERROR: point on land mask. Exiting.')
    sys.exit()
# add alkalinity and save to a new file
spiked_fn.unlink(missing_ok=True)
xypad = 2
ds.alkalinity[0,-16:,iy-xypad:iy+xypad+1,ix-xypad:ix+xypad+1] += dalk
ds.to_netcdf(spiked_fn)
ds.close()
print('Time to spike and save file = %0.1f sec' % (time()-tt0))
# now we have a new initial condition for this day!
# >>>>>>>>>>> End OAE Code <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# check results
ds = xr.open_dataset(spiked_fn)
xypad2 = xypad + 1
print(ds.alkalinity[0,-15,iy-xypad2:iy+xypad2+1,ix-xypad2:ix+xypad2+1].values)

# Looking around a bit

# find volume of that grid cell
z_w = zrfun.get_z(G['h'], ds.zeta[0,:,:].to_numpy(), S, only_w=True)
DZ = np.diff(z_w, axis=0)
dx = G['DX'][iy,ix]
dy = G['DY'][iy,ix]
dz = DZ[-1,iy,ix]
V = dx * dy * dz

# find the initial alkalinity of the top center grid cell
alk = ds.alkalinity[0,-1,iy,ix].to_numpy()

# find numer of moles required to increase alkalinity in this (one cell) volume by dalk
nmoles = dalk * V / 1000 # converting dalk from mmol/m3 to mol/m3

ds.close()