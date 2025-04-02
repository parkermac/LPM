#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is code to test getting glorys model output. It is based on code from Felipe Soares,
and then modified by me.

Created on Wed Dec  6 10:39:40 2023
@author: fsoares
"""
import copernicusmarine
from datetime import datetime, timedelta

# Define the date range
start_date = datetime(2019, 2, 26)
end_date = datetime(2019, 2, 26)  # Adjust the end date as needed

# Loop through the date range
current_date = start_date
while current_date <= end_date:
    # Convert the current date to string format
    current_date_str = current_date.strftime("%Y-%m-%dT%H:%M:%S")

    # Use copernicusmarine.subset for the current date
    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
        variables=["uo", "vo", "so", "thetao", "zos"],
        minimum_longitude=-131,
        maximum_longitude=-121,
        minimum_latitude=41,
        maximum_latitude=53,
        start_datetime=current_date_str,
        end_datetime=current_date_str,
        minimum_depth=0.494,
        maximum_depth=5727.917,
        output_filename=f"GLORYS_Reanalysis_LO_{current_date_str}.nc",
        output_directory="",
        username = "fsoares1",
        password = "Fuconn.2021",
        force_download=True
    )

    # Move to the next date
    current_date += timedelta(days=1)