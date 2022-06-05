"""
Test of getting NWM data using a private url.

RESULT: this works!
"""

import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# These ALL work on 2021.12.01
#url = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts/medium_range_ensemble_member_1/streamflow?station_id=14197369'
#url = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts/medium_range_ensemble_member_1/streamflow?station_id=23989319'
#url = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts/medium_range_ensemble_member_1/streamflow?reference_time=2021120106&reach_id=23989319'
url = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts/medium_range_ensemble_member_1/streamflow?reference_time=2021120100&reach_id=23989319'
# BUT it did not work to look for 2021.11.30

# This version should work for any current day:
dt_now = datetime.now()
dt_str = dt_now.strftime('%Y%m%d')
url = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts/medium_range_ensemble_member_1/streamflow?reference_time='+dt_str+'00&reach_id=23989319'


resp = requests.get(url)

r_dict = resp.json()[0]

for k in r_dict.keys():
    if k != 'data':
        print('%s: %s' % (k, r_dict[k]))

data = r_dict['data'] # a list of dicts

q = [item['value'] for item in data]
t = [item['forecast-time'] for item in data]
# time format is '2021-12-04 19:00:00'
tt = [datetime.strptime(item, '%Y-%m-%d %H:%M:%S') for item in t]

s = pd.Series(q, index=tt)

plt.close('all')
s.plot()
plt.show()

