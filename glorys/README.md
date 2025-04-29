# README for glorys test code

### Where to start for glorys output

https://data.marine.copernicus.eu/products

forecast info

https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description

info about the specific things available for the forecast

https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/services

hindcast info:

https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description

and a form to get more info about the hindcast:

https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/download?dataset=cmems_mod_glo_phy_my_0.083deg_P1D-m_202311

50 vertical layers
regular 8 km (1/12 degree) grid
daily = daily average centered at midnight at start of that day

on 2025.04.21 it appeared:
the daily hindcast was available 1/1/1993 through 6/30/2021
and the daily forecast was available 6/1/2022 through 4/30/2025
so there is an 11-month gap. This is easily solved using the Interim product below:

Troubleshooting info from a very helpful AI thing:

To access interim datasets, you'll need to use the corresponding Interim product for the MultiYear dataset you're interested in. These interim datasets are typically updated monthly and bridge the gap between MultiYear and NearRealTime products.
For example, if you're looking for global physical data, you can access the interim dataset GLOBAL_MULTIYEAR_PHY_001_030, which covers the period from 01/07/2021 to about two months before the present.
Interim datasets are produced using the same modeling core and data assimilation module as the long reanalysis, but they assimilate Near Real Time (NRT) data instead of Reprocessed (REP) data.
For more detailed information on the differences between MultiYear, Interim, and NearRealTime products, please refer to this article: https://help.marine.copernicus.eu/en/articles/4872705-what-are-the-main-differences-between-nearrealtime-and-multiyear-

Looking through the GLOBAL_MULTIYEAR_PHY_001_030 products I found that there is also an "Interim" version,
so instead of using:
dataset_id='cmems_mod_glo_phy_my_0.083deg_P1D-m'
I would use:
dataset_id='cmems_mod_glo_phy_myint_0.083deg_P1D-m'
and this is currently available for 7/1/2021 through 03/25/2025

Automating the inspeciton of time limits, here is the screen output of cm_describe.py
run on 2025.04.21:

cmems_mod_glo_phy_my_0.083deg_P1D-m
INFO - 2025-04-21T20:40:36Z - Selected dataset version: "202311"
INFO - 2025-04-21T20:40:36Z - Selected dataset part: "default"
1993.01.01
2021.06.30

cmems_mod_glo_phy_myint_0.083deg_P1D-m
INFO - 2025-04-21T20:40:51Z - Selected dataset version: "202311"
INFO - 2025-04-21T20:40:51Z - Selected dataset part: "default"
2021.07.01
2025.03.25

cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m
INFO - 2025-04-21T20:41:05Z - Selected dataset version: "202406"
INFO - 2025-04-21T20:41:05Z - Selected dataset part: "default"
2022.06.01
2025.04.30