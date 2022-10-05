"""
Development code for low pass.
"""

from lo_tools import Lfun, zrfun, zfun

from time import time
import xarray as xr
import sys
#import dask

# from dask.distributed import Client
# if __name__ == "__main__":
#     #client = Client(processes=True)
#     client = Client(n_workers=2, threads_per_worker=4)

# NFN = len(fn_list)
# cca = np.arange(NFN)
# # The number of "chunks" is the "12" in this call.  The function np.array_split() is a
# # really handy way to split a vectory into a number of approximatly equal-length sub vectors.
# ccas = np.array_split(cca, 12)


import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart(gridname='cas6', tag='v0', ex_name = 'live')

fn_list = Lfun.get_fn_list('hourly', Ldir, '2019.07.04', '2019.07.06')
# length 73

gs = zfun.godin_shape() # length 71, sum = 1

# ds0 = xr.open_dataset(fn_list[0])
# vn_list = [item for item in ds0.data_vars if 'ocean_time' in ds0[item].dims]
# try:
#     vn_list.remove('CaCO3')
# except ValueError:
#     pass
    
# testing
testing = True
if testing:
    #vn_list = ['salt']
    # vn_list = ['zeta','salt','temp','u','v']
    vn_list = ['zeta','salt','temp','u','v','w',
    'NO3','phytoplankton','zooplankton',
    'detritus','Ldetritus','oxygen',
    'TIC','alkalinity',
    'Pair','Uwind','Vwind','shflux','ssflux','latent','sensible','lwrad','swrad',
    'sustr','svstr','bustr','bvstr']
    N = 2 # 2 gives 1 step
    # RESULT: 6 sec for full list for 1 hour, no chunking
else:
    vn_list = ['zeta','salt','temp','u','v','w',
    'NO3','phytoplankton','zooplankton',
    'detritus','Ldetritus','oxygen',
    'TIC','alkalinity',
    'Pair','Uwind','Vwind','shflux','ssflux','latent','sensible','lwrad','swrad',
    'sustr','svstr','bustr','bvstr']
    N = 72

tt0 = time()
for ii in range(1,N): # use (1,72) for full set
    ds = xr.open_dataset(fn_list[ii])#, chunks={'s_rho':10})
    # RESULT: using chunks seems slower in general
    print(ii)
    sys.stdout.flush()
    if ii == 1:
        lp = (ds[vn_list] * gs[ii-1]).squeeze(dim='ocean_time', drop=True).compute()
    else:
        lp = (lp + (ds[vn_list] * gs[ii-1]).squeeze(dim='ocean_time', drop=True)).compute()
print('Time to create lp = %0.2f sec' % (time()-tt0))

# plotting
if False:
    tt0 = time()
    plt.close('all')
    pfun.start_plot(figsize=(12,12))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plon, plat = pfun.get_plon_plat(lp.lon_rho.values, lp.lat_rho.values)
    #cs = ax.pcolormesh(plon,plat,lp.salt[-1,:,:].values, cmap='jet')
    cs = ax.pcolormesh(plon,plat,lp.zeta[:,:].values, cmap='jet')
    fig.colorbar(cs, ax=ax)
    pfun.dar(ax)
    plt.show()
    pfun.end_plot()
    print('Time to plot = %0.2f sec' % (time()-tt0))
