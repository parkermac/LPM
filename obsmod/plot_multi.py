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

year = '2017'
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'

# specify input (created by process_multi_bottle.py and process_multi_ctd.py)
for otype in ['bottle', 'ctd']:
    in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
    df0_dict = pickle.load(open(in_fn, 'rb'))

    # where to put output figures
    out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod_plots'
    Lfun.make_dir(out_dir)

    if otype == 'bottle':
        # add DIN field
        for gtx in df0_dict.keys():
            if gtx == 'cas6_v0_live':
                df0_dict[gtx]['DIN (uM)'] = df0_dict[gtx]['NO3 (uM)']
            else:
                df0_dict[gtx]['DIN (uM)'] = df0_dict[gtx]['NO3 (uM)'] + df0_dict[gtx]['NH4 (uM)']

    # loop over a variety of choices

    if otype == 'bottle':
        source_list = ['all', 'nceiCoastal', 'nceiSalish', 'dfo1', 'ecology']
    elif otype == 'ctd':
        source_list = ['all', 'dfo1', 'ecology']
        
    for source in source_list:
        for depth_range in ['shallow', 'deep']:
            for time_range in ['spring','summer']:
            
                df_dict = df0_dict.copy()

                # ===== FILTERS ======================================================
                f_str = otype + ' ' + year + '\n\n' # a string to put for info on the map
                ff_str = otype + '_' + year # a string for the output .png file name

                # limit which sources to use
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
                if depth_range == 'all':
                    pass
                elif depth_range == 'shallow':
                    # shallow water
                    zz = -15
                    f_str += 'Z above ' + str(zz) + ' [m]\n'
                    ff_str += '_shallow'
                    for gtx in df_dict.keys():
                        df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].z >= zz,:]
                elif depth_range == 'deep':
                    # deep water
                    zz = -40
                    f_str += 'Z below ' + str(zz) + ' [m]\n'
                    ff_str += '_deep'
                    for gtx in df_dict.keys():
                        df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].z <= zz,:]
        
                # time range
                if time_range == 'all':
                    pass
                elif time_range == 'spring':
                    # specific months
                    f_str += 'Months = [4,5,6]\n'
                    ff_str += '_spring'
                    for gtx in df_dict.keys():
                        dti = pd.DatetimeIndex(df_dict[gtx].time)
                        mask = (dti.month==4) | (dti.month==5) | (dti.month==6)
                        df_dict[gtx] = df_dict[gtx].loc[mask,:]
                elif time_range == 'summer':
                    # specific months
                    f_str += 'Months = [7,8,9]\n'
                    ff_str += '_summer'
                    for gtx in df_dict.keys():
                        dti = pd.DatetimeIndex(df_dict[gtx].time)
                        mask = (dti.month==7) | (dti.month==8) | (dti.month==9)
                        df_dict[gtx] = df_dict[gtx].loc[mask,:]
                # ====================================================================

                # Plotting

                plt.close('all')
                fs = 12
                pfun.start_plot(figsize=(20,12), fs=fs)

                gtx_list = ['cas6_v0_live', 'cas6_traps2_x0mb']
                c_dict = dict(zip(gtx_list,['r','b']))
                t_dict = dict(zip(gtx_list,[.05,.15])) # vertical position of stats text

                alpha = 0.3
                fig = plt.figure()

                if otype == 'bottle':
                    vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)', 'DIC (uM)', 'TA (uM)', 'Chl (mg m-3)']
                    jj_list = [1,2,3,5,6,7,9,10,11] # indices for the data plots
                elif otype == 'ctd':
                    vn_list = ['SA','CT','DO (uM)','Chl (mg m-3)']
                    jj_list = [1,2,4,5] # indices for the data plots

                lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,600),'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
                    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}
    

                for ii in range(len(vn_list)):
                    jj = jj_list[ii]
                    if otype == 'bottle':
                        ax = fig.add_subplot(3,4,jj)
                    elif otype == 'ctd':
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

                    if otype == 'bottle':
                        if jj in [9,10,11]:
                            ax.set_xlabel('Observed')
                        if jj in [1,5,9]:
                            ax.set_ylabel('Modeled')
                    elif otype == 'ctd':
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
                if otype == 'bottle':
                    ax = fig.add_subplot(1,4,4)
                elif otype == 'ctd':
                    ax = fig.add_subplot(1,3,3)
                df_dict['obs'].plot(x='lon',y='lat',style='.g',legend=False, ax=ax)
                pfun.add_coast(ax)
                ax.axis([-130,-122,42,52])
                pfun.dar(ax)
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.text(.05,0,f_str,va='bottom',transform=ax.transAxes,fontweight='bold')

                fig.tight_layout()
                #plt.show()

                plt.savefig(out_dir / (ff_str + '.png'))

    
