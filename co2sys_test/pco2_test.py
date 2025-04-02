"""
Code to explore the relationship between pCO2, TIC, and Alkalinity.

The goal is to get a sense of how much a difference between TIC and Alkalinity
translates to a change in pCO2. The motivation is that we are seeing much higher
pCO2 in the model compared ot observations, especially in the deep water.

"""
import numpy as np
import matplotlib.pyplot as plt
from PyCO2SYS import CO2SYS
import gsw
from lo_tools import plotting_functions as pfun

# using gsw to create in-situ density
SA = 32 # absolute salinty [g kg-1]
CT = 10 # conservative temperature [deg C]
pres = 0 # pressure [dbar]
rho = gsw.rho(SA, CT, pres) # in situ density [kg m-3]

# convert from umol/L to umol/kg using in situ dentity
alkalinity_um = np.linspace(2200,2500,20)
TIC_um = 2200
alkalinity = 1000 * alkalinity_um/ rho
TIC = 1000 * TIC_um / rho
# Assume wa can use SA and CT instead of salt and temp
CO2dict = CO2SYS(alkalinity, TIC, 1, 2, SA, CT, CT,
    pres, pres, 50, 2, 1, 10, 1, NH3=0.0, H2S=0.0)
PH = CO2dict['pHout']
ARAG = CO2dict['OmegaARout']
pCO2 = CO2dict['pCO2out']

plt.close('all')
pfun.start_plot(figsize=(8,8))
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(alkalinity_um,pCO2,'-b')
ax.set_xlabel('Alkalinty (uM)')
ax.set_ylabel('pCO2 (units?)')
ax.grid(True)


plt.show()