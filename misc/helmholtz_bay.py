"""
Code to plot aspects of the solution to the Helmholtz Bay problem.
"""

import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

r_om0 = .1 # R/omega0

omax = 3
om_om0 = np.linspace(0,omax,500)# omega/omega0

phi = np.arctan2(r_om0*om_om0, 1 - om_om0**2) # phase lag [radians]
# phi = np.arctan(r_om0*om_om0/(1 - om_om0**2)) # phase lag [radians]

a_a0 = 1 / np.sqrt((1-om_om0**2)**2 + (r_om0*om_om0**2))

pfun.start_plot()
plt.close('all')
fig = plt.figure(figsize=(10,7))

ax = fig.add_subplot(211)
ax.plot(om_om0, phi*180/np.pi)
ax.grid(True)
ax.set_ylim(0,180)
ax.set_ylabel(r'$\phi$ [deg]')
ax.set_xlim(0,omax)
ax.set_title(r'Helmholtz Bay: $R/\omega_{0}=%0.1f$' % (r_om0))

ax = fig.add_subplot(212)
ax.plot(om_om0, a_a0)
ax.set_xlabel(r'$\omega/\omega_{0}$')
ax.set_ylim(0,4)
ax.grid(True)
ax.set_xlim(0,omax)
