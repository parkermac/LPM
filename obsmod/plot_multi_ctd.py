"""
This focuses on property-property plots and obs-mod plots.
"""
import sys
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

otype = 'ctd'
year = '2017'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
out_fn = out_dir / ('multi_' + otype + '_' + year + '.p')

df_dict = pickle.load(open(out_fn, 'rb'))


plt.close('all')
pfun.start_plot(figsize=(14,12), fs=12)

gtx_list = ['cas6_v0_live', 'cas6_v00_x0mb']
c_dict = dict(zip(gtx_list,['r','b']))
t_dict = dict(zip(gtx_list,[.05,.15]))

source = 'all'

sdf_dict = dict()
if source == 'all':
    sdf_dict = df_dict.copy()
else:
    for gtx in df_dict.keys():
        sdf_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]
    
alpha = 0.3
fig = plt.figure()
vn_list = ['SA','CT','DO (uM)']
lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600)}
for ii in range(len(vn_list)):
    jj = ii + 1
    ax = fig.add_subplot(2,2,jj)
    vn = vn_list[ii]
    x = sdf_dict['obs'][vn].to_numpy()
    for gtx in gtx_list:
        y = sdf_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        if (not np.isnan(x).all()) and (not np.isnan(y).all()) and (len(x) > 0) and (len(y) > 0):
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox)
    ax.set_xlabel('Observed')
    ax.set_ylabel('Modeled')
    yy = 0
    if jj == 5:
        for gtx in c_dict.keys():
            ax.text(.95, .7 + 0.1*yy, gtx, c=c_dict[gtx], transform=ax.transAxes,
                fontweight='bold', ha='right')
            yy += 1
    ax.text(.05,.9,vn,transform=ax.transAxes, fontweight='bold')
    ax.axis([lim_dict[vn][0], lim_dict[vn][1], lim_dict[vn][0], lim_dict[vn][1]])
    ax.plot([lim_dict[vn][0], lim_dict[vn][1]], [lim_dict[vn][0], lim_dict[vn][1]],'-g')
    ax.grid(True)
    
# station map
ax = fig.add_subplot(2,2,4)
sdf_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis([-130,-122,42,52])
ax.set_xlabel('')
ax.set_ylabel('')


fig.suptitle('%s %s' % (source, year))
    
plt.show()

    
