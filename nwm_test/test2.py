"""
Using the nwm package.

https://nwm.readthedocs.io/en/latest/

"""

# import matplotlib.pyplot as plt
# from nwm import NwmHs
#
# # get data from National water model HydroShare App
# nwm_data = NwmHs()
# dataset = nwm_data.get_data(archive='rolling', config='medium_range', geom='channel_rt',
# variable='streamflow', comid=[5781915], init_time=6, start_date='2021-11-01')
# # dataset = nwm_data.get_data(archive='rolling', config='medium_range', geom='channel_rt',
# # variable='streamflow', comid=[23989319], init_time=0, start_date='2021-11-01')
#
# # show metadata - this is an xarray Dataset, yay!
# #dataset.attrs
#
# # plot data
# plt.figure(figsize=(9,5))
# dataset.plot()
# plt.xlabel('Date')
# plt.ylabel('{} ({})'.format(dataset.variable_name,dataset.variable_unit))
# plt.title('Short range streamflow forecast for Channel 5781915 during Harvey Hurricane Event')

url_str = ('https://hs-apps.hydroshare.org/apps/nwm-forecasts/api/GetWaterML/'
        +'?config=medium_range&geom=channel_rt&variable=streamflow&COMID=11359107'
        + '&startDate=2021-11-23&time=06')

import requests
import bs4

response = requests.get(url_str, headers={'Authorization': 'Token 2a76a98258485df3098dd9f41b4ba13cc7b1ca07'},)
soup = bs4.BeautifulSoup(response.content, 'lxml')

"""
RESULT: gives an error:
<h2>Internal Server Error</h2>
<p>We're sorry, but we seem to have a problem. Please, come back later and try again.</p>
"""