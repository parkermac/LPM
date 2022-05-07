"""
Plot a time series of volume-integrated buoyancy flux.  Focused
on a high-resolution nested model of Admiralty Inlet.
"""

import xarray as xr
import numpy as np
import seawater as sw
import pandas as pd

from lo_tools import Lfun, zrfun

Ldir = Lfun.Lstart(gridname='ai0', tag='v0', ex_name='n0k')

fn_list = Lfun.get_fn_list('hourly', Ldir, '2018.01.01', '2018.01.14')

if False:
    fn_list = fn_list[:5]

ot_list = []
eta_list = []
fb_list = []
mix_list = []

for fn in fn_list:
    print(fn.name)
    if fn == fn_list[0]:
        G, S, T = zrfun.get_basic_info(fn)
        DA = G['DX'] * G['DY']
        DA[G['mask_rho']==0] = np.nan
        A = np.nansum(DA)
        
    ds = xr.open_dataset(fn)
    
    ot = ds.ocean_time.values[0]
    ot_list.append(ot)
    
    # Calculate volume-integrated buoyancy flux
    rho = sw.dens0(ds.salt.values.squeeze(), ds.temp.values.squeeze())
    fb = -9.8 * np.sum(ds.AKs[0,1:-1,:,:].squeeze() * np.diff(rho, axis=0), axis=0).values # [W m-2]
    Fb = np.nansum(DA * fb) # [W]
    fb_list.append(Fb)
    
    # Calculate area-mean SSH
    eta = ds.zeta.values.squeeze()
    Eta = np.nansum(DA * eta) / A
    eta_list.append(Eta) # Are
    
    # Calculate volume-integrated salinity variance mixing
    zr = zrfun.get_z(G['h'], eta, S, only_rho=True)
    dz = np.diff(zr, axis=0) # dz on w-grid [1:-1]
    dsalt = np.diff(ds.salt[0,:,:,:].squeeze(), axis=0)
    mix_a = np.sum(ds.AKs[0,1:-1,:,:].values.squeeze() * dsalt * dsalt / dz, axis=0)
    mix = np.nansum(mix_a * DA)
    mix_list.append(mix)
    
df = pd.DataFrame(index=ot_list)
df['Eta'] = eta_list
df['Fb'] = fb_list
df['Mix'] = mix_list

out_dir = Ldir['parent'] / 'LPM_output' / 'buoyancy_flux'
Lfun.make_dir(out_dir)
out_fn = out_dir / 'AI_highres.p'
df.to_pickle(out_fn)

