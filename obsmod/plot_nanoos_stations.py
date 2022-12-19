"""
Map of nanoos stations.
"""

"""
This focuses on property-property plots and obs-mod plots.
"""
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

# This loads the overall station file. Not perfect.
# fn = Ldir['data'] / 'obs' / 'nanoos' / 'salish_cruises-station_info.csv'
# df = pd.read_csv(fn)
# # This has columns:
# # ['Name', 'Station #', 'Description', 'Bottom Depth (m)', 'Latitude',
# #       'Longitude', 'Latitude (dec)', 'Longitude (dec)', 'Basin']
# x = df['Longitude (dec)'].to_numpy()
# y = df['Latitude (dec)'].to_numpy()
# sn = [str(int(item)) for item in df['Station #'].to_numpy()]

# out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
# out_fn = out_dir / (source + '_' + otype + '_' + year + '.p')
# df_dict = pickle.load(open(out_fn, 'rb'))

# Load the processed file
fn = Ldir['LOo'] / 'obs' / 'nanoos' / 'bottle' / 'info_2021.p'
df = pd.read_pickle(fn)

plt.close('all')
pfun.start_plot(figsize=(13,8), fs=10)

fig = plt.figure()

cc = 1
for cruise in df.cruise.unique():

    x = df.loc[df.cruise==cruise,'lon'].to_numpy()
    y = df.loc[df.cruise==cruise,'lat'].to_numpy()
    sn = [str(int(item)) for item in df.loc[df.cruise==cruise,'name'].to_numpy()]
    
    print('\n' + cruise)
    cdf = df[df.cruise==cruise]
    xx = cdf.loc[cdf.name==5,'lon'].to_numpy()[0]
    yy = cdf.loc[cdf.name==5,'lat'].to_numpy()[0]
    print('Station 5: lon=%0.3f lat=%0.3f' % (xx,yy))
    xx = cdf.loc[cdf.name==28,'lon'].to_numpy()[0]
    yy = cdf.loc[cdf.name==28,'lat'].to_numpy()[0]
    print('Station 28: lon=%0.3f lat=%0.3f' % (xx,yy))
    
    ax = fig.add_subplot(1,3,cc)
    ax.plot(x,y,'.b')
    for ii in range(len(x)):
        ax.text(x[ii],y[ii],sn[ii])
    pfun.dar(ax)
    pfun.add_coast(ax)
    ax.axis([-123.25, -122, 47, 48.5])
    
    cc += 1
    
plt.show()