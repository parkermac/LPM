"""
Code to test conservation and accumulation of a sinking tracer.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

# Form an average for scaling of sinking
W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2
Q_sink = W_er * DA

# initialize a DataFrame to hold budget time series
df = pd.DataFrame(columns=['Cnet','Fr','Fin','Fout','dCnet_dt','Error'])

# Box model integrator
# Initial condition
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)
# Boundary conditions
# River source
C_river = np.ones(1)
C_ocean = np.zeros(1)
# Run for a specified number of flushing times
nt = 10 * int(T_flush / dt)
# Integrate over time
for ii in range (nt):

    if np.mod(ii,10) == 0:
        tt = ii*dt
        df.loc[tt,'Cnet'] = np.nansum(C_top*V_top) + np.nansum(C_bot*V_bot)
        df.loc[tt,'Fr'] = C_river[0] * Qr
        df.loc[tt,'Fin'] = C_ocean[0] * Qin[-1]
        df.loc[tt,'Fout'] = -(C_top[-1] * Qout[-1])

    C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean,
        alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=Q_sink)

Cnet = df.Cnet.to_numpy()
tt = df.index.to_numpy()
dCnet_dt = (Cnet[2:]-Cnet[:-2])/(tt[2:]-tt[:-2])
df['dCnet_dt'].iloc[1:-1] = dCnet_dt
df.loc[:,'Error'] = df.dCnet_dt - (df.Fr + df.Fin + df.Fout)

# Plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
df.plot(y=['dCnet_dt','Fr','Fin','Fout','Error'],ax=ax,grid=True,linewidth=3)

pfun.end_plot()
plt.show()