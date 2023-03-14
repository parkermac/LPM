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

# specify input (created by process_multi_bottle.py)
otype = 'ctd'
year = '2017'
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
df_dict = pickle.load(open(in_fn, 'rb'))

# where to put output figure
out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod_plots'
Lfun.make_dir(out_dir)

# ===== FILTERS ======================================================
f_str = otype + ' ' + year + '\n\n' # a string to put for info on the map
ff_str = otype + '_' + year # a string for the output .png file name

# limit which sources to use
# choices: all, dfo1, ecology
source = 'all'
if source == 'all':
    # use df_dict as-is
    f_str += 'Source = all\n'
    ff_str += '_all'
else:
    # use just one source
    f_str += 'Source = ' + source + '\n'
    ff_str += '_' + source
    for gtx in df_dict.keys():
        df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]

# depth range
if True:
    # shallow water
    zz = -15
    f_str += 'Z above ' + str(zz) + ' [m]\n'
    ff_str += '_shallow'
    for gtx in df_dict.keys():
        df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].z >= zz,:]
elif False:
    # deep water
    zz = -40
    f_str += 'Z below ' + str(zz) + ' [m]\n'
    ff_str += '_deep'
    for gtx in df_dict.keys():
        df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].z <= zz,:]
        
# time range
if True:
    # specific months
    f_str += 'Months = [7,8,9]\n'
    ff_str += '_summer'
    for gtx in df_dict.keys():
        dti = pd.DatetimeIndex(df_dict[gtx].time)
        mask = (dti.month==9) | (dti.month==10)
        df_dict[gtx] = df_dict[gtx].loc[mask,:]
elif False:
    # specific months
    f_str += 'Months = [4,5,6]\n'
    ff_str += '_spring'
    for gtx in df_dict.keys():
        dti = pd.DatetimeIndex(df_dict[gtx].time)
        mask = (dti.month==9) | (dti.month==10)
        df_dict[gtx] = df_dict[gtx].loc[mask,:]
# ====================================================================

# Plotting

plt.close('all')
fs = 12
pfun.start_plot(figsize=(18,12), fs=fs)

gtx_list = ['cas6_v0_live', 'cas6_v00_x0mb']
c_dict = dict(zip(gtx_list,['r','b']))
t_dict = dict(zip(gtx_list,[.05,.15])) # vertical position of stats text

alpha = 0.1
fig = plt.figure()

vn_list = ['SA','CT','DO (uM)', 'Chl (mg m-3)']
lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}
    
jj_list = [1,2,4,5] # indices for the data plots
for ii in range(len(vn_list)):
    jj = jj_list[ii]
    ax = fig.add_subplot(2,3,jj)
    vn = vn_list[ii]
    x = df_dict['obs'][vn].to_numpy()
    for gtx in gtx_list:
        y = df_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        
        if (not np.isnan(x).all()) and (not np.isnan(y).all()) and (len(x) > 0) and (len(y) > 0):
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox,
                fontsize=fs-1,style='italic')
                
    if jj in [4,5]:
        ax.set_xlabel('Observed')
    if jj in [1,4]:
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
ax = fig.add_subplot(1,3,3)
df_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
pfun.add_coast(ax)
ax.axis([-130,-122,42,52])
pfun.dar(ax)
ax.set_xlabel('')
ax.set_ylabel('')
ax.text(.05,0,f_str,va='bottom',transform=ax.transAxes,fontweight='bold')

fig.tight_layout()
plt.show()

plt.savefig(out_dir / (ff_str + '.png'))

    
