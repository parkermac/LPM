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

source = 'multi'
otype = 'bottle'
year = '2017'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
out_fn = out_dir / (source + '_' + otype + '_' + year + '.p')

df_dict = pickle.load(open(out_fn, 'rb'))

# add DIN field
for gtx in df_dict.keys():
    if gtx == 'cas6_v0_live':
        df_dict[gtx]['DIN (uM)'] = df_dict[gtx]['NO3 (uM)']
    else:
        df_dict[gtx]['DIN (uM)'] = df_dict[gtx]['NO3 (uM)'] + df_dict[gtx]['NH4 (uM)']

plt.close('all')
pfun.start_plot(figsize=(14,12), fs=12)

gtx_list = ['cas6_v0_live', 'cas6_v00_uu0mb']
c_dict = dict(zip(gtx_list,['b','r']))

source = 'all'
    
alpha = 0.3
fig = plt.figure()
vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)', 'DIC (uM)', 'TA (uM)']
lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500)}
t_dict = dict(zip(gtx_list,[.05,.15,.25]))
for ii in range(len(vn_list)):
    jj = ii + 1
    ax = fig.add_subplot(3,3,jj)
    vn = vn_list[ii]
    if source == 'all':
        x = df_dict['obs'][vn].to_numpy()
    else:
        x = df_dict['obs'].loc[df_dict['obs'].source==source, vn].to_numpy()
    for gtx in gtx_list:
        if source == 'all':
            y = df_dict[gtx][vn].to_numpy()
        else:
            y = df_dict[gtx].loc[df_dict[gtx].source==source, vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        if not np.isnan(y).all():
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox)
    if jj in [4,5,6]:
        ax.set_xlabel('Observed')
    if jj in [1,4]:
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

fig.suptitle('%s %s' % (source, year))
    
plt.show()

    
