# Code based on that from Ivica Janeković, ivica.jan@gmail.com

import os
import numpy as np
from netCDF4 import Dataset, num2date
from datetime import datetime, timedelta

# separate for each variable
url_temp = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_t3z/FMRC_ESPC-D-V02_t3z_best.ncd'
url_salt = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_s3z/FMRC_ESPC-D-V02_s3z_best.ncd'
url_uvel = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_u3z/FMRC_ESPC-D-V02_u3z_best.ncd'
url_vvel = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_v3z/FMRC_ESPC-D-V02_v3z_best.ncd'
url_ssh  = 'https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ssh/FMRC_ESPC-D-V02_ssh_best.ncd'
url_hycom = [url_ssh, url_uvel, url_vvel, url_temp, url_salt]
variables = ["surf_el", "water_u", "water_v", "water_temp", "salinity"]

from lo_tools import Lfun
Ldir = Lfun.Lstart()
out_dir = Ldir['parent'] / 'LPM_output' / 'hycom_test'
Lfun.make_dir(out_dir)

date = '20240913'

# specify the sub region of hycom to extract
aa = [-131, -121, 39, 53]
# specify spatial limits
north = aa[3]
south = aa[2]
west = aa[0] + 360
east = aa[1] + 360

# def get_hycom_file(date, out_dir):

'''
get HYCOM file for given date in format "YYYYmmDD" (20240910) for example
path (i.e. /tmp) is the local path to the file where you want the output
'''
start = datetime.strptime(date,'%Y%m%d')
out_fn = out_dir / ('hycom_%s.nc' %date)
lat_list = [1130, 1448] # for my domain 
lon_list = [1351, 1459]
for i, var in enumerate(variables):
    print('')
    url = url_hycom[i]
    print(i, var, url)
    print('Working step %d for %s using %s' %(i, var, url))
    try:    
        hycom = Dataset(url)
    except:    
        print('hycom for %s does not exist' %url)
        # return
        continue
    hycom_time = num2date(hycom.variables["time"][:],
                        hycom.variables["time"].units)
    time_list = np.where(hycom_time == start)[0]
    hycom.close()
                    
    if not np.any(time_list):
        print("Cannot find valid times")
        # return
        continue

    # extract data from HYCOM file
    if i == 0:
        cmd='ncks -O -v {:s} -d time,{:d},{:d} -d lat,{:d}.,{:d}.,1 -d lon,{:d}.,{:d}.,1 {:s} {:s}'.format(
                var, time_list[0], time_list[0], south, north, west, east, url, str(out_fn))
        # cmd='ncks -O -v {:s} -d time,{:d},{:d} -d lat,{:d},{:d} -d lon,{:d},{:d} {:s} {:s}'.format(
        #         var, time_list[0], time_list[0], lat_list[0], lat_list[-1], lon_list[0], lon_list[-1], url, str(out_fn))
    else:
        cmd='ncks -A -v {:s} -d time,{:d},{:d} -d lat,{:d},{:d} -d lon,{:d},{:d} {:s} {:s}'.format(
                var, time_list[0], time_list[0], lat_list[0], lat_list[-1], lon_list[0], lon_list[-1], url, str(out_fn))

    print(cmd)

    if i == 0:
        os.system(cmd)

# run the function
# get_hycom_file(date, out_dir)