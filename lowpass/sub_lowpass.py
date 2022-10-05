"""
Development code for low pass, trying out subprocess parallelism.
"""

from lo_tools import Lfun, zrfun, zfun

from time import time
import xarray as xr
import sys
#import dask

import subprocess

import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart(gridname='cas6', tag='v0', ex_name = 'live')

fn_list = Lfun.get_fn_list('hourly', Ldir, '2019.07.04', '2019.07.06')
# length 73

gs = zfun.godin_shape() # length 71, sum = 1

# create output location
out_dir = Ldir['parent'] / 'LPM_output' / 'lowpass' / 'temp_dir'
Lfun.make_dir(out_dir, clean=True)

# ds0 = xr.open_dataset(fn_list[0])
# vn_list = [item for item in ds0.data_vars if 'ocean_time' in ds0[item].dims]
# try:
#     vn_list.remove('CaCO3')
# except ValueError:
#     pass
    
# testing
if True:
    vn_list = ['salt']
    fn_list = fn_list[]
else:
    vn_list = ['zeta','salt','temp','u','v','w',
    'NO3','phytoplankton','zooplankton',
    'detritus','Ldetritus','oxygen',
    'TIC','alkalinity',
    'Pair','Uwind','Vwind','shflux','ssflux','latent','sensible','lwrad','swrad',
    'sustr','svstr','bustr','bvstr']

# concert the variable list to a string suitable for nco operators
vn_str = ','.join(vn_list)

# do the initial extractions
N = len(fn_list)
proc_list = []
tt0 = time()
for ii in range(N):
    fn = fn_list[ii]
    # extract one day at a time using ncks
    count_str = ('000000' + str(ii))[-6:]
    out_fn = temp_dir / ('box_' + count_str + '.nc')
    cmd_list1 = ['ncks',
        '-v', vn_list,
        '-d', 'xi_rho,'+str(ilon0)+','+str(ilon1), '-d', 'eta_rho,'+str(ilat0)+','+str(ilat1),
        '-d', 'xi_u,'+str(ilon0)+','+str(ilon1-1), '-d', 'eta_u,'+str(ilat0)+','+str(ilat1),
        '-d', 'xi_v,'+str(ilon0)+','+str(ilon1), '-d', 'eta_v,'+str(ilat0)+','+str(ilat1-1)]
    if Ldir['surf']:
        cmd_list1 += ['-d','s_rho,'+str(S['N']-1)]
    elif Ldir['bot']:
        cmd_list1 += ['-d','s_rho,0']
    cmd_list1 += ['-O', str(fn), str(out_fn)]
    proc = Po(cmd_list1, stdout=Pi, stderr=Pi)
    proc_list.append(proc)

    # screen output about progress
    if (np.mod(ii,10) == 0) and ii>0:
        print(str(ii), end=', ')
        sys.stdout.flush()
    if (np.mod(ii,50) == 0) and (ii > 0):
        print('') # line feed
        sys.stdout.flush()
    if (ii == N-1):
        print(str(ii))
        sys.stdout.flush()

    # Nproc controls how many ncks subprocesses we allow to stack up
    # before we require them all to finish.
    if ((np.mod(ii,Ldir['Nproc']) == 0) and (ii > 0)) or (ii == N-1):
        for proc in proc_list:
            proc.communicate()
        # make sure everyone is finished before continuing
        proc_list = []
    ii += 1
print(' Time to for initial extraction = %0.2f sec' % (time()- tt0))
sys.stdout.flush()

# tt0 = time()
# for ii in range(1,20): # use (1,72) for full set
#     ds = xr.open_dataset(fn_list[ii], chunks={'s_rho':30})
#     print(ii)
#     sys.stdout.flush()
#     if ii == 1:
#         lp = (ds[vn_list] * gs[ii-1]).squeeze(dim='ocean_time', drop=True).compute()
#     else:
#         lp = (lp + (ds[vn_list] * gs[ii-1]).squeeze(dim='ocean_time', drop=True)).compute()
# print('Time to create lp = %0.2f sec' % (time()-tt0))