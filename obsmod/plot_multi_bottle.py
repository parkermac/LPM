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

otype = 'bottle'
year = '2017'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
out_fn = out_dir / ('multi_' + otype + '_' + year + '.p')

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
c_dict = dict(zip(gtx_list,['r','b']))

source = 'all'#'nceiCoastal'
sdf_dict = dict()
if source == 'all':
    sdf_dict['obs'] = df_dict['obs']
    for gtx in gtx_list:
        sdf_dict[gtx] = df_dict[gtx]
else:
    sdf_dict['obs'] = df_dict['obs'].loc[df_dict['obs'].source==source,:]
    for gtx in gtx_list:
        sdf_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]
        
    
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
    x = sdf_dict['obs'][vn].to_numpy()
    for gtx in gtx_list:
        y = sdf_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        if not np.isnan(y).all():
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox)
    if jj in [7,8]:
        ax.set_xlabel('Observed')
    if jj in [1,4,7]:
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
ax = fig.add_subplot(3,3,9)
sdf_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis([-130,-122,42,52])
ax.set_xlabel('')
ax.set_ylabel('')


fig.suptitle('%s %s' % (source, year))
    
plt.show()

    
