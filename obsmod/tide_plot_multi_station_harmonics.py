"""
Code to compare harmonics from observed and modeled SSH time series at 
multiple tide stations and for multiple model runs.

Designed to give a nice graphical sumary of amplitude and phase, by constituent,
along a sequence of different stations.

Assumes the harmonics have already been calculated using tide_get_harmonics.py.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import tide_fun as tfun
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

in_dir = Ldir['parent'] / 'LPM_output' / 'tide'
year_str = '2022'

# organize DataFrames by specific lines
name_list_S = ['Charleston', 'South Beach', 'Garibaldi', 'Toke Point',
    'Westport', 'La Push', 'Neah Bay',]
name_list_SoG = ['Victoria Harbor', 'Friday Harbor', 'Cherry Point',
    'Vancouver', 'Point Atkinson', 'Campbell River']
name_list_PS = ['Port Angeles', 'Port Townsend', 'Seattle', 'Tacoma']

name_list_S_SoG = name_list_S + name_list_SoG
name_list_S_PS = name_list_S + name_list_PS
name_list_dict = {'SoG': name_list_S_SoG, 'PS': name_list_S_PS}
title_dict = {'SoG': 'to Strait of Georgia', 'PS': 'to Puget Sound'}

gtagex_list = ['obs', 'cas7_t0_x4b', 'cas7_t1_x4', 'cas7_t1_x4tf']
clist = 'rybg'

plt.close('all')

for key in name_list_dict.keys():
    name_list = name_list_dict[key]

    pfun.start_plot(figsize=(23,10))
    fig = plt.figure()

    gg = 0 # gtagex counter
    for gtagex in gtagex_list:
        in_fn = in_dir / (gtagex + '_' + year_str + '_harmonics_sn_df.p')
        sn_df = pd.read_pickle(in_fn)

        sn_df_1 = pd.DataFrame()
        for name in name_list:
            row = sn_df.loc[sn_df.name==name,:]
            sn_df_1 = pd.concat((sn_df_1,row))

        # make a distance column
        lon = sn_df_1.lon.to_numpy()
        lat = sn_df_1.lat.to_numpy()
        x, y = zfun.ll2xy(lon, lat, lon[0], lat[0])
        dist = 0 * x
        N = len(x)
        for ii in range(1,N):
            d = np.sqrt((x[ii]-x[ii-1])**2 + (y[ii]-y[ii-1])**2)
            dist[ii] = dist[ii-1] + d/1000
        sn_df_1['dist'] = dist

        if (gg == 0):

            # plot all stations on a map

            ax = fig.add_subplot(151)
            pfun.add_coast(ax)
            ax.axis([-127, -122, 43, 51])
            pfun.dar(ax)
            ax.set_title(title_dict[key])
            nn = 0
            for sn in sn_df.index:
                lon = sn_df.loc[sn,'lon']
                lat = sn_df.loc[sn,'lat']
                name = sn_df.loc[sn,'name']
                if name == 'Neah Bay':
                    nn_nb = nn
                    ax.plot(lon,lat,'oy', markersize=20)
                else:
                    ax.plot(lon,lat,'og')
                ax.text(lon,lat,name,fontsize=8,rotation=45)
                nn += 1
            for sn in sn_df_1.index:
                lon = sn_df_1.loc[sn,'lon']
                lat = sn_df_1.loc[sn,'lat']
                ax.plot(lon,lat,'*r',markersize=12)

            # Save a copy of sn_df_1 from "obs" to adjust phase.
            sn_df_obs = sn_df_1.copy()

            # set up axes for data plots
            N = len(tfun.hn_list)
            ax_list = []
            for ii in range(N):
                ax_list.append(plt.subplot2grid((N,5), (ii,1), colspan=2))
            gax_list = []
            for ii in range(N):
                gax_list.append(plt.subplot2grid((N,5), (ii,3), colspan=2))

        dist = sn_df_1.dist.to_numpy()

        # Amplitude
        N = len(tfun.hn_list)
        for ii in range(N):
            hn = tfun.hn_list[ii]
            ax = ax_list[ii]
            A = sn_df_1.loc[:,hn + '_A'].to_numpy()
            ax.plot(dist[nn_nb],A[nn_nb],'-oy',markersize=10)
            ax.plot(dist,A,'-*'+clist[gg],label=gtagex)
            ax.text(.05,.8,hn,transform=ax.transAxes)
            ax.set_ylim(0,1.2)
            ax.grid(True)
            if (ii == N-1):
                ax.set_xlabel('Distance (km)')
            else:
                ax.set_xticklabels([])

        # Phase
        for ii in range(N):
            hn = tfun.hn_list[ii]
            ax = gax_list[ii]
            G = sn_df_1.loc[:,hn + '_G'].to_numpy()
            Gobs = sn_df_obs.loc[:,hn + '_G'].to_numpy()
            for k in range(len(G)-1):
                if (G[k+1] - G[k]) < -180:
                    G[k+1] += 360
            G = G - Gobs[0] # start line relative to observed phase
            ax.plot(dist[nn_nb],G[nn_nb],'-oy',markersize=10)
            ax.plot(dist,G,'-*'+clist[gg])
            ax.text(.05,.8,hn,transform=ax.transAxes)
            ax.set_ylim(-10,200)
            ax.grid(True)
            if (ii == N-1):
                ax.set_xlabel('Distance (km)')
            else:
                ax.set_xticklabels([])

        gg += 1

        ax_list[0].legend(ncols=2)
        ax_list[0].set_title('Amplitude (m)')
        gax_list[0].set_title('Phase (deg)')
    fig.savefig(in_dir / ('multi_station_harmonics_' + key + '.png'))

plt.show()

