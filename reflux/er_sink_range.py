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

# Run the model for a range of W_sink values [m d-1]
C_bot_dict = dict()
C_top_dict = dict()
# W_list = list(np.linspace(0,100,11))
W_list = [0,7.2,8.02,9.06,10.4,12.21,14.78,18.72,21.6,25.53,40.11,93.6]
for W in W_list:
    Q_sink = W * DA / 86400 # convert W from [m d-1] to [m s-1]
    if False:
        # River source
        C_river = np.ones(1)
        C_ocean = np.zeros(1)
    else:
        # Ocean source
        C_river = np.zeros(1)
        C_ocean = np.ones(1)
    C_top = np.zeros(N_boxes)
    C_bot = np.zeros(N_boxes)
    for ii in range (nt):
        C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)
    C_bot_dict[W] = C_bot
    C_top_dict[W] = C_top
    
    print('W=%0.2f, W*dt/H_top=%0.2f, C_bot[1]=%0.2f' %
        (W,(W*dt/86400)/H_top, C_bot[1]))
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
    ax1.set_ylim(0,20)
    ax1.grid(True)
    ax1.legend(loc='upper center', ncols=2)

    ax2.set_xlim(0, X[-1])
    ax2.set_ylim(0,20)
    ax2.grid(True)

    ax2.set_xlabel('X [km]')
    ax1.set_title('Range of Sinking Speeds [ m d-1]')
    
    ax1.text(.95,.9,'Top Layer', transform = ax1.transAxes, ha='right')
    ax2.text(.95,.9,'Bottom Layer', transform = ax2.transAxes, ha='right')

pfun.end_plot()
plt.show()

