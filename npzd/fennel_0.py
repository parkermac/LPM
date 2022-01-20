"""
Code to explore the Fennel et al. (2006) NPZD model equations.
"""

import matplotlib.pyplot as plt
import numpy as np
from lo_tools import plotting_functions as pfun

import fennel_functions as ff


plt.close('all')
pfun.start_plot(fs=10, figsize=(18,10))

fig, axes = plt.subplots(nrows=2, ncols=2)

# example calculations to look at functional dependence

# mu_max(T)
T = np.linspace(0,25,100)
mu_max = ff.get_mu_max(T)
#
ax = axes[0,0]
ax.plot(T, mu_max, '-b', lw=3)
ax.set_xlabel('Temperature [degC]')
ax.set_ylabel('mu_max [d-1]')
ax.text(.05,.9,'Max Phytoplankton Growth Rate vs. T',transform=ax.transAxes)
ax.grid(True)
ax.set_ylim(bottom=0)

# I(z) with and without Chl
I_0 = 500
z_w = np.linspace(-100,0,101)
z_rho = z_w[:-1] + np.diff(z_w)/2
Chl = np.linspace(0,2,len(z_rho))
I = ff.get_I(I_0, z_rho, z_w, Chl)
Iclean = ff.get_I(I_0, z_rho, z_w, 0*Chl)
#
ax = axes[0,1]
ax.plot(I, z_rho, '-', c='g', lw=3, label='With Chl')
ax.plot(Iclean, z_rho, '-', c='dodgerblue', lw=3, label='No Chl')
ax.legend()
ax.set_xlabel('I [W m-2]')
ax.set_ylabel('Z [m]')
ax.text(.05,.9,'Light vs. Z',transform=ax.transAxes)
ax.grid(True)

# f(I)
I = np.linspace(0,100,100)
T = 10 * np.ones(len(I))
f = ff.get_f(I, ff.get_mu_max(T))
#
ax = axes[1,0]
ax.plot(I, f, '-', c='purple', lw=3)
ax.set_xlabel('I [W m-2]')
ax.set_ylabel('f(I)')
ax.text(.05,.9,'P-I Curve',transform=ax.transAxes)
ax.grid(True)

# L(NO3, NH4)
NO3 = np.linspace(0,30,100)
NH4 = 0 * NO3
L = ff.get_L(NO3, NH4)
NH4 = 0.1 * NO3
LL = ff.get_L(NO3, NH4)
#
ax = axes[1,1]
ax.plot(NO3, L, '-', c='brown', lw=3, label='NH4=0')
ax.plot(NO3, LL, '-', c='gold', lw=3, label='NH4=0.1*NO3')
ax.legend()
ax.set_xlabel('NO3 [mmol N m-3]')
ax.set_ylabel('L')
ax.text(.05,.9,'M-M Curve',transform=ax.transAxes)
ax.grid(True)

plt.show()
pfun.end_plot()
