"""
Code to explore plotting of monthly means and their anomaly from climatology.

This version is intended to put all the fields or anomalies on a single grid.
The goal is to make it easier to see patterns.
"""

import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from datetime import datetime, timedelta

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

gtagex = 'cas7_t0_x4b'

testing = False

if testing:
    # hack to start from a month I have on my mac but still do 10 years
    dt0 = datetime.strptime('2020.01.01', Lfun.ds_fmt)
    dt1 = datetime.strptime('2029.12.31', Lfun.ds_fmt)
else:
    # the actual range of the monthly averages
    dt0 = datetime.strptime('2014.01.01', Lfun.ds_fmt)
    dt1 = datetime.strptime('2023.12.31', Lfun.ds_fmt)
dti = pd.date_range(dt0, dt1, freq='ME', inclusive='both')

dir1 = Ldir['roms_out'] / gtagex / 'averages'
dir2 = Ldir['roms_out'] / gtagex / 'climatologies'
fn1_list = []
fn2_list = []
year_list = []
month_list = []
for dt in dti:
    ym_str = dt.strftime('%Y_%m')
    mo_str = ('000' + str(dt.month))[-2:]
    fn1_list.append(dir1 / ('monthly_mean_' + ym_str + '.nc'))
    fn2_list.append(dir2 / ('monthly_clim_' + mo_str + '.nc'))
    year_list.append(dt.year)
    month_list.append(dt.month)

fld = 'temp'
slev = -1

plt.close('all')
pfun.start_plot(figsize=(8,12))
fig = plt.figure()
gs1 = gridspec.GridSpec(10,12, figure=fig)
gs1.update(wspace=0.025, hspace=0.015) # set the spacing between axes. 

ii = 0
for fn1 in fn1_list:

    if ii == 0:
        ds1 = xr.open_dataset(fn1)
        plon, plat = pfun.get_plon_plat(ds1['lon_rho'].values, ds1['lat_rho'].values)
        f1 = ds1[fld][0,slev,:,:].values
        ds1.close()

    if testing and (ii > 0):
        pass
    elif (not testing) and (ii > 0):
        ds1 = xr.open_dataset(fn1)
        f1 = ds1[fld][0,slev,:,:].values
        ds1.close()

    ax1 = plt.subplot(gs1[ii])
    cs1 = ax1.pcolormesh(plon,plat,f1,cmap='rainbow')
    pfun.dar(ax1)
    # ax1.axis('off')
    if ii in range(12):
        ax1.set_title(month_list[ii])
    if ii in range(0,120,12):
        ax1.set_ylabel(year_list[ii])
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    ax1.set_xticks([])
    ax1.set_yticks([])

    ii += 1

fig.suptitle(gtagex + ': Monthy Means')

if testing:
    plt.show()
else:
    out_dir = Ldir['parent'] / 'LPM_output' / 'plotting'
    Lfun.make_dir(out_dir)
    fig.savefig(out_dir / 'monthly_means.png')
