"""
Plot results of several particle tracking experiments done for
Nina Bednarsek.
"""


import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# Choose an experiment and release to plot.
in_dir0 = Ldir['LOo'] / 'tracks'

plt.close('all')

stay = '70'
tag_list = ['','_twopart']
tag_dict = {'':'', '_twopart':', Go to bottom at 30 days'}

for tag in tag_list:

    exp_name_list = ['nina_jdfw_3d_stay'+stay+tag, 'nina_jdfe_3d_stay'+stay+tag, 'nina_aih_3d_stay'+stay+tag]
    rel_list = ['release_2021.04.15.nc', 'release_2021.09.01.nc']

    # get grid
    fng = in_dir0 / exp_name_list[0] / 'grid.nc'
    dsg = xr.open_dataset(fng)
    # gather some fields, for convenience
    lonp, latp = pfun.get_plon_plat(dsg.lon_rho.values, dsg.lat_rho.values)
    hh = dsg.h.values
    maskr = dsg.mask_rho.values
    zm = -np.ma.masked_where(maskr==0, hh)

    # PLOTTING
    pfun.start_plot(figsize=(20,9))
    aa = [-126.5, -122, 47, 50]
    fig, axes = plt.subplots(nrows=1, ncols=2)

    # MAPS
    for ii in range(2):
        axes[ii].pcolormesh(lonp, latp, zm, vmin=-100, vmax=0, cmap='terrain', alpha=.2)
        pfun.add_coast(axes[ii])
        axes[ii].axis(aa)
        pfun.dar(axes[ii])
        axes[ii].set_xlabel('Longitude')
        if ii == 0:
            axes[ii].set_ylabel('Latitude')
        if ii == 1:
            axes[ii].set_yticklabels([])
        
        axes[ii].text(.05,.9,rel_list[ii], transform=axes[ii].transAxes, fontweight='bold')
    fig.suptitle('Particles around ' + stay + ' m, Run for 60 days' + tag_dict[tag])

    clist = 'rbg'

    ii = 0
    for exp_name in exp_name_list:
        jj = 0
        for rel in rel_list:
        
            # get Datasets
            fn = in_dir0 / exp_name / rel
            dsr = xr.open_dataset(fn, decode_times=False)

            # # subsample output for plotting
            # npmax = 300 # max number of points to plot
            # step = max(1,int(np.floor(NP/npmax)))
            # lon = dsr.lon.values[:,::step]
            # lat = dsr.lat.values[:,::step]
            lon = dsr.lon.values
            lat = dsr.lat.values
            #
            # # make a mask that is False from the time a particle first leaves the domain
            # # and onwards
            # AA = [dsg.lon_rho.values[0,0], dsg.lon_rho.values[0,-1],
            #         dsg.lat_rho.values[0,0], dsg.lat_rho.values[-1,0]]
            # ib_mask = np.ones(lon.shape, dtype=bool)
            # ib_mask[lon < AA[0]] = False
            # ib_mask[lon > AA[1]] = False
            # ib_mask[lat < AA[2]] = False
            # ib_mask[lat > AA[3]] = False
            # NTS, NPS = lon.shape
            # for pp in range(NPS):
            #     tt = np.argwhere(ib_mask[:,pp]==False)
            #     if len(tt) > 0:
            #         ib_mask[tt[0][0]:, pp] = False
            # # and apply the mask to lon and lat
            # lon[~ib_mask] = np.nan
            # lat[~ib_mask] = np.nan

            axes[jj].plot(lon[0,:], lat[0,:], '.'+clist[ii], alpha=.3)
            axes[jj].plot(lon[-1,:], lat[-1,:], '.'+clist[ii], markersize=7-2.5*ii, alpha=.3)
        
            jj += 1
        
        ii += 1

    fig.tight_layout()
    plt.show()
    pfun.end_plot()
    dsr.close()
    dsg.close()
    
    if True:
        out_dir = Ldir['parent'] / 'LPM_output' / 'tracks'
        Lfun.make_dir(out_dir)
        out_fn = out_dir / ('nina_stay_' + stay + tag + '.png')
        fig.savefig(out_fn)

