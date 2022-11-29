"""
Code to check on the amt pCO2 calculated using the PCO2AIR_SECULAR routine in fennel.h.

RESULT: this looks pretty good.  Clearly shows a linear trent with an annual cycle.
A bit low compared to actual values, but much better than what we were doing.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from lo_tools import plotting_functions as pfun

pi2 = 6.2831853071796

D0 = 282.6
D1 = 0.125
D2 =-7.18
D3 = 0.86
D4 =-0.99
D5 = 0.28
D6 =-0.80
D7 = 0.06

dti = pd.date_range(start='1951-01-01', end='2030-12-31', freq='D')

pmonth = dti.year - 1951.0 + dti.dayofyear/365.0

pCO2air_secular = D0 + D1*pmonth*12.0 + D2*np.sin(pi2*pmonth+D3) + D4*np.sin(pi2*pmonth+D5) + D6*np.sin(pi2*pmonth+D7)

s = pd.Series(index=dti, data=pCO2air_secular)

plt.close('all')
pfun.start_plot()
fig = plt.figure()
ax = fig.add_subplot(111)

s.plot(ax=ax)
ax.grid(True)
ax.set_xlabel('Year')
ax.set_ylabel('Atm pCO2')

plt.show()
