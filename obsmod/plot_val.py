"""
This focuses on property-property plots and obs-mod plots.

It is focused on a single run and perhaps a single data source,
but allows delineation by depth, season, etc.
"""
import sys
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

testing = True

# Set nitri = True to force all NH4 to be nitrified to NO3 in the model,
# but not in the observations.
nitri = False
# RESULT: does not make a huge difference, 10% improvement in bias and
# rmse for deep DO. 50% improvement in deep NH4 bias and rmse.

year = '2017'
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'

plt.close('all')

#gtx = 'cas6_v0_live'
gtx = 'cas6_traps2_x2b'
otype = 'bottle'
source = 'nceiSalish'
H = 10

# specify input (created by process_multi_bottle.py)
in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
df0_dict = pickle.load(open(in_fn, 'rb'))

# where to put output figures
out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod_val_plots'
Lfun.make_dir(out_dir)

if nitri == True:
    gtxo = 'cas6_traps2_x2b'
    df0_dict[gtxo]['DO (uM)'] -= 2 * df0_dict[gtxo]['NH4 (uM)']
    df0_dict[gtxo]['TA (uM)'] -= 2 * df0_dict[gtxo]['NH4 (uM)']
    df0_dict[gtxo]['NO3 (uM)'] += df0_dict[gtxo]['NH4 (uM)']
    df0_dict[gtxo]['NH4 (uM)'] = 0

# add DIN field
for gtxo in df0_dict.keys():
    if gtxo == 'cas6_v0_live':
        df0_dict[gtxo]['DIN (uM)'] = df0_dict[gtxo]['NO3 (uM)']
        df0_dict[gtxo]['NO3 (uM)'] = np.nan
    else:
        df0_dict[gtxo]['DIN (uM)'] = df0_dict[gtxo]['NO3 (uM)'] + df0_dict[gtxo]['NH4 (uM)']

# ===== FILTERS ======================================================
f_str = otype + ' ' + year + '\n' + gtx + '\n' # a string to put for info on the map
ff_str = otype + '_' + year + '_' + gtx # a string for the output .png file name

# limit which sources to use
if source == 'all':
    # use df_dict as-is
    f_str += 'Source = all\n'
    ff_str += '_all'
else:
    # use just one source
    f_str += 'Source = ' + source + '\n'
    ff_str += '_' + source
    for gtxo in df0_dict.keys():
        df0_dict[gtxo] = df0_dict[gtxo].loc[df0_dict[gtxo].source==source,:]
        
f_str += 'Dividing depth = %d m\n' % (H)

# Plotting

vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)',
    'DIC (uM)', 'TA (uM)']#, 'Chl (mg m-3)']
jj_list = [1,2,3,5,6,7,9,10,11] # indices for the data plots

lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),
    'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}

fs = 10
# pfun.start_plot(figsize=(20,12), fs=fs)
pfun.start_plot(figsize=(13,8), fs=fs)

depth_list = ['deep', 'shallow']
c_dict = dict(zip(depth_list,['b','r']))
t_dict = dict(zip(depth_list,[.05,.15])) # vertical position of stats text

alpha = 0.3
fig = plt.figure()

ax_dict = {}
for depth_range in depth_list:
    
    df_dict = df0_dict.copy()
    
    # depth range
    if depth_range == 'shallow':
        # shallow water
        zz = -H
        for gtxo in df_dict.keys():
            df_dict[gtxo] = df_dict[gtxo].loc[df_dict[gtxo].z >= zz,:]
    elif depth_range == 'deep':
        # deep water
        zz = -H
        for gtxo in df_dict.keys():
            df_dict[gtxo] = df_dict[gtxo].loc[df_dict[gtxo].z <= zz,:]

    for ii in range(len(vn_list)):
        jj = jj_list[ii]
        if depth_range == depth_list[0]:
            ax = fig.add_subplot(3,4,jj)
            ax_dict[ii] = ax
        else:
            ax = ax_dict[ii]
        vn = vn_list[ii]
        x = df_dict['obs'][vn].to_numpy()
        y = df_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[depth_range], alpha=alpha)

        if (not np.isnan(x).all()) and (not np.isnan(y).all()) and (len(x) > 0) and (len(y) > 0):
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[depth_range],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),
                c=c_dict[depth_range],
                transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox,
                fontsize=fs*.7,style='italic')

        if jj in [9,10,11]:
            ax.set_xlabel('Observed')
        if jj in [1,5,9]:
            ax.set_ylabel('Modeled')

        # add labels to identify the model runs with the colors
        if jj == 1:
            yy = 0
            for Depth_range in c_dict.keys():
                ax.text(.05, .7 + 0.1*yy, Depth_range, c=c_dict[Depth_range],
                    transform=ax.transAxes,
                    fontweight='bold', ha='left')
                yy += 1

        ax.text(.05,.9,vn,transform=ax.transAxes, fontweight='bold')
        ax.axis([lim_dict[vn][0], lim_dict[vn][1], lim_dict[vn][0], lim_dict[vn][1]])
        ax.plot([lim_dict[vn][0], lim_dict[vn][1]], [lim_dict[vn][0], lim_dict[vn][1]],'-g')
        ax.grid(True)
        
# station map
ax = fig.add_subplot(1,4,4)
df_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
pfun.add_coast(ax)
ax.axis([-130,-122,42,52])
pfun.dar(ax)
ax.set_xlabel('')
ax.set_ylabel('')
ax.text(.05,0,f_str,va='bottom',transform=ax.transAxes,fontweight='bold')

fig.tight_layout()

print('Plotting ' + ff_str)
sys.stdout.flush()

if testing:
    plt.show()
else:
    plt.savefig(out_dir / (ff_str + '.png'))
    plt.close('all')

    
