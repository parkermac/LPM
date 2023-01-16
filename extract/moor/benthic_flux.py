"""
Code to explore benthic flux from a mooring extraction.

"""
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

from lo_tools import plotting_functions as pfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

sn = 'dabob'
gtx = 'cas6_v00_uu0mb'
date_str = '2017.01.01_2017.12.31'

# out_dir = Ldir['parent'] / 'LPM_output' / 'benthic_flux'
# Lfun.make_dir(out_dir)

plt.close('all')
in_dir = Ldir['LOo'] / 'extract' / gtx / 'moor'
fn = in_dir / (sn + '_' + date_str + '.nc')
ds = xr.open_dataset(fn)

# time
ot = ds.ocean_time.values
ot_dt = pd.to_datetime(ot)
t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
T = t/86400 # time in days from start

pfun.start_plot(figsize=(18,10))
fig = plt.figure()
ii = 1
for vn in ['NO3','NH4','oxygen','alkalinity','TIC','SdetritusN','LdetritusN']:
    
    ax = fig.add_subplot(3,3,ii)
    v = ds[vn][:,0].values
    ax.plot(T,v,'-b')
    ax.grid(True)
    ax.text(.05,.9,vn, fontweight='bold', transform=ax.transAxes)
    ax.set_xlim(T[0],T[-1])
    
    ii += 1
plt.show()
