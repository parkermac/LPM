"""
Code to combine observed and modeled bottle values for a collection
of sources. This is designed to work for one gtagex, and assumes the
model run is using the newer ROMS bgc code, with NH4.

It does both bottle and ctd by default, saving the output in files named:
combined_[bottle,ctd]_[year]_[gtagex].p

It should also work automatically for runs with no bgc, but that is untested.

It creates a dict of two pandas DataFrames with both observed
and model values: df_dict['obs'] and df_dict[[gtagex]]

Each DataFrame has EXACTLY the same rows, except for the data values.

It assumes you have run cast extractions for the given gtagex(s) for
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
source_list = ['dfo1', 'ecology_nc', 'nceiSalish', 'nceiCoastal',
    'LineP', 'nceiPNW', 'NHL', 'WOD', 'ocnms_ctd']
otype_list = ['bottle','ctd']
year_list = [2017]
#gtx = 'cas7_t1_x11ab'
gtx = 'cas7_t0_x4b'

testing = False

for otype in otype_list:

    for year in year_list:

        year = str(year)
        print('\n===== ' + year + ' ==========')

        out_dir = Ldir['parent'] / 'LPM_output' / 'obsmod'
        Lfun.make_dir(out_dir)
        out_fn = out_dir / ('combined_' + otype + '_' + year + '_' + gtx + '.p')

        # initialize a dict of empty DataFrames that we will concatenate on
        df_dict = {}
        df_dict['obs'] = pd.DataFrame()
        df_dict[gtx] = pd.DataFrame()

        # Intialize a cast id starting value. We will increment this as we go
        # through the sources so that the final DataFrames have unique cid values
        # for each cast.
        cid0 = 0

        vn_list0 = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z', 'source']
        # these are all the non-data columns.

        vn_list = ['CT', 'SA','Chl (mg m-3)', 'DO (uM)', 'Chl (mg m-3)',
                'NO3 (uM)', 'NH4 (uM)', 'TA (uM)', 'DIC (uM)']
        vn_list_no_bgc = ['CT', 'SA']
        # these are all the model (and possibly obs) data columns for a run with or without bgc

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

            # hack for bad DO in nceiCoastal for 2021
            if (year=='2021') & (source=='nceiCoastal'):
                print('>> hack for bad DO <<')
                obs_df.loc[:,'DO (uM)'] = np.nan

            if testing:
                cid_list = list(info_df.index)[:3]
                # this will work even if there are fewer than the requested cid's.
            else:
                cid_list = list(info_df.index)
                
            vn_list = ['CT', 'SA', 'DO (uM)', 'Chl (mg m-3)',
                'NO3 (uM)', 'NH4 (uM)', 'TA (uM)', 'DIC (uM)']
            
            mod_dir = (Ldir['LOo'] / 'extract' / gtx / 'cast' / (source + '_' + otype + '_' + year))

            # Fill DataFrames with model extractions,
            # matching the format of the observations.
            
            mod_df = obs_df.copy()
            
            mod_df['source'] = source
            # add a "source" columm, e.g. filled with "ecology_nc"
            
            for vn in vn_list:
                mod_df[vn] = np.nan
            # make sure data columns are numeric
            mod_df.loc[:,vn_list] = mod_df.loc[:,vn_list].apply(pd.to_numeric)
        
            ii = 0
            for cid in cid_list:
            
                fn = mod_dir / (str(int(cid)) + '.nc')
                if fn.is_file(): # useful for testing, and for missing casts
                    ds = xr.open_dataset(fn)
                    # check on which bio variables to get
                    if ii == 0:
                        if 'NH4' in ds.data_vars:
                            do_bgc = True
                        else:
                            do_bgc = False
                            vn_list = vn_list_no_bgc
                            obs_df = obs_df[vn_list0+vn_list_no_bgc]
                            mod_df = mod_df[vn_list0+vn_list_no_bgc]
                
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
                    if do_bgc:
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

            mod_df = mod_df[vn_list0+vn_list]
                        
            mod_df['cid'] += cid0
                    
            df_dict[gtx] = pd.concat((df_dict[gtx], mod_df.copy()), ignore_index=True)
                
            obs_df['cid'] += cid0
            df_dict['obs'] = pd.concat((df_dict['obs'], obs_df.copy()), ignore_index=True)
            cid0 = obs_df.cid.max() + 1
            
        pickle.dump(df_dict, open(out_fn, 'wb'))
