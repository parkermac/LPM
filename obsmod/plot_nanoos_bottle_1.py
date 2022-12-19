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

fig = plt.figure()
    
plt.show()

    
