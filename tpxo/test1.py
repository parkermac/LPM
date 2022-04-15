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

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun
Ldir = Lfun.Lstart()

# This gives the order in which constituents are packed in tides.nc
c_list =  ['m2','s2','k1','o1', 'n2','p1','k2','q1']

plt.close('all')
for con in ['s2']:
    
    # Set the day to look at.
    date_str = '2019.07.04'
    time_dt = datetime.strptime(date_str, Ldir['ds_fmt'])

    # load tpxo9 fields
    in_dir = Ldir['data'] / 'tide' / 'tpxo9'
    c_fn = in_dir / ('h_' + con + '_tpxo9_atlas_30_v5.nc')
    c_ds = xr.open_dataset(c_fn)
    lon_vec = c_ds.lon_z.values # 0:360
    lat_vec = c_ds.lat_z.values # -90:90
    i0 = zfun.find_nearest_ind(lon_vec, -130 + 360)
    i1 = zfun.find_nearest_ind(lon_vec, -122 + 360)
    j0 = zfun.find_nearest_ind(lat_vec, 42)
    j1 = zfun.find_nearest_ind(lat_vec, 52)
    lon, lat = np.meshgrid(lon_vec[i0:i1], lat_vec[j0:j1])
    lon = lon - 360 # hack to convert to -180:180 that only works west of 0 degrees
    # extended lon, lat for pcolormesh plotting
    plon, plat = pfun.get_plon_plat(lon, lat)

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
    phase[amp==0] = np.nan
    amp[amp==0] = np.nan
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
    # wrap phase to ensure it is in -pi to pi
    phase = np.angle(np.exp(1j*phase))
    # convert to degrees [-180:180]
    phase = 180 * phase / np.pi
    # convert to 0-360 format to better (?) compare with tides.nc
    phase[phase<0] += 360 # [0:360]
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

    # For comparison I will also load a ROMS forcing file.
    c_dict = dict(zip(c_list, range(len(c_list))))
    ic = c_dict[con] # index of this constituent
    # path to forcing file
    r_fn = Ldir['LOo'] / 'forcing' / 'cas6_v0' / ('f' + date_str) / 'tide1' / 'tides.nc'
    r_ds = xr.open_dataset(r_fn)
    # get amplitude and phase
    amp_r = r_ds.tide_Eamp[ic,:,:].values # [m]
    phase_r = r_ds.tide_Ephase[ic,:,:].values # [0-360 degrees]
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
    # and check on the phase limits
    print('Constituent = %s, max phase = %0.2f, min phase = %0.2f' %
                (con, np.nanmin(phase_r), np.nanmax(phase_r)))

    # Plotting

    # phase limits
    dmin = 0
    dmax = 360
    amax = 2

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
