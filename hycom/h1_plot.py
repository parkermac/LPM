"""
Code to explore the extracted hycom fields.  The specific goal is
to see if there are obvous artifacts of data assimilation that might
contaminate bottom pressure analysis that I am doing for the MG&G folks.

Plot the results of h1.py/
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun

Ldir = Lfun.Lstart()

in_dir = Ldir['parent'] / 'LPM_output' / 'hycom'

df = pd.read_pickle(in_dir / 'h1.p')

plt.close('all')
pfun.start_plot()
fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
for h in df.hexp.unique():
    dfh = df[df.hexp==h]
    dfh.salt.plot(fig=fig, ax=ax1)
    dfh.temp.plot(fig=fig, ax=ax2)
    
ax1.set_title('HYCOM Fields at 2000 m (46 N, 126 W)')
ax1.grid(True)
ax2.grid(True)
ax1.set_xticklabels([])
ax1.set_xlim(df.index[0], df.index[-1])
ax2.set_xlim(df.index[0], df.index[-1])
ax1.text(.05, .85, '(a) Salinity [psu]', weight='bold', transform=ax1.transAxes)
ax2.text(.05, .85, '(b) In-situ Temperature [deg C]', weight='bold', transform=ax2.transAxes)
ax2.set_xlabel('Date')
plt.show()