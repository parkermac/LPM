"""
Code to test a box model based on efflux-reflux theory.

The primary test is whether or not the model, when run to
steady state, can reproduce the Sin and Sout fields that
were used to create the transport fields.

Result: The _alt versions match Q_efflux.sum() and Q_reflux.sum() quite well for N_boxes = 10000.

Interestingly, the _alt versions are extremely insensitive to N_boxes, varying by about 1% over the range N_boxes = 10 to 10000.

In contrast the estimates from Q_efflux.sum() and Q_reflux.sum() require
N_boxes >= 1000 to be similar. I believe the reason is that in the finite-box
version the incoming transport is larger than would be appropriate for the
box, so it is decreased by the dS term in the demoninator to make it give the
right value for a finite box.

Summary:
For the box integrator, use the standard alphas, but for estimates of the
net efflux and reflux use the continuous function (i.e. alt) version.
"""

import numpy as np
import matplotlib.pyplot as plt

from lo_tools import plotting_functions as pfun
import er_fun
from importlib import reload
reload(er_fun)

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# create the physical solution
phys_tup, sol_tup, er1_tup, er2_tup, er3_tup, t_tup = er_fun.get_params(etype='chatwin')
# unpacking
Qr, B, H_top, H_bot, Sbar_0, DS_0, N_boxes, L, etype = phys_tup
Sin, Sout, Qin, Qout, x, DS, dx, DA, X, xb, XB, V_top, V_bot, V = sol_tup
alpha_efflux, alpha_reflux = er1_tup
Q_efflux, Q_reflux, W_efflux, W_reflux, Net_efflux, Net_reflux = er2_tup
Q_efflux_alt, Q_reflux_alt, W_efflux_alt, W_reflux_alt, Net_efflux_alt, Net_reflux_alt = er3_tup
dt, T_flush = t_tup

# Box model integrator
# Initial condition
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
# Boundary conditions
# This mimics salinity
C_river = np.zeros(1)
C_ocean = Sin[-1]*np.ones(1)
# Run for a specified number of flushing times
nt = 10 * int(T_flush / dt)
# Integrate over time
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean,
        alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout)

# Plotting
plt.close('all')
pfun.start_plot(fs=20)
fig = plt.figure(figsize=(12,8))

ax = fig.add_subplot(311)
ax.plot(X, Sin, '-r', label='Sin')
ax.plot(X, Sout, '-b', label='Sout')
ax.plot(X, DS, '-', color='orange', label=r'$\Delta S$')
ax.plot(XB, C_bot, '--r', label='C_bot')
ax.plot(XB, C_top, '--b', label='C_top')
ax.plot(XB, C_bot - C_top, '--', color='orange', label=r'$\Delta C$')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='upper left', ncols=2)
ax.set_title('Efflux-Reflux in the %s Solution' % (etype.upper()))

ax = fig.add_subplot(312)
ax.plot(X, Qin/Qr, '-r', label='Qin/Qr')
ax.plot(X, Qout/Qr, '-b', label='Qout/Qr')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='upper left')

ax = fig.add_subplot(313)
sec_per_day = 86400
if False:
    ax.plot(XB, W_efflux_alt * sec_per_day, '-r', label='W_efflux_alt [m/day]')
    ax.plot(XB, W_reflux_alt * sec_per_day, '-b', label='W_reflux_alt [m/day]')
    ax.plot(XB, W_efflux * sec_per_day, '--r', label='W_efflux [m/day]')
    ax.plot(XB, W_reflux * sec_per_day, '--b', label='W_reflux [m/day]')
else:
    # Give preference to the "alt" versions as being correct
    ax.plot(XB, W_efflux_alt * sec_per_day, '-r', label='W_efflux [m/day]')
    ax.plot(XB, W_reflux_alt * sec_per_day, '-b', label='W_reflux [m/day]')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='lower right')
ax.set_xlabel('X [km]')

# ax.text(.2, .5, 'Number of boxes = %d' % (N_boxes), transform=ax.transAxes)
ax.text(.2, .45, 'Net Efflux / Qin_mouth = %0.1f' %
    (Net_efflux_alt / Qin[-1]), transform=ax.transAxes,bbox=pfun.bbox)
ax.text(.2, .25, 'Net Reflux / Qout_mouth = %0.1f' %
    (Net_reflux_alt / Qout[-1]), transform=ax.transAxes,bbox=pfun.bbox)

fig.tight_layout()
pfun.end_plot()
plt.show()

out_fn = Ldir['parent'] / 'LPM_output' / 'reflux'/ 'er_test.png'
Lfun.make_dir(out_fn.parent)
fig.savefig(out_fn)

