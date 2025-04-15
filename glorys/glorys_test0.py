
'''
This is code to test getting glorys model output. It is based on code from Felipe Soares,
and then modified by me.

NOTES:

I added "copernicusmarine" to my loenv.yml to enable this. I had to create
a user account and then put the username and password in my
LO_data/accounts in a csv file.
- Use copernicusmarine.subset to get the data
- copernicusmarine.subset? gives useful info on the API

depth is positive down and packed top-to-bottom

The REANALYSIS product goes from 1993 - recent past. I think
that all variables are in the reanalysis files, whereas for
the forecast you have to get them from separate files.
- Daily:
  cmems_mod_glo_phy_my_0.083deg_P1D-m
  This is the daily mean. The time stamp is midnight of the requested day
  and the averaging period is the 24 hour window centered on that time
  (based on info in a 2019 report about the Mediterranean sub-model).

The FORECAST product has the last two years + (sliding window)
including 10 days of forecast. It
- Hourly:
  cmems_mod_glo_phy_anfc_0.083deg_PT1H-m and etc.
  Example time range on 2025.04.02: 06/01/2022, 00:00 to 04/11/2025, 23:00
- Daily:
  cmems_mod_glo_phy_anfc_0.083deg_P1D-m and etc. (see below for details)
- Performance: 5 minutes per daily snapshot for the LO cas7 domain (14 MB)

'''
import copernicusmarine
from datetime import datetime, timedelta
from time import time
import xarray as xr

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# get Copernicus login credentials
cred_fn = Ldir['data'] / 'accounts' / 'glorys_pm_2025.04.02.csv'
cred_dict = Lfun.csv_to_dict(cred_fn)

# name the output file
out_dir0 = Ldir['parent'] / 'LPM_output' / 'glorys'
Lfun.make_dir(out_dir0)

# set lat-lon limits
aa = [-131, -121, 41, 53]
#aa = [-127, -126.5, 45, 45.3] # testing

if True:
    tt00 = time()
    # Daily average from forecast.
    # For the forecast you have to get each variable separately.
    # set variables to get
    vn_list = ['so', 'thetao', 'zos','cur']
    #vn_list = ['cur'] # testing

    tt0 = time()
    dt_now = datetime.now()
    dt = datetime(dt_now.year, dt_now.month, dt_now.day)
    f_dstr = dt.strftime(Lfun.ds_fmt)
    out_dir = out_dir0 / ('f' + f_dstr) / 'glorys' / 'Data'
    Lfun.make_dir(out_dir, clean=True)

    dstr = dt.strftime('%Y-%m-%dT%H:%M:%S')
    for vn in vn_list:
        if vn == 'zos':
            dataset_id='cmems_mod_glo_phy_anfc_0.083deg_P1D-m'
        else:
            dataset_id='cmems_mod_glo_phy-'+vn+'_anfc_0.083deg_P1D-m'
        if vn == 'cur':
            variables=['uo','vo']
        else:
            variables=[vn]

        out_name = 'forecast_'+vn+'.nc'
        
        copernicusmarine.subset(
            dataset_id=dataset_id,
            variables=variables,

            minimum_longitude=aa[0],
            maximum_longitude=aa[1],
            minimum_latitude=aa[2],
            maximum_latitude=aa[3],

            start_datetime=dstr,
            end_datetime=dstr,

            output_filename=out_name,
            output_directory=str(out_dir),

            username=cred_dict['username'],
            password=cred_dict['password'],
            overwrite=True,
            disable_progress_bar=True
        )
        print('\nTime to get %s at one time = %0.1f' % (vn, time()-tt0))

        out_fn = out_dir / out_name
        ds = xr.open_dataset(out_fn)
        print(ds)
        ds.close()

    print('\nTime to get all variables = %0.1f' % (time()-tt00))


if False:
    # Daily average from renalaysis
    # For reanalysis you can get all variables in one file.
    # set variables to get
    vn_list = ['uo', 'vo', 'so', 'thetao', 'zos']
    tt0 = time()
    out_name = 'glorys_reanalysis_test0_daily.nc'
    dt = datetime(2018, 2, 26)
    dstr = dt.strftime('%Y-%m-%dT%H:%M:%S')

    copernicusmarine.subset(
        dataset_id='cmems_mod_glo_phy_my_0.083deg_P1D-m',
        variables=vn_list,

        minimum_longitude=aa[0],
        maximum_longitude=aa[1],
        minimum_latitude=aa[2],
        maximum_latitude=aa[3],
        start_datetime=dstr,
        end_datetime=dstr,

        output_filename=out_name,
        output_directory=str(out_dir),
        username=cred_dict['username'],
        password=cred_dict['password'],
        overwrite=True,
        disable_progress_bar=True
    )
    print('time to get all variables at one time = %0.1f' % (time()-tt0))


