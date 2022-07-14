"""
Code to test the PyCO2SYS module.

Info on useage and units is available here:
https://pyco2sys.readthedocs.io/en/latest/co2sys_nd/

This test is to make a plot like Fig. 4.2 in Emerson and Hedges.
"""

import PyCO2SYS as pyco2
import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

salt = 35
temp = 20 # deg C
pres = 0 # dbar

# calculate over a range of pH
N = 100
DIC = 2000*np.ones(N) # umol kg-1
pH = np.linspace(0,12,N)
r = pyco2.sys(par1=pH, par2=DIC, par1_type=3, par2_type=2,
    salinity=salt, temperature=temp, pressure=pres,
    total_silicate=50, total_phosphate=2,
    opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)
    
# and for a specific alkalinity
Alk = 2300 # Total Alkalinity [umol kg-1]
R = pyco2.sys(par1=Alk, par2=DIC[0], par1_type=1, par2_type=2,
    salinity=salt, temperature=temp, pressure=pres,
    total_silicate=50, total_phosphate=2,
    opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)
    
    
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111)
ax.semilogy(pH,r['CO2'],'-b',label='CO2aq')
ax.semilogy(pH,r['HCO3'],'-g',label='HCO3')
ax.semilogy(pH,r['CO3'],'-r',label='CO3')
ax.set_xlim(0,12)
ax.set_ylim(1e-1, 1e4)
ax.set_xlabel('pH')
ax.set_ylabel('[C] (umol kg-1)')
ax.legend(ncol=3)
ax.set_title('s=%0.1f, T=%0.1f (degC), p=%0.1f (dbar), DIC=%0.1f (umol kg-1)' %
    (salt, temp, pres, DIC[0]))

# add info for specific alkalinity
ax.axvline(R['pH'],linestyle='--', color='c')
ax.text(.95, .95, 'Alkalinity=\n%0.1f (ueq kg-1)' % (Alk), c='c',
    transform=ax.transAxes, ha='right')

plt.show()
pfun.end_plot()

