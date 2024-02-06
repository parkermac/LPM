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

# Estuary physical parameters
Qr = 1000    # River Transport [m3 s-1]
B = 3e3     # width [m]
H_top = 20  # thickness of top layer [m]
H_bot = 20  # thickness of bottom layer [m]

# Create the solution at box edges
Sbar_0 = 30
DS_0 = 5
N_boxes = 100
L = 50e3
Sin, Sout, x, L = er_fun.get_Sio_chatwin(Sbar_0, DS_0, N_boxes, L)
DS = Sin - Sout

# Make x-axes for plotting
dx = np.diff(x) # along-channel length of each box [m]
DA = B * dx     # horizontal area of each box [m2]
X = x/1e3       # box edges [km]
xb = x[:-1] + dx/2
XB = xb/1e3     # box centers[km]

# Box volumes [m3]
V_top = B * H_top * dx
V_bot = B * H_bot * dx
V = np.sum(V_top + V_bot)

# Calculate transports using steady Knudsen balance
# (sign convention used here is that all transports are positive)
Qout = Qr*Sin/DS
Qin = Qr*Sout/DS

# Efflux-Reflux parameters
alpha_efflux, alpha_reflux, Q_efflux, Q_reflux = er_fun.alpha_calc(Qin, Qout, Sin, Sout)

# Calculate the continuous function vertical transports.
Q_efflux_alt = np.diff(Sout) * Qout[1:] / DS[1:]
Q_reflux_alt = np.diff(Sin) * Qin[:-1] / DS[:-1]
W_efflux_alt = Q_efflux_alt / DA
W_reflux_alt = Q_reflux_alt / DA
# and form an average for scaling of sinking
W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2
Q_sink = W_er * DA

# Estimate max dt for stability
dt = 0.9 * np.min((np.min(V_top/Qout[1:]), np.min(V_bot/Qin[1:])))
# Run for a specified number of flushing times
T_flush = V / Qout[-1]
nt = 10 * int(T_flush / dt)

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

