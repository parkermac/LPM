"""
Code to experiment with tpxo9 files and converting them to ROMS forcing.
"""

import xarray as xr
import matplotlib.pyplot as plt
import cmath
import numpy as np
import pytide
from datetime import datetime, timedelta

# pyTMD modules
import load_constituents as lc
import load_nodal_corrections as lnc
import tidal_ellipse as ellip

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun
Ldir = Lfun.Lstart()

# get some gird and masking info
in_dir = Ldir['data'] / 'tide' / 'tpxo9'
g_fn = in_dir / 'grid_tpxo9_atlas_30_v5.nc'
g_ds = xr.open_dataset(g_fn)

def get_ginfo(zuv):
    # zuv should be 'z' or 'u' or 'v'
    lon_vec = g_ds['lon_'+zuv].values # 0:360
    lat_vec = g_ds['lat_'+zuv].values # -90:90
    i0 = zfun.find_nearest_ind(lon_vec, -130 + 360)
    i1 = zfun.find_nearest_ind(lon_vec, -122 + 360)
    j0 = zfun.find_nearest_ind(lat_vec, 42)
    j1 = zfun.find_nearest_ind(lat_vec, 52)
    lon, lat = np.meshgrid(lon_vec[i0:i1], lat_vec[j0:j1])
    lon = lon - 360 # hack to convert to -180:180 that only works west of 0 degrees
    # extended lon, lat for pcolormesh plotting
    plon, plat = pfun.get_plon_plat(lon, lat)
    # depth field (0 = land)
    h = g_ds['h'+zuv][i0:i1, j0:j1].values
    h = h.T
    return i0, i1, j0, j1, lon, lat, plon, plat, h
    
zuv = 'z'
i0, i1, j0, j1, lon, lat, plon, plat, h = get_ginfo(zuv)

# This gives the order in which constituents are packed in tides.nc
c_list =  ['m2','s2','k1','o1', 'n2','p1','k2','q1']

con = 'm2'

# Set the day to look at.
date_str = '2019.07.04'
time_dt = datetime.strptime(date_str, Ldir['ds_fmt'])

# load tpxo9 fields
c_fn = in_dir / ('h_' + con + '_tpxo9_atlas_30_v5.nc')
c_ds = xr.open_dataset(c_fn)

u_fn = in_dir / ('u_' + con + '_tpxo9_atlas_30_v5.nc')
u_ds = xr.open_dataset(u_fn)

# Load contituent fields
# Info from c_ds.hRe.field (MATLAB notation):
#    amp=abs(hRe+i*hIm)
#    GMT phase=atan2(-hIm,hRe)/pi*180 [converting radians to degrees]
# Also 0 = land so we use that as a mask.
# The amplitude units are mm (int), and I believe the phase is relative to 1/1/1992
hRe = c_ds.hRe[i0:i1, j0:j1].values
hIm = c_ds.hIm[i0:i1, j0:j1].values
# Note that these are packed [lon, lat] hence the transpose below to get them
# to my standard [lat, lon] packing.
# Real part
hRe = np.float64(hRe)
hRe = hRe.T
# Imaginary part
hIm = np.float64(hIm)
hIm = hIm.T
# Complex
hcx = hRe + 1j*hIm
# Then find the amplitude and phase of the complex amplitide
amp = abs(hcx)
phase = np.arctan2(-hIm,hRe) # -pi:pi
phase[h==0] = np.nan
amp[h==0] = np.nan

# then get the velocities
uRe = u_ds.uRe[i0:i1+1, j0:j1].values
uIm = u_ds.uIm[i0:i1+1, j0:j1].values
vRe = u_ds.vRe[i0:i1, j0:j1+1].values
vIm = u_ds.vIm[i0:i1, j0:j1+1].values

uRe = np.float64(uRe)
uRe = uRe.T
uIm = np.float64(uIm)
uIm = uIm.T
ucx = uRe + 1j*uIm
# interpolate to the z grid and mask
ucx = (ucx[:,:-1] + ucx[:,1:])/2
# convert from cm2/s to m/s
ucx[h>0] = (ucx[h>0]/1e4) / h[h>0]
ucx[h==0] = np.nan

vRe = np.float64(vRe)
vRe = vRe.T
vIm = np.float64(vIm)
vIm = vIm.T
vcx = vRe + 1j*vIm
# interpolate to the z grid and mask
vcx = (vcx[:-1,:] + vcx[1:,:])/2
# convert from cm2/s to m/s
vcx[h>0] = (vcx[h>0]/1e4) / h[h>0]
vcx[h==0] = np.nan

(umajor, uminor, uincl, uphase) = ellip.tidal_ellipse(ucx, vcx)

# apply nodal corrections and Greenwich phase using pyTMD functions
junk, ph, om, junk, junk = lc.load_constituent(con)
# ph = Greenwich phase of this constituent [rad] without nodal correction
# om = frequency of this constituent [rad s-1]
# 2*np.pi/(om*3600) gives period in hours
# the pyTMD nodal correction code expects time in Modified Julian Date (mjd)
# which is the number of days since midnight on November 17, 1858.  Weird.
#
# trel is the time in days from the reference time of TPXO (1/1/1992) to the
# time where we can the nodal corrections.
tref_dt = datetime(1992,1,1)
trel_days = (time_dt - tref_dt).days # days from tref to current time
# then mjd is
tref_mjd = (tref_dt - datetime(1858,11,17)).days # mjd of tref (should be 48622)
mjd = trel_days + tref_mjd # mjd of current time
pu, pf, G = lnc.load_nodal_corrections(mjd, [con])
# pu = nodal correction of phase [rad]
# pf = nodal correction to multiply amplitude by [dimensionless]
# include Greenwich phase and nodal phase corrrection
phase = phase - ph - pu
uphase = np.pi*uphase/180 - ph - pu
# wrap phase to ensure it is in -pi to pi
phase = np.angle(np.exp(1j*phase))
uphase = np.angle(np.exp(1j*uphase))
# convert to degrees [-180:180]
phase = 180 * phase / np.pi
uphase = 180 * uphase / np.pi
# convert to 0-360 format to better (?) compare with tides.nc
phase[phase<0] += 360 # [0:360]
uphase[uphase<0] += 360 # [0:360]
# apply nodal correction to amplitude, and convert mm to m
amp = pf * amp / 1000
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

umajor = fadj * pf * umajor
uminor = fadj * pf * uminor

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
print('Constituent = %s, max phase = %0.2f, min phase = %0.2f (before 0-360 conversion)' %
            (con, np.nanmin(phase_r), np.nanmax(phase_r)))
# force phase_r to be 0-360
phase_r[phase_r<0] += 360
uphase_r[uphase_r<0] += 360
uincl_r[uincl_r<0] += 360

# Plotting
plt.close('all')

if False:
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

    pfun.start_plot(figsize=(16, 12), fs=10)
    fig = plt.figure()

    ax = fig.add_subplot(241)
    cs = ax.pcolormesh(plon, plat, umajor, vmin=0, vmax=Umajor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 umajor [m/s]')

    ax = fig.add_subplot(245)
    cs = ax.pcolormesh(plon_r, plat_r, umajor_r, vmin=0, vmax=Umajor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 umajor [m/s]')

    ax = fig.add_subplot(242)
    cs = ax.pcolormesh(plon, plat, uminor, vmin=0, vmax=Uminor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uminor [m/s]')

    ax = fig.add_subplot(246)
    cs = ax.pcolormesh(plon_r, plat_r, uminor_r, vmin=0, vmax=Uminor, cmap='jet')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uminor [m/s]')
    
    ax = fig.add_subplot(243)
    cs = ax.pcolormesh(plon, plat, uphase, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uphase [deg]')
    ax.contour(lon, lat, uphase, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(247)
    cs = ax.pcolormesh(plon_r, plat_r, uphase_r, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uphase [deg]')
    ax.contour(lon_r, lat_r, uphase_r, np.arange(dmin, dmax+10, 10))

    
    ax = fig.add_subplot(244)
    cs = ax.pcolormesh(plon, plat, uincl, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('TPXO9 uincl [deg]')
    ax.contour(lon, lat, phase, np.arange(dmin, dmax+10, 10))

    ax = fig.add_subplot(248)
    cs = ax.pcolormesh(plon_r, plat_r, uincl_r, vmin=dmin, vmax=dmax, cmap='bwr')
    fig.colorbar(cs)
    pfun.dar(ax)
    ax.set_title('tide1 uincl [deg]')
    ax.contour(lon_r, lat_r, uincl_r, np.arange(dmin, dmax+10, 10))

    fig.suptitle(con)

    plt.show()
    pfun.end_plot()

