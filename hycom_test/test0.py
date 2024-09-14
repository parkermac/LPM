# Code based on that from Ivica Janeković, ivica.jan@gmail.com

import os
import numpy as np
# from netCDF4 import Dataset, num2date
from datetime import datetime, timedelta
import xarray as xr
import cftime
from time import time
from lo_tools import Lfun

Ldir = Lfun.Lstart()

# separate for each variable
# url_temp = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_t3z/FMRC_ESPC-D-V02_t3z_best.ncd'
# url_salt = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_s3z/FMRC_ESPC-D-V02_s3z_best.ncd'
# url_uvel = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_u3z/FMRC_ESPC-D-V02_u3z_best.ncd'
# url_vvel = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_v3z/FMRC_ESPC-D-V02_v3z_best.ncd'
# url_ssh  = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ssh/FMRC_ESPC-D-V02_ssh_best.ncd'
# url_hycom = [url_ssh, url_uvel, url_vvel, url_temp, url_salt]
# variables = ["surf_el", "water_u", "water_v", "water_temp", "salinity"]

# new combined versions
url_temp_salt = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ts3z/FMRC_ESPC-D-V02_ts3z_best.ncd'
url_uvel_vvel = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_uv3z/FMRC_ESPC-D-V02_uv3z_best.ncd'
url_ssh  = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ssh/FMRC_ESPC-D-V02_ssh_best.ncd'
url_hycom = [url_ssh, url_uvel_vvel, url_temp_salt]
variables = ["surf_el", "water_u,water_v", "water_temp,salinity"]

out_dir = Ldir['parent'] / 'LPM_output' / 'hycom_test'
Lfun.make_dir(out_dir)

date = '2024.09.13'

# specify the sub region of hycom to extract
aa = [-131, -121, 39, 53]
# specify spatial limits
north = aa[3]
south = aa[2]
west = aa[0] + 360
east = aa[1] + 360

'''
get HYCOM file for given date in format "YYYY.mm.DD" (2024.09.10) for example
path (i.e. /tmp) is the local path to the file where you want the output
'''
start = datetime.strptime(date,Lfun.ds_fmt)

out_fn = out_dir / ('hycom_%s.nc' % (date))

for i, var in enumerate(variables):
    tt0 = time()
    print('')
    url = url_hycom[i]
    print(i, var, url)
    print('Working step %d for %s using %s' %(i, var, url))
    try:    
        # hycom = Dataset(url)
        ds = xr.open_dataset(url, use_cftime=True, decode_times=False)
    except:    
        print('hycom for %s does not exist' % (url))
        # return
        continue
    # hycom_time = num2date(ds.variables["time"][:], ds.variables["time"].units)
    hycom_time = cftime.num2date(ds.time.values, ds.time.units)
    time_list = np.where(hycom_time == start)[0]
    ds.close()
    # hycom.close()
                    
    if not np.any(time_list):
        print("Cannot find valid times")
        print(hycom_time)
        break

    # extract data from HYCOM file
    if i == 0:
        cmd='ncks -O -v {:s} -d time,{:d},{:d} -d lat,{:d}.,{:d}.,1 -d lon,{:d}.,{:d}.,1 {:s} {:s}'.format(
                var, time_list[0], time_list[0], south, north, west, east, url, str(out_fn))
    else:
        cmd='ncks -A -v {:s} -d time,{:d},{:d} -d lat,{:d}.,{:d}.,1 -d lon,{:d}.,{:d}.,1  {:s} {:s}'.format(
                var, time_list[0], time_list[0], south, north, west, east, url, str(out_fn))

    print(cmd)
    os.system(cmd)
    print('Took %0.1f sec to get %s' % (time()-tt0, var))

# check on the results
ds = xr.open_dataset(out_fn)
print(ds)
