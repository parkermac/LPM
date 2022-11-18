"""
Plot results of a particle tracking experiment.

Customized for a section release in Admiralty Inlet
"""


import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
from subprocess import Popen as Po
from subprocess import PIPE as Pi
import sys

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# Choose an experiment and release to plot.
in_dir0 = Ldir['LOo'] / 'tracks'
# exp_name = Lfun.choose_item(in_dir0, tag='', exclude_tag='.csv',
#     itext='** Choose experiment from list **', last=False)
# rel = Lfun.choose_item(in_dir0 / exp_name, tag='.nc', exclude_tag='grid',
#     itext='** Choose item from list **', last=False)

er_list = [('sect_AImid_3d_sh20_SpringSBF', 'release_2021.07.25.nc'),
        ('sect_AImid_3d_sh14_SpringSBE', 'release_2021.07.26.nc'),
        ('sect_AImid_3d_sh14_NeapSBF', 'release_2021.08.01.nc'),
        ('sect_AImid_3d_sh8_NeapSBE', 'release_2021.08.02.nc')]

plt.close('all')

for exp_name, rel in er_list:#[er_list[2]]:

    # get Datasets
    fn = in_dir0 / exp_name / rel
    dsr = xr.open_dataset(fn, decode_times=False)
    
    # temp folder for movie frames
    ename = exp_name.split('_')[-1]
    print('\n' + ename)
    out_dir = Ldir['parent'] / 'LPM_output' / 'tracks' / ename
    Lfun.make_dir(out_dir, clean=True)

    # grid map fields
    fng = in_dir0 / exp_name / 'grid.nc'
    dsg = xr.open_dataset(fng)
    lonp, latp = pfun.get_plon_plat(dsg.lon_rho.values, dsg.lat_rho.values)
    hh = dsg.h.values
    maskr = dsg.mask_rho.values
    zm = -np.ma.masked_where(maskr==0, hh)
    
    for tt in range(25):

        # PLOTTING
        pfun.start_plot(figsize=(13,7))
        fig = plt.figure()

        # set domain limits
        aa = [-123, -122.4, 47.8, 48.3]
    
        last_hour = tt
    
        # map
        ax = fig.add_subplot(121)
        plt.pcolormesh(lonp, latp, zm, vmin=-100, vmax=0,
            cmap='terrain', alpha=.25)
        pfun.add_coast(ax)
        ax.plot(dsr.lon[0,:].values, dsr.lat[0,:].values, '.b',alpha=.1)
        ax.plot(dsr.lon[last_hour,:].values, dsr.lat[last_hour,:].values, '.g',alpha=.1)
        ax.axis(aa)
        pfun.dar(ax)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(ename)

        # other plots
        ax = fig.add_subplot(222)
    
        ax.plot(dsr.lat[0,:].values, dsr.salt[0,:].values, '.b',alpha=.1)
        ax.plot(dsr.lat[last_hour,:].values, dsr.salt[0,:].values, '.g',alpha=.1)
        #ax.invert_yaxis()
        ax.set_ylim(33,28.5)
        ax.set_xlim(aa[2], aa[3])
        ax.set_ylabel('Salinity')

        ax = fig.add_subplot(224)
        ax.plot(dsr.lat[0,:].values, dsr.z[0,:].values, '.b',alpha=.1)
        ax.plot(dsr.lat[last_hour,:].values, dsr.z[0,:].values, '.g',alpha=.1)
        ax.set_ylim(-250,10)
        ax.set_xlim(aa[2], aa[3])
        ax.set_xlabel('Latitude')
        ax.set_ylabel('Z [m]')
        
        nouts = ('0000' + str(tt))[-4:]
        outname = 'plot_' + nouts + '.png'
        outfile = out_dir / outname
        print(' - plotting ' + outname)
        sys.stdout.flush()

        plt.savefig(outfile)
        # plt.show()
        pfun.end_plot()
        plt.close()
        
    # and make a movie
    cmd_list = ['ffmpeg','-r','8','-i', str(out_dir)+'/plot_%04d.png', '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p', '-crf', '25', str(out_dir)+'/' + ename + '.mp4']
    proc = Po(cmd_list, stdout=Pi, stderr=Pi)
    stdout, stderr = proc.communicate()
    # if len(stdout) > 0:
    #     print('\n'+stdout.decode())
    # if len(stderr) > 0:
    #     print('\n'+stderr.decode())

    dsr.close()
    dsg.close()

