"""
Plot the vertical structure of Ri for the classical (cubic-quintic) u and s' profiles.
"""

import numpy as np
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun

zee = np.linspace(-1,0,100) # zeta at cell edges
ze = zee[:-1] + np.diff(zee)/2 # zeta at cell centers

# the polynomials that go into the u and s' profiles
# and their derivatives (e.g. P1p for P1) vs. zeta
P1 = 3/2 - (3/2)*ze**2
P1p = -3*ze

P2 = 1 - 9*ze**2 - 8*ze**3
P2p = -18*ze - 24*ze**2

P3 = -7/120 + (1/4)*ze**2 - (1/8)*ze**4
P3p = (1/2)*ze -(1/2)*ze**3

P4 = -1/12 + (1/2)*ze**2 - (3/4)*ze**4 - (2/5)*ze**5
P4p = ze - 3*ze**3 - 2*ze**4

plt.close('all')
pfun.start_plot(figsize=(10,10))
fig = plt.figure()

# Create profiles of u and, s' (from b = g*beta*s'), vs. zeta.
# Note these have been checked for consistency with integral
# expectations (all are very close):
# sp.mean() = 0
# u.mean() = ubar
# u[-1] = ubar + ue
#
# parameters
ue = 0.1    # Ue [m s-1]
ubar = 0.01 # Ubar [m s-1]
H = 20      # depth [m]
km_ks = 2   # Km / Ks [dimensionless]
g = 9.8     # gravity [m s-2]
beta = 7.7e-4 # haline contraction [psu-1]
#
# profiles
u = ubar*P1 + ue*P2
b = ue * km_ks * (48/H) * (ubar*P3 + ue*P4)
sp = b / (g * beta)
#
# plotting
ax = fig.add_subplot(223)
ax.plot(u,ze,'-b')
ax.grid(True)
ax.set_xlabel('u [m s-1]')
ax.set_ylabel('zeta')
ax.axvline()
ax.set_ylim(-1,0)
#
ax = fig.add_subplot(224)
ax.plot(sp,ze,'-b')
ax.grid(True)
ax.set_xlabel('sprime [g kg-1]')
ax.axvline()
ax.set_ylim(-1,0)

# Ri vs. zeta for a range of ubar/ue
ax = fig.add_subplot(211)
for ub_ue in [0, 1/10, 1/2, 1, 2]:
    top = ub_ue*P3p + P4p
    bot = (ub_ue**2)*(P1p**2) + 2*ub_ue*P1p*P2p + P2p**2
    Ri = -48 * km_ks * top / bot
    ax.plot(Ri, ze, label=str(ub_ue))
ax.grid(True)
ax.set_xlim(0,5)
ax.legend()
ax.set_ylabel('zeta')
ax.set_xlabel('Ri')
ax.set_title('Ri vs. zeta for a range of Ubar/Ue')
ax.set_ylim(-1,0)

plt.show()