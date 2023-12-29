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
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'

# plotting choices
testing = False
small = False # True for laptop size plot

# run choices
year = '2014'
# gtx = 'cas6_v0_live'
# gtx = 'cas6_traps2_x2b'
# gtx = 'cas2k_v0_x2b'
# gtx = 'cas7_trapsV00_meV00'
gtx = 'cas7_t0_x4b'

# data choices
otype = 'bottle'
# source = 'nceiSalish'
source = 'all'
H = 10 # dividing depth for deep and shallow

# specify input (created by process_multi_bottle.py)
in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
df0_dict = pickle.load(open(in_fn, 'rb'))

# where to put output figures
out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod_val_plots'
Lfun.make_dir(out_dir)

# add DIN field
for gtxo in df0_dict.keys():
    if gtxo == 'cas6_v0_live':
        df0_dict[gtxo]['DIN (uM)'] = df0_dict[gtxo]['NO3 (uM)']
        df0_dict[gtxo]['NO3 (uM)'] = np.nan
    else:
        df0_dict[gtxo]['DIN (uM)'] = df0_dict[gtxo]['NO3 (uM)'] + df0_dict[gtxo]['NH4 (uM)']

# ========= SET FILTERS =============================================

fil_dict = dict() # dict to hold filter choices

# Set nitri = True to force some or all NH4 to be nitrified to NO3 in the model,
# but not in the observations.
fil_dict['nitri'] = False
# RESULT: does not make a huge difference, 10% improvement in bias and
# rmse for deep DO. 50% improvement in deep NH4 bias and rmse.

# Set alk_cons = True to use the TA(salt) equation from fennel.h instead
# of the non-conservative one we calculated.
fil_dict['alk_cons'] = False
# RESULT: This gives significantly better results for TA!

# Set mask_salish to True to ignore stations in the Salish Sea
fil_dict['mask_salish'] = False
# Set mask_coast to True to ignore stations OUTSIDE the Salish Sea
fil_dict['mask_coast'] = False
if fil_dict['mask_salish'] and fil_dict['mask_coast']:
    print('Error: Too many spatial masks!')
    sys.exit()

# Set summer_fall = True to just plot the second half of the year, and so on
# set at most one to True!
fil_dict['summer_fall'] = False
fil_dict['winter_spring'] = False
if fil_dict['summer_fall'] and fil_dict['winter_spring']:
    print('Error: Too many time masks!')
    sys.exit()
    
# ======== APPLY FILTERS ==================================

if fil_dict['nitri']:
    if gtx != 'cas6_v0_live':
        df0_dict[gtx]['DO (uM)'] -= 2 * df0_dict[gtx]['NH4 (uM)']/2
        df0_dict[gtx]['TA (uM)'] -= 2 * df0_dict[gtx]['NH4 (uM)']/2
        df0_dict[gtx]['NO3 (uM)'] += df0_dict[gtx]['NH4 (uM)']/2
        df0_dict[gtx]['NH4 (uM)'] *= 0.5
    else:
        print('Cannot use nitri flag with cas6_v0_live (no NH4)')
    
if fil_dict['alk_cons']:
    df0_dict[gtx]['TA (uM)'] = 587.05 + 50.56*df0_dict[gtx]['SA']
        
# mask out Salish Fields
if fil_dict['mask_salish']:
    for gtxo in df0_dict.keys():
        a = df0_dict[gtxo].copy()
        mask1 = (a.lat>=46) & (a.lat<49) & (a.lon>-124)
        mask2 = (a.lat>=49) & (a.lat<51) & (a.lon>-125)
        a = a.loc[(~mask1) & (~mask2),:]
        df0_dict[gtxo] = a
        
# mask out Coastal Fields
if fil_dict['mask_coast']:
    for gtxo in df0_dict.keys():
        a = df0_dict[gtxo].copy()
        mask1 = (a.lat>=47) & (a.lat<49) & (a.lon>-124)
        mask2 = (a.lat>=49) & (a.lat<51) & (a.lon>-125)
        mask = (~mask1) & (~mask2)
        a = a.loc[~mask,:]
        df0_dict[gtxo] = a
        
# mask time range:
if fil_dict['summer_fall']:
    for gtxo in df0_dict.keys():
        a = df0_dict[gtxo].copy()
        mask = (a.time>pd.Timestamp(int(year),6,30))
        a = a.loc[mask,:]
        df0_dict[gtxo] = a
elif fil_dict['winter_spring']:
    for gtxo in df0_dict.keys():
        a = df0_dict[gtxo].copy()
        mask = (a.time<=pd.Timestamp(int(year),6,30))
        a = a.loc[mask,:]
        df0_dict[gtxo] = a

# start assembling some text for the plot that will include info about the filters
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

for fil in fil_dict.keys():
    if fil_dict[fil]:
        f_str += 'Filter: %s\n' % (fil)

# PLOTTING

plt.close('all')

vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)',
    'DIC (uM)', 'TA (uM)']#, 'Chl (mg m-3)']
jj_list = [1,2,3,5,6,7,9,10,11] # indices for the data plots

lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),
    'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}

if small:
    fs = 10
    pfun.start_plot(figsize=(13,8), fs=fs)
else:
    fs = 14
    pfun.start_plot(figsize=(20,12), fs=fs)

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
        if (vn == 'TA (uM)') and fil_dict['alk_cons']:
            ax.text(.05,.8,'* Using Alkalinty(salt) *',transform=ax.transAxes, fontweight='bold')
            
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

plt.show()
if not testing:
    plt.savefig(out_dir / (ff_str + '.png'))

    
