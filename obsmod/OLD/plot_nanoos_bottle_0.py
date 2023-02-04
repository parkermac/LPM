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

source = 'nanoos'
otype = 'bottle'
year = '2021'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
out_fn = out_dir / (source + '_' + otype + '_' + year + '.p')

df_dict = pickle.load(open(out_fn, 'rb'))

# add DIN field
for gtx in df_dict.keys():
    if gtx == 'cas6_v0_live':
        df_dict[gtx]['DIN (uM)'] = df_dict[gtx]['NO3 (uM)']
    else:
        df_dict[gtx]['DIN (uM)'] = df_dict[gtx]['NO3 (uM)'] + df_dict[gtx]['NH4 (uM)']


plt.close('all')
pfun.start_plot(figsize=(13,8), fs=10)

gtx_list = ['cas6_v0_live','cas6_v00NegNO3_uu0mb','cas6_v00Stock_uu0mb']
c_dict = dict(zip(gtx_list,['c','b','r']))

fig = plt.figure()
alpha=.3
# xy_list = [('SA','CT'),('DO (uM)','NO3 (uM)'), ('DO (uM)','z'), ('NO3 (uM)','z')]
xy_list = [('DO (uM)','NO3 (uM)'), ('DO (uM)','z'), ('NO3 (uM)','z'), ('NH4 (uM)','z'), ('DIN (uM)','z')]
for ii in range(5):
    ax = fig.add_subplot(2,3,ii+1)
    x, y = xy_list[ii]
    for gtx in gtx_list:
        df_dict[gtx].plot(x=x,y=y,marker='.',ls='',color=c_dict[gtx],ax=ax,legend=False,alpha=alpha)
    df_dict['obs'].plot(x=x,y=y,style='.k',ax=ax,legend=False)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    yy = 0
    if ii == 0:
        for gtx in c_dict.keys():
            ax.text(.95, .9 - 0.1*yy, gtx, c=c_dict[gtx], transform=ax.transAxes,
                fontweight='bold', ha='right')
            yy += 1
    

fig = plt.figure()
vn_list = ['SA','CT','DO (uM)','NO3 (uM)','NH4 (uM)','DIN (uM)']
lim_dict = {'SA':(22,34),'CT':(7,20),'DO (uM)':(-10,600),'NO3 (uM)':(-.1,50),'NH4 (uM)':(-.1,10),'DIN (uM)':(-.1,50)}
t_dict = dict(zip(gtx_list,[.05,.15,.25]))
for ii in range(len(vn_list)):
    jj = ii + 1
    ax = fig.add_subplot(2,3,jj)
    vn = vn_list[ii]
    x = df_dict['obs'][vn].to_numpy()
    for gtx in gtx_list:
        y = df_dict[gtx][vn].to_numpy()
        ax.plot(x,y,marker='.',ls='',color=c_dict[gtx], alpha=alpha)
        if not np.isnan(y).all():
            bias = np.nanmean(y-x)
            rmse = np.sqrt(np.nanmean((y-x)**2))
            ax.text(.95,t_dict[gtx],'bias=%0.1f, rmse=%0.1f' % (bias,rmse),c=c_dict[gtx],
                transform=ax.transAxes, ha='right')
    if jj in [4,5,6]:
        ax.set_xlabel('Observed')
    if jj in [1,4]:
        ax.set_ylabel('Modeled')
    yy = 0
    if jj == 5:
        for gtx in c_dict.keys():
            ax.text(.95, .9 - 0.1*yy, gtx, c=c_dict[gtx], transform=ax.transAxes,
                fontweight='bold', ha='right')
            yy += 1
    ax.text(.05,.9,vn,transform=ax.transAxes)
    ax.axis([lim_dict[vn][0], lim_dict[vn][1], lim_dict[vn][0], lim_dict[vn][1]])
    ax.grid(True)
    
plt.show()

    
