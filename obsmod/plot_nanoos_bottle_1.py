"""
This focuses on plots that identify when and where the biggest model
errors orrur.
"""
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

plt.close('all')
pfun.start_plot(figsize=(13,8), fs=10)

gtx_list = ['cas6_v0_live','cas6_v00NegNO3_uu0mb','cas6_v00_uu0mb']
c_dict = dict(zip(gtx_list,['c','b','r']))

cruise_list = ['RC0051', 'RC0058', 'RC0063']

# sequences of stations
sta_list_mb = [26, 22, 21, 20, 7, 28, 29, 30, 31, 33, 35, 38, 36]
sta_list_hc = [8, 10, 17, 15, 14, 13, 401, 12, 11, 402]
sta_list_w = [5, 1, 3, 4]

obs_df = df_dict['obs']
mod_df = df_dict['cas6_v00NegNO3_uu0mb']

fac_dict = {'NH4 (uM)':1, 'NO3 (uM)':0.6, 'DO (uM)':0.05}

fig = plt.figure()

vn = 'NO3 (uM)'

cc = 1
for cruise in cruise_list:
    ax = fig.add_subplot(3,1,cc)
    if cc == 1:
        ax.set_title(vn)
    ii = 0
    for sn in sta_list_mb + sta_list_hc + sta_list_w:
        o = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), vn].to_numpy()
        oz = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), 'z'].to_numpy()
        m = mod_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), vn].to_numpy()
        mz = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), 'z'].to_numpy()
        mo = m - o
        for jj in range(len(mo)):
            MO = mo[jj]
            Z = oz[jj]
            if MO >=0:
                c = 'r'
            else:
                c = 'b'
            ax.plot(ii,Z, marker='o', ls='', ms=fac_dict[vn]*np.abs(MO), c=c)
        if sn in [sta_list_mb[-1], sta_list_hc[-1]]:
            ax.axvline(ii+.5)
        ii += 1
    cc += 1
    ax.set_xlim(-1,27)
plt.show()

    
