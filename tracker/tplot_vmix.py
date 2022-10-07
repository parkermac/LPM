"""
Plot results of a particle tracking experiment, specific to experiments about
vertical mixing of particles.

e.g. from:
python tracker.py -exp vmix -3d True -clb True -no_advection True
"""

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# Choose an experiment and release to plot.
in_dir0 = Ldir['LOo'] / 'tracks'
exp_name = 'vmix_3d_nadv'
rel = 'release_2019.07.04.nc'

# get Datasets
fn = in_dir0 / exp_name / rel
dsr = xr.open_dataset(fn, decode_times=False)

# get a list of datetimes
ot_vec = dsr.ot.values
dt_list = [Lfun.modtime_to_datetime(ot) for ot in ot_vec]
t = (ot_vec - ot_vec[0])/3600

NT, NP = dsr['lon'].shape

# Gather particle data
# packed [time, particle #]
z = dsr.z.values
h = dsr.h.values
cs = dsr.cs.values
dsr.close()

# rescale z to remove tides
ZZ = cs*(h)

if False:
    # generate random samples
    aa = np.nan * np.ones((28,4000))
    abins = np.linspace(0,1,29)
    for ii in range(4000):
        a = np.random.random(4000)
        aa[:,ii], aobins  = np.histogram(a, bins=abins)
    amin = aa.min(axis=1)
    amax = aa.max(axis=1)
else:
    amin = 102.5 * np.ones(28)
    amax = 187.3 * np.ones(28)

# PLOTTING
#plt.close('all')
pfun.start_plot(figsize=(14,8))
fig = plt.figure()

# Histograms
title_list = ['Slope', 'Juan de Fuca', 'Whidbey Basin']
for jj in [1,2,3]:
    
    NN = int(z.shape[1]/3)
    zz = ZZ[:,NN*(jj-1):NN*jj - 1]
    zmin = zz.min()
    zs = zz/(-zmin)
    ax = fig.add_subplot(1,3,jj)
    bins=np.linspace(-1, 0, 29)
    for ii in range(NT):
        counts, obins = np.histogram(zs[ii,:], bins=bins)
        ax.plot(counts, bins[:-1],'-o', label='Hour = %d' % (t[ii]))
    ax.plot(amin, bins[:-1],'-k',lw=1, alpha=.3)
    ax.plot(amax, bins[:-1],'-k',lw=1, alpha=.3)
    ax.set_xlim(0,300)
    ax.set_xlabel('Counts')
    if jj == 1:
        ax.set_ylabel('Scaled Z')
    ax.set_title(title_list[jj-1])

plt.show()
pfun.end_plot()


