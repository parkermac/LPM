"""
Code to plot obs and mod casts at a given station, typically from ecology.
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
otype = 'ctd'
in_fn = in_dir / ('multi_' + otype + '_' + year + '.p')
df_dict = pickle.load(open(in_fn, 'rb'))

source = 'ecology'
for gtx in df_dict.keys():
    df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].source==source,:]
    
name = 'HCB003'
for gtx in df_dict.keys():
    df_dict[gtx] = df_dict[gtx].loc[df_dict[gtx].name==name,:]
"""
HCB003 is around Hoodsport
HCB004 is near Alderbrook
HCB007 is closer to thehead of Lynch Cove
"""
    
# plotting
plt.close('all')
#pfun.start_plot(figsize=(20,12))
pfun.start_plot(figsize=(12,8))
fig = plt.figure()

c_dict = {'obs':'k', 'cas6_v0_live':'r', 'cas6_traps2_x1b':'b'}

cid_list = df_dict['obs'].cid.unique()
cid_list.sort()
ii = 1
for cid in cid_list:
    ax = fig.add_subplot(2,6,ii)
    for gtx in df_dict.keys():
        x = df_dict[gtx].loc[df_dict[gtx].cid==cid,'DO (uM)'].to_numpy()
        y = df_dict[gtx].loc[df_dict[gtx].cid==cid,'z'].to_numpy()
        ax.plot(x,y,'-o',c=c_dict[gtx])
    ii += 1
    #ax.set_xlim(20,32)
    
plt.show()
