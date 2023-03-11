"""
Code to explore a rivers.nc file from Aurora, in an effort to figure
out why runs with LwSrc (vertical sources for WWTPs) are blowing up.
"""

from lo_tools import Lfun
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

Ldir = Lfun.Lstart()
fn = Ldir['parent'] / 'LPM_data' / 'traps_debug_2023_03' / 'rivers.nc'
ds = xr.open_dataset(fn)

ii = 0
for rn in ds.river_name.values:
    if 'Birch' in rn:
        print('\n'+rn)
        print('ii = %d, river = %d' % (ii,ds.river[ii].values))
        #river_Vshape     (s_rho, river) float64 ...
        print('river_Xposition = %d, river_Eposition = %d, river_direction = %d' %
            (ds.river_Xposition[ii].values, ds.river_Eposition[ii].values,
            ds.river_direction[ii].values))
        print('river_transport max = %0.3f, min = %0.3f' %
            (ds.river_transport[:,ii].max(), ds.river_transport[:,ii].min()))
        print('river_Vshape:')
        Vshape = ds.river_Vshape[:,ii].values
        print(Vshape)
    ii += 1
    
ii = 0
for rn in ds.river_name.values:
    if ds.river_Xposition[ii].values in [542, 543, 544]:
        print('\n'+rn)
        print('ii = %d, river = %d' % (ii,ds.river[ii].values))
        #river_Vshape     (s_rho, river) float64 ...
        print('river_Xposition = %d, river_Eposition = %d, river_direction = %d' %
            (ds.river_Xposition[ii].values, ds.river_Eposition[ii].values,
            ds.river_direction[ii].values))
    ii += 1
    
ii = 0
for rn in ds.river_name.values:
    if ds.river_Eposition[ii].values in [1030, 1031, 1032]:
        print('\n'+rn)
        print('ii = %d, river = %d' % (ii,ds.river[ii].values))
        #river_Vshape     (s_rho, river) float64 ...
        print('river_Xposition = %d, river_Eposition = %d, river_direction = %d' %
            (ds.river_Xposition[ii].values, ds.river_Eposition[ii].values,
            ds.river_direction[ii].values))
    ii += 1

    