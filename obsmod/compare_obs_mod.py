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
gtx = 'cas7_t0_x4b'

# data choices
otype = 'bottle'
source = 'all'
H = 10 # dividing depth for deep and shallow

# overrides for testing
if testing:
    year_list = [2019]
    # source = 'nceiCoastal'
    # small = True
else:
    year_list = range(2013,2024)

# prepare for plotting
plt.close('all')
if small:
    fs = 12
    pfun.start_plot(figsize=(10.75,8.75), fs=fs)
else:
    fs = 14
    pfun.start_plot(figsize=(14,12), fs=fs)

for year in year_list:
    year = str(year)

    # specify input (created by process_multi_bottle.py)
    in_fn = in_dir / ('combined_' + otype + '_' + year + '_' + gtx + '.p')
    df0_dict = pickle.load(open(in_fn, 'rb'))

    # ========= SET FILTERS =============================================

    fil_dict = dict() # dict to hold filter choices

    # Set mask_salish to True to ignore stations in the Salish Sea
    fil_dict['mask_salish'] = False
    # Set mask_coast to True to ignore stations OUTSIDE the Salish Sea
    fil_dict['mask_coast'] = False
    if fil_dict['mask_salish'] and fil_dict['mask_coast']:
        print('Error: Too many spatial masks!')
        sys.exit()

    # Set summer_fall = True to just plot the second half of the year, and so on.
    # set at most one to True!
    fil_dict['summer_fall'] = False
    fil_dict['winter_spring'] = False
    if fil_dict['summer_fall'] and fil_dict['winter_spring']:
        print('Error: Too many time masks!')
        sys.exit()

    # add symbols for the bio variables calculated using regressions
    # vs. salt

    # ======= USE FILTERS TO HELP NAME OUTPUT DIRECTORY ===================
    # where to put output figures
    ocp_string = 'obsmod_compare_plots'
    for key in fil_dict.keys():
        if fil_dict[key] == True:
            ocp_string += '_' + key
    out_dir = Ldir['parent'] / 'LPM_output' / ocp_string
    Lfun.make_dir(out_dir)
        
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

    vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)',
        'DIC (uM)', 'TA (uM)']
    jj_list = [1,2,3,4,5,7,8] # indices for the data plots

    lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),
        'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),
        'DIC (uM)':(1500,2600),'TA (uM)':(1500,2600),'Chl (mg m-3)':(0,20)}

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
                ax = fig.add_subplot(3,3,jj)
                ax_dict[ii] = ax
            else:
                ax = ax_dict[ii]
            vn = vn_list[ii]

            plot_this_var = True
            try:
                x = df_dict['obs'][vn].to_numpy()
                y = df_dict[gtx][vn].to_numpy()
            except KeyError:
                print('No values for ' + vn)
                plot_this_var = False

            if plot_this_var:

                ax.plot(x,y,marker='.',ls='',color=c_dict[depth_range], alpha=alpha)

                if (not np.isnan(x).all()) and (not np.isnan(y).all()) and (len(x) > 0) and (len(y) > 0):
                    bias = np.nanmean(y-x)
                    rmse = np.sqrt(np.nanmean((y-x)**2))
                    ax.text(.95,t_dict[depth_range],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),
                        c=c_dict[depth_range],
                        transform=ax.transAxes, ha='right', fontweight='bold', bbox=pfun.bbox,
                        fontsize=fs*.9,style='italic')

            # For uniformity, add axes even of there is no data for this variable.
            # Axis labels
            if jj in [7,8]:
                ax.set_xlabel('Observed')
            if jj in [1,4,7]:
                ax.set_ylabel('Modeled')
            # Identify depth range
            if jj == 1:
                yy = 0
                for Depth_range in c_dict.keys():
                    ax.text(.05, .7 + 0.1*yy, Depth_range, c=c_dict[Depth_range],
                        transform=ax.transAxes,
                        fontweight='bold', ha='left')
                    yy += 1
            # Identify variable and set limits.
            ax.text(.05,.9,vn,transform=ax.transAxes, fontweight='bold')
            ax.axis([lim_dict[vn][0], lim_dict[vn][1], lim_dict[vn][0], lim_dict[vn][1]])
            ax.plot([lim_dict[vn][0], lim_dict[vn][1]], [lim_dict[vn][0], lim_dict[vn][1]],'-g')
            ax.grid(True)
            
    # station map
    ax = plt.subplot2grid((3,3), (1,2), rowspan=2)
    df_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
    pfun.add_coast(ax)
    ax.axis([-130,-122,42,52])
    ax.set_xticks([-130,-126,-122])
    ax.set_yticks([45,50])
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

    
