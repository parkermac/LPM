"""
Code to use copernicusmarine to get info
about products, e.g. the time range available.
"""

import copernicusmarine as cm
import pandas as pd
from lo_tools import Lfun
Ldir = Lfun.Lstart()

# get Copernicus login credentials
cred_fn = Ldir['data'] / 'accounts' / 'glorys_pm_2025.04.02.csv'
cred_dict = Lfun.csv_to_dict(cred_fn)

dsid_list = [
    'cmems_mod_glo_phy_my_0.083deg_P1D-m',
    'cmems_mod_glo_phy_myint_0.083deg_P1D-m',
    'cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m'
]

for dsid in dsid_list:
    print('\n'+dsid)
    data = cm.open_dataset(dataset_id=dsid,
        username=cred_dict['username'],
        password=cred_dict['password'])
    if 'time' in data.dims:
        start_date = data['time'][0].values
        end_date = data['time'][-1].values
    dt0 = pd.Timestamp(start_date)
    dt1 = pd.Timestamp(end_date)
    print(dt0.strftime(Lfun.ds_fmt))
    print(dt1.strftime(Lfun.ds_fmt))


