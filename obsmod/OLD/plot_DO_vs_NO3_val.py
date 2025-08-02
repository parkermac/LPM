"""
This focuses on property-property plots and obs-mod plots.

It is focused on a single run and perhaps a single data source,
but allows delineation by depth, season, etc.

This one specifically is for plotting the model-obs values of DO vs. NO3,
in order to think about how to fix the NO3 accumulation in the Salish Sea.
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
small = True # True for laptop size plot

# run choices
year = '2014'
gtx = 'cas7_t0_x4b'

# data choices
otype = 'bottle'
source = 'all'
# source = 'all'
H = 20 # dividing depth for deep and shallow

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

# Set mask_salish to True to ignore stations in the Salish Sea
fil_dict['mask_salish'] = False
# Set mask_coast to True to ignore stations OUTSIDE the Salish Sea
fil_dict['mask_coast'] = True
if fil_dict['mask_salish'] and fil_dict['mask_coast']:
    print('Error: Too many spatial masks!')
    sys.exit()

# Set summer_fall = True to just plot the second half of the year, and so on
# set at most one to True!
fil_dict['summer_fall'] = True
fil_dict['winter_spring'] = False
if fil_dict['summer_fall'] and fil_dict['winter_spring']:
    print('Error: Too many time masks!')
    sys.exit()
    
# ======== APPLY FILTERS ==================================
        
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
ff_str = 'DO NO3 ' + otype + '_' + year + '_' + gtx # a string for the output .png file name

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

ax = fig.add_subplot(121)

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

    x = df_dict[gtx]['DIN (uM)'].to_numpy() - df_dict['obs']['DIN (uM)'].to_numpy()
    y = df_dict[gtx]['DO (uM)'].to_numpy() - df_dict['obs']['DO (uM)'].to_numpy()
    ax.plot(x,y,marker='.',ls='',color=c_dict[depth_range], alpha=alpha)

# add a line that relates DO loss to creation of DIN by respiration
xx = np.linspace(-20,30,10)
yy = -(138/16)* xx
ax.plot(xx,yy,'-g',lw=3)
ax.axis([-20, 30, -300, 200])
ax.grid(True)

# add labels to identify depth with colors
yy = 0
for Depth_range in c_dict.keys():
    ax.text(.05, .7 + 0.1*yy, Depth_range, c=c_dict[Depth_range],
        transform=ax.transAxes,
        fontweight='bold', ha='left')
    yy += 1

ax.set_xlabel('DIN (uM): Model - Obs')
ax.set_ylabel('DO (uM): Model - Obs')
ax.text(.9,.05,'-138/16 line',fontweight='bold',color='g',
    transform=ax.transAxes,ha='right')
ax.axhline()
ax.axvline()
        
# station map
ax = fig.add_subplot(122)
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

