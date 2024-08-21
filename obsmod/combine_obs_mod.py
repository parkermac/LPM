"""
Code to combine observed and modeled bottle values for a collection
of sources. This is designed to work for one or more gtagex, and assumes the
model run is using the newer ROMS bgc code, with NH4.

It creates a dict of pandas DataFrames with both observed
and model values: df_dict['obs'], df_dict[gtx_list[0]], etc.

The intention is that each DataFrame has EXACTLY the same rows,
except for the data values.

It assumes you have run cast extractions for the given gtagex for
all the years and sources you will be using.

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

# user choices
otype = 'bottle'
year_list = range(2013,2024)
gtx_list = ['cas7_t0_x4b']
source_list = ['dfo1', 'ecology_nc', 'nceiSalish', 'nceiCoastal',
    'LineP', 'nceiPNW', 'NHL', 'WOD', 'ocnms_ctd']

testing = True
if testing:
    source_list = ['LineP']
    year_list = [2019]

for year in year_list:

    year = str(year)
    print('\n===== ' + year + ' ==========')

    out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
    Lfun.make_dir(out_dir)
    out_fn = out_dir / ('combined_' + otype + '_' + year +  + '_' + gtx'.p')

    # initialize a dict of empty DataFrames that we will concatenate on
    df_dict = {}
    df_dict['obs'] = pd.DataFrame()
    for gtx in gtx_list:
        df_dict[gtx] = pd.DataFrame()

    # Intialize a cast id starting value. We will increment this as we go
    # through the sources so that the final DataFrames have unique cid values
    # for each cast.
    cid0 = 0

    for source in source_list:
        print(source)
        
        # load observations and associated info file
        info_fn = Ldir['LOo'] / 'obs' / source / otype / ('info_' + year + '.p')
        obs_fn = Ldir['LOo'] / 'obs' / source / otype / (year + '.p')
        
        try:
            info_df = pd.read_pickle(info_fn)
        except FileNotFoundError:
            print('-- no file')
            continue # this jumps to the next source in source_list
            
        obs_df = pd.read_pickle(obs_fn)
        obs_df['source'] = source

        if testing:
            cid_list = list(info_df.index)[:3]
        else:
            cid_list = list(info_df.index)
            
        vn_list = ['CT', 'SA','Chl (mg m-3)', 'DO (uM)',
            'NO3 (uM)', 'NO2 (uM)' 'NH4 (uM)', 'TA (uM)', 'DIC (uM)']
        
        mod_dir_dict = {}
        for gtx in gtx_list:
            mod_dir_dict[gtx] = (Ldir['LOo'] / 'extract' / gtx / 'cast' /
            (source + '_' + otype + '_' + year))

        # Fill DataFrames with model extractions,
        # matching the format of the observations.

        for gtx in gtx_list:
        
            mod_df = obs_df.copy()
            
            mod_df['source'] = source
            # add a "source" columm, e.g. filled with "ecology_nc"
            
            for vn in vn_list:
                mod_df[vn] = np.nan
                # Note: what if there are data variables, like PO4 (uM) in
                # obs_df? The algorithm as written here will leave them
                # in mod_df, but they should not be there.
                # Also this will add columns to mod_df that are not in
                # obs_df...?
        
            ii = 0
            for cid in cid_list:
            
                fn = mod_dir_dict[gtx] / (str(int(cid)) + '.nc')
                if fn.is_file(): # useful for testing, and for missing casts
                    ds = xr.open_dataset(fn)
                    # check on which bio variables to get
                    if ii == 0:
                        if 'NH4' in ds.data_vars:
                            npzd = 'new'
                        else:
                            npzd = 'none'
                
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
                    if npzd in == 'new':
                        mod_df.loc[mod_df.cid==cid, 'NO3 (uM)'] = ds.NO3[iz_list].values
                        mod_df.loc[mod_df.cid==cid, 'DO (uM)'] = ds.oxygen[iz_list].values
                        mod_df.loc[mod_df.cid==cid, 'DIC (uM)'] = ds.TIC[iz_list].values
                        mod_df.loc[mod_df.cid==cid, 'TA (uM)'] = ds.alkalinity[iz_list].values
                        mod_df.loc[mod_df.cid==cid, 'NH4 (uM)'] = ds.NH4[iz_list].values
                        mod_df.loc[mod_df.cid==cid, 'Chl (mg m-3)'] = ds.chlorophyll[iz_list].values
                
                    ii += 1
            
                else:
                    mod_df.loc[mod_df.cid==cid, vn_list] = np.nan
                
            print('-- processed %d casts' % (ii))
            sys.stdout.flush()

            mod_df = mod_df[['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'source']+vn_list]
                        
            mod_df['cid'] += cid0
                    
            df_dict[gtx] = pd.concat((df_dict[gtx], mod_df.copy()), ignore_index=True)
            
        obs_df['cid'] += cid0
        df_dict['obs'] = pd.concat((df_dict['obs'], obs_df.copy()), ignore_index=True)
        cid0 = obs_df.cid.max() + 1
        
    pickle.dump(df_dict, open(out_fn, 'wb'))
