"""
Plot results of a particle tracking experiment.

Like tplot.py but plots all particles and no tracks,
and it saves images as a sequence of png's which can then
be made into a movie.

This is hard-coded to make a plot of specific experiments.

"""


import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
from subprocess import Popen as Po
from subprocess import PIPE as Pi
from pathlib import Path

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# specific output files from tracker2 runs
fng = Path('/Users/parkermaccready/Documents/LO_output/tracks2/cas7_t0_x4b/PS3shallow_3d_rise40/grid.nc')
fn_s = Path('/Users/parkermaccready/Documents/LO_output/tracks2/cas7_t0_x4b/PS3shallow_3d_rise40/release_2022.07.01.nc')
fn_d = Path('/Users/parkermaccready/Documents/LO_output/tracks2/cas7_t0_x4b/PS3deep_3d_sink40/release_2022.07.01.nc')

def process_release(fn):
    dsr = xr.open_dataset(fn, decode_times=False)

    lon0 = dsr.lon[0,:].to_numpy()
    lat0 = dsr.lat[0,:].to_numpy()

    lon = dsr.lon.to_numpy()
    lat = dsr.lat.to_numpy()

    # filter to only use particles released in deeper water
    h0 = dsr.h[0,:].to_numpy()
    zmask = h0 >= 50
    lon0 = lon0[zmask]
    lat0 = lat0[zmask]
    lon = lon[:,zmask]
    lat = lat[:,zmask]

    # filter to only use a limited spatial domain
    xymask = (lon0>-123.5) & (lon0<-123) & (lat0>48) & (lat0<48.5)
    lon0 = lon0[xymask]
    lat0 = lat0[xymask]
    lon = lon[:,xymask]
    lat = lat[:,xymask]

    # filter to use fewer time steps
    nstep = 3
    lon = lon[::nstep,:]
    lat = lat[::nstep,:]

    NT, NP = lon.shape

    return NT, NP, lon, lat
    dsr.close()

NT_s, NP_s, lon_s, lat_s = process_release(fn_s)
NT_d, NP_d, lon_d, lat_d = process_release(fn_d)

# gather some grid fields, for convenience
dsg = xr.open_dataset(fng)
lonp, latp = pfun.get_plon_plat(dsg.lon_rho.values, dsg.lat_rho.values)
hh = dsg.h.values
maskr = dsg.mask_rho.values
dsg.close()

# PLOTTING
plt.close('all')
pfun.start_plot(figsize=(10,12))

out_dir = Ldir['parent'] / 'LPM_output' / 'tplot1movie'
Lfun.make_dir(out_dir, clean=True)

for tt in range(NT_s):

    lon1_s = lon_s[tt,:]
    lat1_s = lat_s[tt,:]
    lon1_d = lon_d[tt,:]
    lat1_d = lat_d[tt,:]

    fig = plt.figure()

    # MAP
    # set domain limits
    # automatically plot region of particles, with padding
    pad = .2
    # aa = [np.nanmin(lon0) - pad, np.nanmax(lon0) + pad,
    # np.nanmin(lat0) - pad, np.nanmax(lat0) + pad]

    aa = [-126, -122, 46, 50]
        
    ax = fig.add_subplot(111)
    zm = -np.ma.masked_where(maskr==0, hh)
    plt.pcolormesh(lonp, latp, zm, vmin=-100, vmax=0,
        cmap='terrain', alpha=.25)
    pfun.add_coast(ax)
    ax.axis(aa)
    pfun.dar(ax)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.plot(lon1_d, lat1_d, '.g')
    ax.plot(lon1_s, lat1_s, '.r')

    ntt = ('0000' + str(tt))[-4:]

    fig.savefig(out_dir / ('plot_' + ntt + '.png'))

    plt.close()

pfun.end_plot()

# make a movie
cmd_list = ['ffmpeg','-r','8','-i', str(out_dir)+'/plot_%04d.png', '-vcodec', 'libx264',
    '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
    '-pix_fmt', 'yuv420p', '-crf', '25', str(out_dir)+'/tplot1movie.mp4']
proc = Po(cmd_list, stdout=Pi, stderr=Pi)
stdout, stderr = proc.communicate()




