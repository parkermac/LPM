"""
Code to plot obs and mod casts at a given station, typically from ecology because
Those are monthly time series at a named location.

This is just a modification of plot_casts to look at different combinations of x and y variables.
"""

import sys
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

year = '2015'
in_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'

# choices
sta_name = 'HCB010'
# vnx = 'NO3 (uM)'
# vny = 'DO (uM)'
vnx = 'SA'
vny = 'CT'
"""
HCB003 is around Hoodsport
HCB004 is near Alderbrook
HCB007 is closer to the head of Lynch Cove
HCB010 is near the connection to Dabob Bay

Look for a station map plot in LO_data/obs/ecology.
"""

# specify input (created by process_multi_bottle.py and process_multi_ctd.py)
otype = 'ctd'
in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
df_dict = pickle.load(open(in_fn, 'rb'))

source = 'ecology'
for gtx in df_dict.keys():
    df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]
    
for gtx in df_dict.keys():
    df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].name==sta_name,:]

# dicts to help with plotting
lim_dict = {'SA':(14,36),'CT':(0,20),'DO (uM)':(0,500),
    'NO3 (uM)':(0,50),'NH4 (uM)':(0,10),'DIN (uM)':(0,50),
    'DIC (uM)':(1500,2500),'TA (uM)':(1500,2500),'Chl (mg m-3)':(0,20)}
    
c_list = ['r','b','y','c']
c_dict = {'obs':'k'}
ii = 0
for gtx in df_dict.keys():
    if gtx == 'obs':
        pass
    else:
        c_dict[gtx] = c_list[ii]
        ii += 1
    
    
# plotting
plt.close('all')
pfun.start_plot(figsize=(20,10))
#pfun.start_plot(figsize=(12,8))
fig = plt.figure()

cid_list = df_dict['obs'].cid.unique()
cid_list.sort()
ii = 1
zbot = 0
ax_dict = dict()
for cid in cid_list:
    mo = df_dict[gtx].loc[df_dict[gtx].cid==cid,'time'].to_list()[0].month
    ax = fig.add_subplot(2,6,ii)
    for gtx in df_dict.keys():
        x = df_dict[gtx].loc[df_dict[gtx].cid==cid,vnx].to_numpy()
        y = df_dict[gtx].loc[df_dict[gtx].cid==cid,vny].to_numpy()
        if otype == 'bottle':
            ax.plot(x,y,'-o',c=c_dict[gtx])
        elif otype == 'ctd':
            ax.plot(x,y,'-',c=c_dict[gtx])
        ax.text(.05,.05,'Month=%d' % (mo),transform=ax.transAxes,
            fontweight='bold',bbox=pfun.bbox)
        ax.set_xlim(lim_dict[vnx])
        ax.set_ylim(lim_dict[vny])
    ax_dict[ii] = ax
    ax.set_xlim(lim_dict[vnx])
    if ii not in [1,7]:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel(vny)
    ax.set_xlabel(vnx)
    ax.grid(True)
    if ii == 1:
        jj = 0
        for gtx in df_dict.keys():
            ax.text(.05,.9-jj/10,gtx,color=c_dict[gtx],transform=ax.transAxes,
                fontweight='bold',bbox=pfun.bbox)
            jj += 1
    ii += 1
    
fig.suptitle('Station: %s, %s' % (sta_name,year))
plt.show()
