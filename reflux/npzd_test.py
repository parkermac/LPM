"""
Code to test the npzd_equations module. For a single box.
"""

from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import npzd_equations as npzde
from importlib import reload
reload(npzde)


# initialize fields
# intial conditions, all [mmol N m-3]
v = dict()
v['Phy'] = 0.01
v['Zoo'] = 0.001
v['SDet'] = 0
v['LDet'] = 0
v['NO3'] = 20
v['NH4'] = 0
v_list = list(v.keys())

E = 100 # [W m-2]

dt_days = 0.16
nt = 300

df = pd.DataFrame(columns = v_list)

for ii in range(nt):
    if np.mod(ii,10) == 0:
        df.loc[ii*dt_days,v_list] = v
    v = npzde.update_v(v, E, dt_days)