"""
Code to test the hydrotools module.
"""

# Import the nwm Client
from hydrotools.nwm_client import http as nwm
import pandas as pd

# Path to server (NOMADS in this case)
server = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/"

# Instantiate model data service
model_data_service = nwm.NWMDataService(server)

# Set reference time
yesterday = pd.Timestamp.utcnow() - pd.Timedelta("1D")
reference_time = yesterday.strftime("%Y%m%dT%-HZ")

# Retrieve forecast data
#  By default, only retrieves data at USGS gaging sites in
#  CONUS that are used for model assimilation
forecast_data = model_data_service.get(
    configuration = "short_range",
    reference_time = reference_time
    )

# Look at the data
print(forecast_data.info(memory_usage='deep'))
print(forecast_data[['value_time', 'value']].head())