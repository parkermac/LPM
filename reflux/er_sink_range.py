"""
Code to explore tracer distributions calculated using a box model
based on efflux-reflux theory.

This runs the model over a range of sinking speeds.
It is meant to reproduce Fig. 3.4 from Lily engle's thesis.

RESULT: This appears to perfectly reproduce her results. Along
the way it revealed that my treatment of the landward boundary
condition in the lower layer causes non-conservation of sinking
tracers.

UPDATE: Since I have modified the box model to mask the deep landward cell
the tracer conservation is now correct even with sinking. This is now
a different model than what Lily was using so this code no longer
replicates her results. It will instead be a framework for other
explorations such as time to reach steady state, it ever, with
different sinking speeds.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

# Run for a specified number of flushing times
nt = 100 * int(T_flush / dt)

# Form an average for scaling of sinking
W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2
W_er_mpd = W_er * 86400

# initialize a dict to hold budget time series
budget_dict = dict()

# Run the model for a range of W_sink values [m d-1]
C_bot_dict = dict()
C_top_dict = dict()
W_list = list(np.array([0,.25,.5,1,2,4]) * W_er * 86400) # [m d-1]
W_list = [round(item,2) for item in W_list]

# W_list = [0,7.2,8.02,9.06,10.4,12.21,14.78,18.72,21.6,25.53,40.11,93.6] # Lily's list [m d-1]
for W in W_list:

    # initialize a DataFrame to hold budget time series
    df = pd.DataFrame(columns=['Cnet','Cmean','Fr','Fin','Fout','dCnet_dt','Error'])

    Q_sink = W * DA / 86400 # convert W from [m d-1] to [m s-1]
    if True:
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

        if np.mod(ii,10) == 0:
            tt = ii*dt/86400 # use time in days for the index
            df.loc[tt,'Cnet'] = np.nansum(C_top*V_top) + np.nansum(C_bot*V_bot)
            df.loc[tt,'Fr'] = C_river[0] * Qr
            df.loc[tt,'Fin'] = C_ocean[0] * Qin[-1]
            df.loc[tt,'Fout'] = -(C_top[-1] * Qout[-1])

        C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)

    C_bot_dict[W] = C_bot
    C_top_dict[W] = C_top

    Cnet = df.Cnet.to_numpy()
    tt_sec = df.index.to_numpy()*86400
    dCnet_dt = (Cnet[2:]-Cnet[:-2])/(tt_sec[2:]-tt_sec[:-2])
    df['dCnet_dt'].iloc[1:-1] = dCnet_dt
    df.loc[:,'Error'] = df.dCnet_dt - (df.Fr + df.Fin + df.Fout)

    df.Cmean = df.Cnet/V

    budget_dict[W] = df
    
    print('W=%0.2f, W*dt/H_top=%0.2f, C_bot[1]=%0.2f' %
        (W,(W*dt/86400)/H_top, C_bot[1]))

# Plotting final state vs. x

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

fig.tight_layout()
pfun.end_plot()
plt.show()

out_fn = Ldir['parent'] / 'LPM_output' / 'reflux'/ 'er_sink_range1.png'
Lfun.make_dir(out_fn.parent)
fig.savefig(out_fn)

# Plotting budget time series

pfun.start_plot()
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)

for W in W_list:
    df = budget_dict[W]
    df.plot(y=['Cmean'],ax=ax,grid=True,linewidth=3,label=[round(W/W_er_mpd,2)])
    ax.set_xlabel('Time [days]')
ax.set_title('Mean Tracer Concentration vs. Time')

fig.tight_layout()
pfun.end_plot()
plt.show()

out_fn = Ldir['parent'] / 'LPM_output' / 'reflux'/ 'er_sink_range2.png'
Lfun.make_dir(out_fn.parent)
fig.savefig(out_fn)

