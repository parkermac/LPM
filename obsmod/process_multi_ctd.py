"""
Code to combine various observed and modeled bottle values for a collection
of sources.

Performance: runs in about a minute for two gtx's.
"""

import sys
import pandas as pd
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import gsw
import pickle

from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

testing = False

source_list = ['ecology', 'dfo1']
otype = 'ctd'
year = '2017'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
Lfun.make_dir(out_dir)
out_fn = out_dir / ('multi_' + otype + '_' + year + '.p')

gtx_list = ['cas6_v0_live', 'cas6_v00_x0mb']

# initialize a dict of empty DataFrames that we will concatenate on
df_dict = {}
df_dict['obs'] = pd.DataFrame()
for gtx in gtx_list:
    df_dict[gtx] = pd.DataFrame()

cid0 = 0
for source in source_list:
    print('\n'+source)
    
    # load observations
    info_fn = Ldir['LOo'] / 'obs' / source / otype / ('info_' + year + '.p')
    obs_fn = Ldir['LOo'] / 'obs' / source / otype / (year + '.p')
    info_df = pd.read_pickle(info_fn)
    obs_df = pd.read_pickle(obs_fn)
    obs_df['source'] = source
    if testing:
        cid_list = [list(info_df.index)[0]]
    else:
        cid_list = list(info_df.index)
        
    vn_list = ['CT', 'SA','DO (uM)']
    
    mod_dir_dict = {}
    for gtx in gtx_list:
        mod_dir_dict[gtx] = (Ldir['LOo'] / 'extract' / gtx / 'cast' /
        (source + '_' + otype + '_' + year))

    # Fill DataFrames with model extractions, matching the format of the observations.

    for gtx in gtx_list:
    
        mod_df = obs_df.copy()
        
        mod_df['source'] = source
        
        for vn in vn_list:
            mod_df[vn] = np.nan
    
        ii = 0
        for cid in cid_list:
        
            fn = mod_dir_dict[gtx] / (str(int(cid)) + '.nc')
            if fn.is_file(): # useful for testing, and for missing casts
                ds = xr.open_dataset(fn)
        
                print('Processing ' + fn.name)
                sys.stdout.flush()
            
                oz = obs_df.loc[obs_df.cid==cid,'z'].to_numpy()
                mz = ds.z_rho.values
            
                iz_list = []
                for z in oz:
                    iz_list.append(zfun.find_nearest_ind(mz,z))
            
                # convert everything to the obs variables
                SP = ds.salt[iz_list].values
                z = ds.z_rho[iz_list].values
                PT = ds.temp[iz_list].values
                lon = info_df.loc[cid,'lon']
                lat = info_df.loc[cid,'lat']
                p = gsw.p_from_z(z, lat)
                SA = gsw.SA_from_SP(SP, p, lon, lat)
                CT = gsw.CT_from_pt(SA, PT)
                
                mod_df.loc[mod_df.cid==cid, 'SA'] = SA
                mod_df.loc[mod_df.cid==cid, 'CT'] = CT
                mod_df.loc[mod_df.cid==cid, 'DO (uM)'] = ds.oxygen[iz_list].values
            
                ii += 1
        
            else:
                mod_df.loc[mod_df.cid==cid, vn_list] = np.nan
            
        mod_df = mod_df[['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'source']+vn_list]
                    
        mod_df['cid'] += cid0
                
        df_dict[gtx] = pd.concat((df_dict[gtx], mod_df.copy()), ignore_index=True)
        
    obs_df['cid'] += cid0
    df_dict['obs'] = pd.concat((df_dict['obs'], obs_df.copy()), ignore_index=True)
    cid0 = obs_df.cid.max() + 1
    
pickle.dump(df_dict, open(out_fn, 'wb'))
