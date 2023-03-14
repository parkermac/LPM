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
fs = 12
pfun.start_plot(figsize=(20,12), fs=fs)

gtx_list = ['cas6_v0_live', 'cas6_v00_x0mb']
c_dict = dict(zip(gtx_list,['r','b']))
t_dict = dict(zip(gtx_list,[.05,.15]))

# limit which sources to use
source = 'all'
sdf_dict = dict()
if source == 'all':
    sdf_dict = df_dict.copy()
else:
    for gtx in df_dict.keys():
        sdf_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]

# Other filters
if False:
    # shallow water
    zz = -15
    for gtx in sdf_dict.keys():
        sdf_dict[gtx] = sdf_dict[gtx].loc[sdf_dict[gtx].z >= zz,:]
elif False:
    # deep water
    zz = -50
    for gtx in sdf_dict.keys():
        sdf_dict[gtx] = sdf_dict[gtx].loc[sdf_dict[gtx].z <= zz,:]
elif True:
    # specific months
    for gtx in sdf_dict.keys():
        dti = pd.DatetimeIndex(sdf_dict[gtx].time)
        mask = (dti.month==9) | (dti.month==10)
        sdf_dict[gtx] = sdf_dict[gtx].loc[mask,:]
    

alpha = 0.1
fig = plt.figure()

vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)', 'DIC (uM)', 'TA (uM)', 'Chl (mg m-3)']
lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}
    
jj_list = [1,2,3,5,6,7,9,10,11] # indices for the data plots
for ii in range(len(vn_list)):
    jj = jj_list[ii]
    ax = fig.add_subplot(3,4,jj)
    vn = vn_list[ii]
    x = sdf_dict['obs'][vn].to_numpy()
    for gtx in gtx_list:
        y = sdf_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        
        if (not np.isnan(x).all()) and (not np.isnan(y).all()) and (len(x) > 0) and (len(y) > 0):
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox,
                fontsize=fs-1,style='italic')
                
    if jj in [9,10,11]:
        ax.set_xlabel('Observed')
    if jj in [1,5,9]:
        ax.set_ylabel('Modeled')
        
    # add labels to identify the model runs with the colors
    if jj == 1:
        yy = 0
        for gtx in c_dict.keys():
            ax.text(.05, .7 + 0.1*yy, gtx, c=c_dict[gtx], transform=ax.transAxes,
                fontweight='bold', ha='left')
            yy += 1
            
    ax.text(.05,.9,vn,transform=ax.transAxes, fontweight='bold')
    ax.axis([lim_dict[vn][0], lim_dict[vn][1], lim_dict[vn][0], lim_dict[vn][1]])
    ax.plot([lim_dict[vn][0], lim_dict[vn][1]], [lim_dict[vn][0], lim_dict[vn][1]],'-g')
    ax.grid(True)
    
# station map
ax = fig.add_subplot(1,4,4)
sdf_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
pfun.add_coast(ax)
pfun.dar(ax)
ax.axis([-130,-122,42,52])
ax.set_xlabel('')
ax.set_ylabel('')

fig.suptitle('%s %s %s' % (source, otype, year))
    
plt.show()

    
