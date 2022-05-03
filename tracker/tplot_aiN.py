"""
Code to plot results of a pair of tracker experiments hwere particles were
released near the bottom of Admiralty Inlet North (job=aiN) at the start of ebb
during Spring or neap.  We used a high-resolution nested model.
"""


import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# Choose an experiment and release to plot.
in_dir0 = Ldir['LOo'] / 'tracks'

# get grid info
fng = in_dir0 / 'aiN_3d_sh7_Spring' / 'grid.nc'
dsg = xr.open_dataset(fng)
lonp, latp = pfun.get_plon_plat(dsg.lon_rho.values, dsg.lat_rho.values)
hh = dsg.h.values
maskr = dsg.mask_rho.values

# get tracker output
fnS = in_dir0 / 'aiN_3d_sh7_Spring' / 'release_2018.01.02.nc'
fnN = in_dir0 / 'aiN_3d_sh12_Neap' / 'release_2018.01.09.nc'
# We know that these had 300 particles each, and ran for 3 days minus the number of
# hours in sh#, so we will just plot the first 50 hours.  We also know they were saved at
# 12 saves per hour, so we will just look at the first 600 time points.

for fnr in [fnS, fnN]:
    V = dict()
    
    vn_list = ['lon', 'lat', 'z', 'salt', 'temp']
    # extract variables and clip
    dsr = xr.open_dataset(fnr)
    nn = 600
    for vn in vn_list:
        V[vn] = dsr[vn][:nn,:].values

    # make a mask that is False from the time a particle first leaves the domain
    # and onwards
    AA = [dsg.lon_rho.values[0,2], dsg.lon_rho.values[0,-3],
            dsg.lat_rho.values[2,0], dsg.lat_rho.values[-3,0]]
    ib_mask = np.ones(V['lon'].shape, dtype=bool)
    ib_mask[V['lon'] < AA[0]] = False
    ib_mask[V['lon'] > AA[1]] = False
    ib_mask[V['lat'] < AA[2]] = False
    ib_mask[V['lat'] > AA[3]] = False
    NT, NP = V['lon'].shape
    for pp in range(NP):
        tt = np.argwhere(ib_mask[:,pp]==False)
        if len(tt) > 0:
            ib_mask[tt[0][0]:, pp] = False

    # and apply the mask
    for vn in vn_list:
        V[vn][~ib_mask] = np.nan
    
    # save in separate dicts
    if fnr == fnS:
        VS = V.copy()
    elif fnr == fnN:
        VN = V.copy()

# PLOTTING
plt.close('all')
pfun.start_plot(figsize=(14,8))
fig = plt.figure()

# MAP
# set domain limits
# plot full domain
aa = [lonp.min(), lonp.max(), latp.min(), latp.max()]
    
ax = fig.add_subplot(121)
zm = -np.ma.masked_where(maskr==0, hh)
plt.pcolormesh(lonp, latp, zm, vmin=-100, vmax=0,
    cmap='terrain', alpha=.25)
pfun.add_coast(ax)
ax.axis(aa)
pfun.dar(ax)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Admiralty Inlet')

# Add the tracks (packed [time, particle]):

# Define "winners" as having lon at the end > -122.55
wS = VS['lon'][-1,:] > -122.55
wN = VN['lon'][-1,:] > -122.55
# these are Boolean masks, vectors of length NP

# graphical choices (0 = losers, 1 = winners)
a0 = .2; a1 = .7 # alphas
cS0 = 'r'; cS1 = 'm' # colors
cN0 = 'c'; cN1 = 'b' # colors
lw0 = .2; lw1 = .5 # linewidths

# Spring
ax.plot(VS['lon'][:,~wS], VS['lat'][:,~wS], '-', c=cS0, lw=lw0, alpha=a0)
ax.plot(VS['lon'][:,wS], VS['lat'][:,wS], '-', c=cS1, lw=lw1, alpha=a1)
ax.plot(VS['lon'][-1,wS], VS['lat'][-1,wS], 'o', c=cS1, alpha=a1)

# Neap
ax.plot(VN['lon'][:,~wN], VN['lat'][:,~wN], '-', c=cN0, lw=lw0, alpha=a0)
ax.plot(VN['lon'][:,wN], VN['lat'][:,wN], '-', c=cN1, lw=lw1, alpha=a1)
ax.plot(VN['lon'][-1,wN], VN['lat'][-1,wN], 'o', c=cN1, alpha=a1)

# Release Location (same for both experiments)
ax.plot(VS['lon'][0,0], VS['lat'][0,0], '*y', markeredgecolor='k', ms=20)

# and some tallies:
ax.text(.95,.85, 'Spring: %d winners' % (wS.sum()), c=cS1, ha='right', transform=ax.transAxes)
ax.text(.95,.75, '  Neap: %d winners' % (wN.sum()), c=cN1, ha='right', transform=ax.transAxes)

# time series
th = np.arange(nn) * 300 / 3600 # time from release in hours
tv_list = ['z', 'lon', 'lat']
ntv = len(tv_list)
for ii in range(ntv):
    tv = tv_list[ii]
    NC = 2
    ax = fig.add_subplot(ntv,NC, (ii+1)*NC)
    
    ax.plot(th, VS[tv][:,~wS], '-', c=cS0, lw=lw0, alpha=a0)
    ax.plot(th, VS[tv][:,wS], '-', c=cS1, lw=lw1, alpha=a1)
    
    ax.plot(th, VN[tv][:,~wN], '-', c=cN0, lw=lw0, alpha=a0)
    ax.plot(th, VN[tv][:,wN], '-', c=cN1, lw=lw1, alpha=a1)
    
    ax.text(.05, .05, tv, fontweight='bold', transform=ax.transAxes)
    if ii == ntv-1:
        ax.set_xlabel('Time (hours)')

plt.show()
pfun.end_plot()

