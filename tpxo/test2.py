"""
Code to experiment with tpxo9 files and converting them to ROMS forcing.

Like test1.py but hiding all the tpxo extraction in a function
"""

import xarray as xr
import matplotlib.pyplot as plt
import cmath
import numpy as np
import pytide
from datetime import datetime, timedelta

from lo_tools import tpxo_functions as tpxo_fun
from importlib import reload
reload(tpxo_fun)

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun
Ldir = Lfun.Lstart()

# This gives the order in which constituents are packed in tides.nc.
# We need it to know what index to look at in tides.nc.
c_list =  ['m2','s2','k1','o1', 'n2','p1','k2','q1']

con = 'k1'

# Set the day to look at.
date_str = '2019.07.04'
time_dt = datetime.strptime(date_str, Ldir['ds_fmt'])

domain_tup = (-130, -122, 42, 52)

# this is where we do the entire tpxo9 extraction and processing
om, lon, lat, plon, plat, h, amp, phase, umajor, uminor, uincl, uphase = \
    tpxo_fun.get_tpxo_clip(Ldir, con, time_dt, domain_tup)

# check on the phase limits
print('Constituent = %s' % (con))
print('phase: max = %0.2f, min = %0.2f' % (np.nanmin(phase), np.nanmax(phase)))
print('uphase: max = %0.2f, min = %0.2f' % (np.nanmin(uphase), np.nanmax(uphase)))
print('uincl: max = %0.2f, min = %0.2f' % (np.nanmin(uincl), np.nanmax(uincl)))

# For comparison I will also load a ROMS forcing file.
c_dict = dict(zip(c_list, range(len(c_list))))
ic = c_dict[con] # index of this constituent
# path to forcing file
r_fn = Ldir['LOo'] / 'forcing' / 'cas6_v0' / ('f' + date_str) / 'tide1' / 'tides.nc'
r_ds = xr.open_dataset(r_fn)
# get amplitude and phase
amp_r = r_ds.tide_Eamp[ic,:,:].values # [m]
phase_r = r_ds.tide_Ephase[ic,:,:].values # [0-360 degrees]
# also get ellipse parameters
uphase_r = r_ds.tide_Cphase[ic,:,:].values
uincl_r = r_ds.tide_Cangle[ic,:,:].values
umajor_r = r_ds.tide_Cmax[ic,:,:].values
uminor_r = r_ds.tide_Cmin[ic,:,:].values
# NOTE: Actually some of the phases are negative (still greater than -180) [n2, p1, q1]
# get ROMS grid info for plotting
rg_fn = Ldir['data'] / 'grids' / 'cas6' / 'grid.nc'
rg_ds = xr.open_dataset(rg_fn)
lon_r = rg_ds.lon_rho.values
lat_r = rg_ds.lat_rho.values
mask_r = rg_ds.mask_rho.values
plon_r, plat_r = pfun.get_plon_plat(lon_r, lat_r)
# mask for plotting
amp_r[mask_r==0] = np.nan
phase_r[mask_r==0] = np.nan
uphase_r[mask_r==0] = np.nan
uincl_r[mask_r==0] = np.nan
umajor_r[mask_r==0] = np.nan
uminor_r[mask_r==0] = np.nan
# and check on the phase limits
print('\ntides.nc %s, max phase = %0.2f, min phase = %0.2f (before 0-360 conversion)' %
            (con, np.nanmin(phase_r), np.nanmax(phase_r)))
# force phase_r to be 0-360
phase_r[phase_r<=0] += 360
uphase_r[uphase_r<=0] += 360
uincl_r[uincl_r<=0] += 360

# ad hoc amplitude adjustments from make_forcing_worker.m
if con == 'o1':
    fadj = 1.21*1.087
elif con == 'k1':
    fadj = 1.21*1.11
elif con == 'p1':
    fadj = 1.21
elif con == 'q1':
    fadj = 1.21
elif con == 'm2':
    fadj = 1.17*1.075
elif con == 's2':
    fadj = 1.261*1.13
elif con == 'n2':
    fadj = 1.196*1.11
elif con == 'k2':
    fadj = 1.2*1.11
# apply ad hoc correction so we can directly compare with tides.nc
amp_adj = fadj * amp
umajor_adj = fadj * umajor
uminor_adj = fadj * uminor

# Plotting
plt.close('all')

if True:
    # First plot: Elevation

    # limits
    dmin = 0
    dmax = 360
    amax = np.nanmax(amp)

    pfun.start_plot(figsize=(16, 12))
    fig = plt.figure()

    ax = fig.add_subplot(231)
    cs = ax.pcolormesh(plon, plat, amp, vmin=0, vmax=amax, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 Amplitude [m]')

    ax = fig.add_subplot(232)
    cs = ax.pcolormesh(plon_r, plat_r, amp_r, vmin=0, vmax=amax, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 Amplitude [m]')

    ax = fig.add_subplot(233)
    ax.plot(amp[:,0], lat[:,0], '-r', label='TPXO9')
    ax.plot(amp_adj[:,0], lat[:,0], '--r', label='TPXO9 adjusted')
    ax.plot(amp_r[:,0], lat_r[:,0], '-b', label='tide1')
    ax.legend()
    ax.set_ylim(42, 52)
    ax.grid(True)
    ax.set_title('Amplitude at West [m]')

    ax = fig.add_subplot(234)
    cs = ax.pcolormesh(plon, plat, phase, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 Phase [deg]')
    ax.contour(lon, lat, phase, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(235)
    cs = ax.pcolormesh(plon_r, plat_r, phase_r, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 Phase [deg]')
    ax.contour(lon_r, lat_r, phase_r, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(236)
    ax.plot(phase[:,0], lat[:,0], '-r', label='TPXO9')
    ax.plot(phase_r[:,0], lat_r[:,0], '-b', label='tide1')
    ax.legend()
    ax.set_ylim(42, 52)
    ax.grid(True)
    ax.set_title('Phase at West [deg]')

    fig.suptitle(con)

    plt.show()
    pfun.end_plot()

if True:
    # Second plot current ellipse parameters
    dmin = 0
    dmax = 360
    Umajor = .4
    Uminor = .1

    pfun.start_plot(figsize=(20, 12), fs=10)
    fig = plt.figure()

    ax = fig.add_subplot(251)
    cs = ax.pcolormesh(plon, plat, umajor_adj, vmin=0, vmax=Umajor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 umajor_adj [m/s]')

    ax = fig.add_subplot(256)
    cs = ax.pcolormesh(plon_r, plat_r, umajor_r, vmin=0, vmax=Umajor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 umajor [m/s]')
    
    ax = fig.add_subplot(155)
    ax.plot(umajor_adj[:,0], lat[:,0], '-r', label='TPXO9')
    ax.plot(umajor_r[:,0], lat_r[:,0], '-b', label='tide1')
    ax.legend()
    ax.set_ylim(42, 52)
    ax.grid(True)
    ax.set_title('umajor_adj at West [m/s]')

    ax = fig.add_subplot(252)
    cs = ax.pcolormesh(plon, plat, uminor_adj, vmin=0, vmax=Uminor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uminor [m/s]')

    ax = fig.add_subplot(257)
    cs = ax.pcolormesh(plon_r, plat_r, uminor_r, vmin=0, vmax=Uminor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uminor [m/s]')
    
    ax = fig.add_subplot(253)
    cs = ax.pcolormesh(plon, plat, uphase, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uphase [deg]')
    # ax.contour(lon, lat, uphase, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(258)
    cs = ax.pcolormesh(plon_r, plat_r, uphase_r, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uphase [deg]')
    # ax.contour(lon_r, lat_r, uphase_r, np.arange(dmin, dmax+10, 10))

    
    ax = fig.add_subplot(254)
    cs = ax.pcolormesh(plon, plat, uincl, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uincl [deg]')
    # ax.contour(lon, lat, phase, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(259)
    cs = ax.pcolormesh(plon_r, plat_r, uincl_r, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uincl [deg]')
    # ax.contour(lon_r, lat_r, uincl_r, np.arange(dmin, dmax+10, 10))

    fig.suptitle(con)

    plt.show()
    pfun.end_plot()

