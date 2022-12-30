"""
This focuses on plots that identify when and where the biggest model
errors orrur.
"""
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

source = 'nanoos'
otype = 'bottle'
year = '2021'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
out_fn = out_dir / (source + '_' + otype + '_' + year + '.p')

df_dict = pickle.load(open(out_fn, 'rb'))

plt.close('all')
pfun.start_plot(figsize=(13.5,8), fs=12)

gtx_list = ['cas6_v0_live','cas6_v00NegNO3_uu0mb','cas6_v00_uu0mb']


# sequences of stations
sta_list_mb = [26, 22, 21, 20, 7, 28, 29, 30, 31, 33, 35, 38, 36]
sta_list_hc = [8, 10, 17, 15, 14, 13, 401, 12, 11, 402]
sta_list_w = [5, 1, 3, 4]

# legend size
leg_dict = {'NO3 (uM)':25, 'NH4 (uM)':2}

obs_df = df_dict['obs']
gtx = gtx_list[2]
mod_df = df_dict[gtx]

# get time information, specifically the month of each cruise
cruise_list = list(obs_df.cruise.unique())
date_list = []
for cruise in cruise_list:
    date_list.append(obs_df.loc[obs_df.cruise==cruise,'time'].iloc[0])
cruise_dict = dict(zip(date_list, cruise_list))
date_list.sort()

fig = plt.figure()

vn = 'NH4 (uM)'

cc = 0
for this_date in date_list:
    cruise = cruise_dict[this_date]
    ax = plt.subplot2grid((3,3), (cc,0), colspan=2)
    #ax = fig.add_subplot(3,1,cc)
    if cc == 0:
        ax.set_title('%s  (%s)  %s' % (gtx, year, vn))
    ii = 0
    for sn in sta_list_mb + sta_list_hc + sta_list_w:
        o = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), vn].to_numpy()
        oz = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), 'z'].to_numpy()
        m = mod_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), vn].to_numpy()
        mz = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), 'z'].to_numpy()
        mo = m - o
        for jj in range(len(mo)):
            M = m[jj]
            O = o[jj]
            MO = mo[jj]
            Z = oz[jj]
            
            if False:
                # plot model-obs difference
                fac_dict = {'NH4 (uM)':1, 'NO3 (uM)':0.6, 'DO (uM)':0.05}
                if MO >=0:
                    c = 'r'
                else:
                    c = 'b'
                ax.plot(ii,Z, marker='o', ls='', ms=fac_dict[vn]*np.abs(MO), c=c)
            else:
                # plot obs and model at the same time
                fac_dict = {'NH4 (uM)':1, 'NO3 (uM)':0.4, 'DO (uM)':0.05}
                ax.plot(ii,Z, marker='o', ls='', ms=fac_dict[vn]*O, c='r', alpha=.3)
                ax.plot(ii,Z, marker='o', ls='', ms=fac_dict[vn]*M, mfc='None', mec='k')
                
        ax.set_ylabel('Z (m)')
        
        # add a vertical line between station sequences
        if sn in [sta_list_mb[-1], sta_list_hc[-1]]:
            ax.axvline(ii+.5)
            
        # add a legend
        if (sn == sta_list_hc[0]) and (cc==0):
            ax.plot(ii+.5,-220, marker='o', ls='',
                ms=fac_dict[vn]*leg_dict[vn],
                mfc='b', mec='b', alpha=.5)
            ax.text(ii+1,-220,'%s = %d' % (vn, leg_dict[vn]), c = 'b',
                fontweight='bold', va='center')
        
        # add station labels
        if cc == 2:
            if sn in sta_list_mb:
                sn_c = 'm'
            elif sn in sta_list_hc:
                sn_c = 'c'
            elif sn in sta_list_w:
                sn_c = 'g'
            ax.text(ii,-200,sn,ha='center',va='center',rotation=60,style='italic',c=sn_c)
            ax.set_xlabel('Station')
            
        # add month info
        ax.text(.05,.25, 'Month = %d' % (this_date.month), fontweight='bold',
            transform=ax.transAxes)
            
        ii += 1
    cc += 1
    ax.set_xlim(-1,27)
    ax.set_ylim(-250,25)
    ax.set_xticks([])
    
# add a map
# Load the processed file
info_fn = Ldir['LOo'] / 'obs' / 'nanoos' / 'bottle' / 'info_2021.p'
info_df = pd.read_pickle(info_fn)
cruise = cruise_list[1]
x = info_df.loc[info_df.cruise==cruise,'lon'].to_numpy()
y = info_df.loc[info_df.cruise==cruise,'lat'].to_numpy()
sn = [int(item) for item in info_df.loc[info_df.cruise==cruise,'name'].to_numpy()]
ax = fig.add_subplot(1,3,3)
for ii in range(len(x)):
    if sn[ii] in sta_list_mb:
        sn_c = 'm'
    elif sn[ii] in sta_list_hc:
        sn_c = 'c'
    elif sn[ii] in sta_list_w:
        sn_c = 'g'
    else:
        sn_c = 'gray'
    ax.plot(x[ii],y[ii],marker='o',c=sn_c)
    ax.text(x[ii]+.06,y[ii],sn[ii],c=sn_c,
        ha='center',va='center',rotation=60,style='italic')
pfun.dar(ax)
pfun.add_coast(ax, color='gray')
ax.axis([-123.2, -122.2, 47, 48.5])
ax.set_xticks([])
ax.set_yticks([])

plt.show()

    
