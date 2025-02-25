"""
Code to compare observed and modeled SSH time series at tide stations.

Designed to give a nice graphical sumary of results from multiple
stations, and for several model runs.
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
name_list = name_list_S + name_list_SoG # combine into one line

gtagex_list = ['obs', 'cas7_t0_x4b', 'cas7_t1_x4', 'cas7_t1_x4tf']
clist = 'rybg'

gg = 0
for gtagex in gtagex_list:
    print(gtagex)

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

    if gg == 0:
        plt.close('all')

        # plot all stations on a map
        pfun.start_plot(figsize=(20,10))
        fig = plt.figure()
        ax = fig.add_subplot(151)
        pfun.add_coast(ax)
        ax.axis([-127, -122, 43, 51])
        pfun.dar(ax)
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

        # set up axes for data plots
        N = len(tfun.hn_list)
        ax_list = []
        for ii in range(N):
            print(ii)
            ax_list.append(plt.subplot2grid((N,5), (ii,1), colspan=2))

        gax_list = []
        for ii in range(N):
            print(ii)
            gax_list.append(plt.subplot2grid((N,5), (ii,3), colspan=2))

        # Go_dict = dict()

    dist = sn_df_1.dist.to_numpy()
    N = len(tfun.hn_list)
    for ii in range(N):
        hn = tfun.hn_list[ii]
        ax = ax_list[ii]
        A = sn_df_1.loc[:,hn + '_A'].to_numpy()
        ax.plot(dist[nn_nb],A[nn_nb],'-oy',markersize=10)
        ax.plot(dist,A,'-*'+clist[gg])
        ax.text(.05,.8,hn,transform=ax.transAxes)
        ax.set_ylim(0,1.2)

    for ii in range(N):
        hn = tfun.hn_list[ii]
        ax = gax_list[ii]
        G = sn_df_1.loc[:,hn + '_G'].to_numpy()
        # if gtagex == 'obs':
        #     Go_dict[hn] = G
        # # fix when phase difference straddles 360
        # for jj in range(len(G)):
        #     if (G[jj] - Go_dict[hn][jj]) > 180:
        #         G[jj] = G[jj] - 360
        #     elif (G[jj] - Go_dict[hn][jj]) < -180:
        #         G[jj] = G[jj] + 360
        ax.plot(dist[nn_nb],G[nn_nb],'-oy',markersize=10)
        ax.plot(dist,G,'-*'+clist[gg])
        ax.text(.05,.8,hn,transform=ax.transAxes)

    gg += 1

plt.show()

