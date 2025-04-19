"""
This is code to test getting glorys model output. It is based on code from Felipe Soares,
and then modified by me.

NOTES:

I added "copernicusmarine" to my loenv.yml to enable this. I had to create
a user account and then put the username and password in my
LO_data/accounts in a csv file.
- Use copernicusmarine.subset to get the data
- copernicusmarine.subset? gives useful info on the API
- depth is positive down and packed top-to-bottom

The REANALYSIS (hindcast) product goes from 1993 - recent past. I think
that all variables are in the reanalysis files, whereas for
the forecast you have to get them from separate files.
- Daily:
  cmems_mod_glo_phy_my_0.083deg_P1D-m
  This is the daily mean. The time stamp is midnight of the requested day
  and the averaging period is the 24 hour window centered on that time
  (based on info in a 2019 report about the Mediterranean sub-model).
  -- Performance: 1.4 minutes per daily snapshot for the LO cas7 domain (7 MB)

The FORECAST product has the last two years + (sliding window)
including 10 days of forecast.
- Hourly:
  cmems_mod_glo_phy_anfc_0.083deg_PT1H-m and etc.
  Example time range on 2025.04.02: 06/01/2022, 00:00 to 04/11/2025, 23:00
- Daily (again, the daily mean, like for the reanalysis):
  cmems_mod_glo_phy_anfc_0.083deg_P1D-m and etc. (see below for details)
  -- Performance: 1.5 minutes per daily snapshot for the LO cas7 domain (14 MB)
"""
from datetime import datetime, timedelta
import glorys_functions as gfun
from lo_tools import Lfun
Ldir = Lfun.Lstart()

do_forecast = True
do_hindcast = True

if do_forecast:
    # Test forecast product
    # dt_now = datetime.now()
    # dt = datetime(dt_now.year, dt_now.month, dt_now.day)
    dt = datetime(2025,4,15)
    dstr = dt.strftime(Lfun.ds_fmt)
    out_dir0 = Ldir['parent'] / 'LPM_output' / 'glorys'
    Lfun.make_dir(out_dir0)
    out_dir = out_dir0 / ('f' + dstr) / 'glorys' / 'Data'
    Lfun.make_dir(out_dir, clean=True)
    gfun.get_glorys_forecast(dt, out_dir, verbose=True)

if do_hindcast:
    # Test hindcast product
    dt = datetime(2018,4,15)
    dstr = dt.strftime(Lfun.ds_fmt)
    out_dir = Ldir['parent'] / 'LPM_output' / 'glorys_archive'
    Lfun.make_dir(out_dir)
    gfun.get_glorys_hindcast(dt, out_dir, verbose=True)
