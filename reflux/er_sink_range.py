"""
Code to explore tracer distributions calculated using a box model
based on efflux-reflux theory.

This runs the model to steady state over a range of sinking speeds.
It is meant to reproduce Fig. 3.4 from Lily engle's thesis.

RESULT: this appears to perfectly reproduce her results. Along
the way it revealed that my treatment of the landward boundary
condition in the lower layer causes non-conservation of sinking
tracers. Not clear what to do about this.
"""

import numpy as np
import matplotlib.pyplot as plt

from lo_tools import plotting_functions as pfun
import er_fun
from importlib import reload
reload(er_fun)


# Estuary physical parameters: Lily's base case
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
nt = 100 * int(T_flush / dt)

# Run the model for a range of W_sink values
C_bot_dict = dict()
C_top_dict = dict()
# W_list = list(np.linspace(0,100,11))
W_list = [0,7.2,8.02,9.06,10.4,12.21,14.78,18.72,21.6,25.53,40.11,93.6]
for W in W_list:
    Q_sink = W * DA / 86400 # convert W from [m d-1] to [m s-1]
    # River source
    C_river = np.ones(1)
    C_ocean = np.zeros(1)
    C_top = np.zeros(N_boxes)
    C_bot = np.zeros(N_boxes)
    for ii in range (nt):
        C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)
    C_bot_dict[W] = C_bot
    C_top_dict[W] = C_top
    
    print('W=%0.2f, W*dt/H_top=%0.2f, C_bot[0]=%0.2f' %
        (W,(W*dt/86400)/H_top, C_bot[0]))
    # check tracer conservation
    in1 = Qr*C_river[0]
    out1 = Qout[-1]*C_top[-1]
    print(' in1=%0.5f, out1=%0.5f, diff=%0.5f' % (in1,out1, in1-out1))


# Plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

for W in W_list:
    C_bot = C_bot_dict[W]
    C_top = C_top_dict[W]

    if W == 21.6:
        ls = '--'
    else:
        ls = '-'
    ax2.plot(XB[1:], C_bot[1:], ls=ls, label=W)
    ax1.plot(XB, C_top, ls=ls, label=W)

    ax1.set_xlim(0, X[-1])
    ax1.set_ylim(0,6)
    ax1.grid(True)
    ax1.legend(loc='upper center', ncols=2)

    ax2.set_xlim(0, X[-1])
    ax2.set_ylim(0,11)
    ax2.grid(True)

    ax2.set_xlabel('X [km]')
    ax1.set_title('Range of Sinking Speeds [ m d-1]')
    
    ax1.text(.95,.9,'Top Layer', transform = ax1.transAxes, ha='right')
    ax2.text(.95,.9,'Bottom Layer', transform = ax2.transAxes, ha='right')

pfun.end_plot()
plt.show()

