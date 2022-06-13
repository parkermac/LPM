"""
Plot a map of the sections, segments, and rivers.

"""

# imports
import sys
import matplotlib.pyplot as plt
import pickle
import xarray as xr
import pandas as pd
import numpy as np

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun

gridname = 'cas6'
tag = 'v3'
Ldir = Lfun.Lstart(gridname, tag)

pth = str(Ldir['LO'] / 'extract' / 'tef')
if pth not in sys.path:
    sys.path.append(pth)
import tef_fun, flux_fun

# get the DataFrame of all sections
sect_df = tef_fun.get_sect_df(Ldir['gridname'])

# select the indir
indir0 = Ldir['LOo'] / 'extract' / 'tef'
voldir = indir0 / ('volumes_' + Ldir['gridname'])

# set the outdir
outdir = Ldir['parent'] / 'LPM_output' / 'extract'/ 'tef'
Lfun.make_dir(outdir)

# load DataFrame of volumes, created by flux_get_vol.py
v_df = pd.read_pickle(voldir / 'volumes.p')
# index is ['J1', 'J2', 'J3',...
# columns are ['volume m3', 'area m2', 'lon', 'lat']

def inax(x,y,aa):
    # returns True if x,y, is inside of the box defined by aa
    is_in = x>aa[0] and x<aa[1] and y>aa[2] and y<aa[3]
    return is_in

aa0 = [-125.4, -122, 46.8, 50.4] # Salish Sea
aa1 = [-123.25, -122.1, 47, 48.5] # Puget Sound

plt.close('all')
lw=3
fs=16
pfun.start_plot(fs=fs)

fig = plt.figure(figsize=(14,11.5))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

ax_counter = 0
for ax in [ax1, ax2]:

    if ax_counter == 0:
        aa = aa0
    elif ax_counter == 1:
        aa = aa1

    small_sect_list = ['hc7', 'hc8', 'tn1', 'tn2', 'tn3', 'ss1']
    small_seg_list = ['S1', 'T1', 'T2', 'H6', 'H7', 'H8']
    # sections
    for sn in sect_df.index:
        if sn in small_sect_list:
            ff = .5
        else:
            ff = .7
        x0, x1, y0, y1 = sect_df.loc[sn,:]
        xx = (x0+x1)/2; yy = (y0+y1)/2
        # color
        for ch in flux_fun.channel_dict.keys():
            if sn in flux_fun.channel_dict[ch]:
                sn_color = flux_fun.c_dict[ch]
            else:
                pass
        if inax(xx,yy,aa):
            ax.plot([x0,x1], [y0,y1], '-', color=sn_color, lw=lw)
            if (ax_counter == 0) and not inax(xx,yy,aa1):
                ax.text(xx,yy, sn, fontsize=ff*fs, color='k', va='center',ha='center',
                bbox=dict(facecolor='w', edgecolor='None', alpha=0.6), style='italic', weight='bold')
            elif ax_counter == 1:
                ax.text(xx,yy, sn, fontsize=ff*fs, color='k', va='center',ha='center',
                bbox=dict(facecolor='w', edgecolor='None', alpha=0.6), style='italic', weight='bold')

    # segments
    for Sn in v_df.index:
        if Sn in small_seg_list:
            ff = .5
        else:
            ff = 1
        
        vx = v_df.loc[Sn,'lon']
        vy = v_df.loc[Sn,'lat']
        # color
        for ch in flux_fun.short_seg_dict.keys():
            if Sn in flux_fun.short_seg_dict[ch]:
                Sn_color = flux_fun.c_dict[ch]
            else:
                pass
        if inax(vx,vy,aa):
            if (ax_counter == 0) and not inax(vx,vy,aa1):
                ax.text(vx,vy, Sn,
                    va='center',ha='center', color=Sn_color,
                        fontsize=ff*fs, fontweight='bold', alpha=.8)
            elif ax_counter == 1:
                ax.text(vx,vy, Sn,
                    va='center',ha='center', color=Sn_color,
                        fontsize=ff*fs, fontweight='bold')
    
    pfun.add_coast(ax)
    pfun.dar(ax)
    ax.axis(aa)

    if ax_counter == 0:
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_xticks([-125, -124, -123])
        ax.set_yticks([47, 48, 49, 50])
        pfun.draw_box(ax1, aa1, alpha=.3, linewidth=3)
        ax.set_title('(a) Salish Sea')
        iii = 0
        for ch in flux_fun.channel_list:
            ax.text(.02, .2-iii*.05, ch, color = flux_fun.c_dict[ch],
            transform=ax.transAxes, weight='bold', size=.8*fs)
            iii += 1
    elif ax_counter == 1:
        ax.set_xlabel('Longitude')
        ax.set_xticks([-123, -122.5])
        ax.set_yticks([47, 48])
        ax.set_title('(b) Puget Sound')

    ax_counter += 1

fig.tight_layout()
plt.show()
fig.savefig(outdir / 'seg_sect_maps.png')
    
pfun.end_plot()
    