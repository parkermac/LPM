"""
Code to explore tracer distributions calculated using a box model
based on efflux-reflux theory.

This includes the effects of sinking, decay, and ocean vs. river source.
"""

import numpy as np
import matplotlib.pyplot as plt

from lo_tools import plotting_functions as pfun
import er_fun
from importlib import reload
reload(er_fun)

# create the physical solution
phys_tup, sol_tup, er1_tup, er2_tup, er3_tup, t_tup = er_fun.get_params(etype='chatwin')
# unpacking
Qr, B, H_top, H_bot, Sbar_0, DS_0, N_boxes, L, etype = phys_tup
Sin, Sout, Qin, Qout, x, DS, dx, DA, X, xb, XB, V_top, V_bot, V = sol_tup
alpha_efflux, alpha_reflux = er1_tup
Q_efflux, Q_reflux, W_efflux, W_reflux, Net_efflux, Net_reflux = er2_tup
Q_efflux_alt, Q_reflux_alt, W_efflux_alt, W_reflux_alt, Net_efflux_alt, Net_reflux_alt = er3_tup
dt, T_flush = t_tup

# Run for a specified number of flushing times
nt = 10 * int(T_flush / dt)

# Form an average for scaling of sinking
W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2
Q_sink = W_er * DA

# Plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(12,8))

ax = fig.add_subplot(311)
# Ocean source
C_river = np.zeros(1)
C_ocean = np.ones(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout)
ax.plot(XB, C_bot, '-r', label='$C_{bot}$ ocean source')
ax.plot(XB, C_top, '-b', label='$C_{top}$ ocean source')
# River source
C_river = np.ones(1)
C_ocean = np.zeros(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout)
ax.plot(XB, C_bot, '--r', label='$C_{bot}$ river source')
ax.plot(XB, C_top, '--b', label='$C_{top}$ river source')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='center left')

ax = fig.add_subplot(312)
# Ocean source
C_river = np.zeros(1)
C_ocean = np.ones(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)
ax.plot(XB, C_bot, '-r', label='$C_{bot}$ ocean source')
ax.plot(XB, C_top, '-b', label='$C_{top}$ ocean source')
# River source
C_river = np.ones(1)
C_ocean = np.zeros(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)
ax.plot(XB, C_bot, '--r', label='$C_{bot}$ river source')
ax.plot(XB, C_top, '--b', label='$C_{top}$ river source')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
#ax.legend(loc='center right')
ax.text(.05, .9, 'Sinking', transform=ax.transAxes)

ax = fig.add_subplot(313)
# Ocean source
C_river = np.zeros(1)
C_ocean = np.ones(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, T_decay=T_flush)
ax.plot(XB, C_bot, '-r', label='$C_{bot}$ ocean source')
ax.plot(XB, C_top, '-b', label='$C_{top}$ ocean source')
# River source
C_river = np.ones(1)
C_ocean = np.zeros(1)
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
for ii in range (nt):
    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, T_decay=T_flush)
ax.plot(XB, C_bot, '--r', label='$C_{bot}$ river source')
ax.plot(XB, C_top, '--b', label='$C_{top}$ river source')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
#ax.legend(loc='center right')
ax.text(.05, .9, 'Decay', transform=ax.transAxes)

ax.set_xlabel('X [km]')


pfun.end_plot()
plt.show()

