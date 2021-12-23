"""
Code to explore tidal exchange flow and stratification in a 1-D model
with Richardson number control.
"""

import numpy as np
import matplotlib.pyplot as plt

from lo_tools import plotting_functions as pfun

# parameters
g = 9.8
rho0 = 1025
H = 20
drho = -1 # initial top minus bottom density difference
du0 = .1  # steady shear, top minus bottom velocity difference
du1 = 1   #  tidal shear, top minus bottom velocity difference
om = 2*np.pi / (12 * 3600) # tidal frequency
G = g * 25 / (50e3 * rho0) # d(g*rho/rho0)/dx

ndays = 3
dt = 60
t = np.arange(0, 86400*ndays + dt, dt)
tdays = t/86400

dudz = du0/H + (du1/H)*np.cos(om*t)

dbdz0 = -g*drho/(rho0*H)

# analytical
dbdz = dbdz0 + G*( t*du0/H + (du1/H)*np.sin(om*t)/om )
ri = dbdz / (1e-6 + dudz**2)

# integration
Dbdz = np.zeros(t.shape)
Dbdz[0] = dbdz0
Ri = np.zeros(t.shape)
Ri_crit = .25
for ii in range(1,len(t)):
    Dbdz[ii] = Dbdz[ii-1] + dt*G*dudz[ii]
    this_ri = Dbdz[ii] / (1e-6 + dudz[ii]**2)
    if (this_ri < Ri_crit):
        Dbdz[ii] = Ri_crit * (1e-6 + dudz[ii]**2)
        this_ri = Dbdz[ii] / (1e-6 + dudz[ii]**2)
    Ri[ii] = this_ri
#Ri = Dbdz / (1e-6 + dudz**2)

# plotting
plt.close('all')
pfun.start_plot()

fig = plt.figure(figsize=(14,10))

ax = fig.add_subplot(311)
ax.plot(tdays, dudz)
ax.grid(True)
ax.set_ylabel('du/dz')

ax = fig.add_subplot(312)
ax.plot(tdays, dbdz,'-b')
ax.plot(tdays, Dbdz,'--g')
ax.grid(True)
ax.set_ylabel('db/dz')

ax = fig.add_subplot(313)
ax.plot(tdays, ri,'-b')
ax.plot(tdays, Ri,'--g')
ax.set_ylim(0,3)
ax.grid(True)
ax.set_ylabel('Ri')
ax.set_xlabel('Days')

plt.show()
pfun.end_plot()
