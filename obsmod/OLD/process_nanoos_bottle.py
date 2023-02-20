"""
Code to compare various observed and modeled bottle values for nanoos cruises.

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

source = 'nanoos'
otype = 'bottle'
year = '2021'

out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
Lfun.make_dir(out_dir)
out_fn = out_dir / (source + '_' + otype + '_' + year + '.p')

# load observations
info_fn = Ldir['LOo'] / 'obs' / source / otype / ('info_' + year + '.p')
obs_fn = Ldir['LOo'] / 'obs' / source / otype / (year + '.p')
info_df = pd.read_pickle(info_fn)
obs_df = pd.read_pickle(obs_fn)

# prepare to load model extractions
if testing:
    gtx_list = ['cas6_v0_live']
    cid_list = [list(info_df.index)[0]]
else:
    gtx_list = ['cas6_v0_live', 'cas6_v00NegNO3_uu0mb', 'cas6_v00Stock_uu0mb']
    cid_list = list(info_df.index)
    
mod_dir_dict = {}
for gtx in gtx_list:
    mod_dir_dict[gtx] = (Ldir['LOo'] / 'extract' / gtx / 'cast' /
    (source + '_' + otype + '_' + year))

# Fill DataFrames with model extractions, matching the format of the observations.
df_dict = {}
for gtx in gtx_list:
    df_dict[gtx] = obs_df.copy()

for gtx in gtx_list:
    
    mod_df = df_dict[gtx]
    
    ii = 0
    for cid in cid_list:
        
        fn = mod_dir_dict[gtx] / (str(int(cid)) + '.nc')
        if fn.is_file(): # useful for testing, and for missing casts
            ds = xr.open_dataset(fn)
            # check on which bio variables to get
            if ii == 0:
                if 'NH4' in ds.data_vars:
                    npzd = 'new'
                elif 'NO3' in ds.data_vars:
                    npzd = 'old'
                else:
                    npzd = 'none'
        
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
            if npzd in ['new', 'old']:
                mod_df.loc[mod_df.cid==cid, 'NO3 (uM)'] = ds.NO3[iz_list].values
                mod_df.loc[mod_df.cid==cid, 'DO (uM)'] = ds.oxygen[iz_list].values
            if npzd == 'new':
                mod_df.loc[mod_df.cid==cid, 'NH4 (uM)'] = ds.NH4[iz_list].values
            if npzd == 'old':
                mod_df.loc[mod_df.cid==cid, 'NH4 (uM)'] = np.nan
    
            
            # obs_df columns:
            # ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'CT', 'SA',
            #        'DO (uM)', 'NO3 (uM)', 'NO2 (uM)', 'NH4 (uM)', 'PO4 (uM)', 'SiO4 (uM)',
            #        'Fluor (ug/L)', 'ChlA (ug/L)', 'Phaeo (ug/L)', 'TA (umol/kg)',
            #        'DIC (umol/kg)', 'Secchi (m)']
            
            # list of ds.data_vars:
            # npzd = 'new'
            # ['AKs','Cs_r','Cs_w','LdetritusN','NO3','NH4,'TIC','alkalinity',
            # 'SdetritusN','h','hc','oxygen','phytoplankton','chlorophyll','salt','temp','zeta',
            # 'zooplankton','z_rho','z_w']
            #
            # npzd = 'old'
            # ['AKs','Cs_r','Cs_w','Ldetritus','NO3','TIC','alkalinity',
            # 'detritus','h','hc','oxygen','phytoplankton','salt','temp','zeta',
            # 'zooplankton','z_rho','z_w']
            
            ii += 1
        
        else:
            mod_df.loc[mod_df.cid==cid, ['SA', 'CT', 'DO (uM)', 'NO3 (uM)', 'NH4 (uM)']] = np.nan
            
            
    mod_df = mod_df[['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'CT', 'SA',
                'DO (uM)', 'NO3 (uM)', 'NH4 (uM)']]
                
    df_dict[gtx] = mod_df
    
df_dict['obs'] = obs_df
pickle.dump(df_dict, open(out_fn, 'wb'))
