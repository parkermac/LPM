"""
Code to run the efflux-reflux model with NPZD variables.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from lo_tools import plotting_functions as pfun
import er_fun
import npzd_equations as npzde
from importlib import reload
reload(er_fun)
reload(npzde)

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

# NPZD model
# Note that the time is always in units of days for the NPZD model, whereas
# time is seconds for the physical circulation.
#
# intial conditions, all [mmol N m-3]
v_top = dict()
v_top['Phy'] = 0.01 * np.ones(N_boxes)
v_top['Zoo'] = 0.1 * v_top['Phy'].copy()
v_top['SDet'] = 0 * np.ones(N_boxes)
v_top['LDet'] = 0 * np.ones(N_boxes)
v_top['NO3'] = 20 * np.ones(N_boxes)
v_top['NH4'] = 0 * np.ones(N_boxes)
vn_list = list(v_top.keys())
v_bot = v_top.copy()
#
E = 100 # PAR for upper layer [W m-2]
dt_days = dt/86400

print('dt_days = %0.2f' % (dt_days))
print('nt = %d' % (nt))
print('total time i days = %0.1f' % (nt * dt /86400))
print('W_er [m d-1] = %0.2f' % (W_er*86400))

sink_fac = 4
sink_dist = dt * sink_fac * W_er # [m]
print('H_top = %0.1f, H_bot = %0.1f, sink_dist = %0.1f [m]' % (H_top,H_bot,sink_dist))

df_mean_top = pd.DataFrame(columns = vn_list)
df_mean_bot = pd.DataFrame(columns = vn_list)

for ii in range(nt):

    if np.mod(ii,10) == 0:
        for vn in vn_list:
            df_mean_top.loc[ii*dt_days,vn] = np.mean(v_top[vn])
            df_mean_bot.loc[ii*dt_days,vn] = np.mean(v_bot[vn])

    # advection step
    for vn in vn_list:
        C_top = v_top[vn].copy()
        C_bot = v_bot[vn].copy()
        if vn == 'NO3':
            if True: 
                source_str = 'River N Source'
                C_river = np.array([10])
                C_ocean = np.array([0])
            else:
                source_str = 'Ocean N Source'
                C_river = np.array([0])
                C_ocean = np.array([10])
        else:
            C_river = np.array([0])
            C_ocean = np.array([0])
        if vn == 'SDet':
            QQ_sink = sink_fac * Q_sink/10
            # vertical flux due to sinking
            S_sink = C_bot * QQ_sink * dt / V_bot
        elif vn == 'LDet':
            QQ_sink = sink_fac * Q_sink
            # vertical flux due to sinking
            L_sink = C_bot * QQ_sink * dt / V_bot
        else:
            QQ_sink = 0 * Q_sink

        C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean,
         alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=QQ_sink)

        v_top[vn] = C_top
        v_bot[vn] = C_bot   
                 
    # npzd step
    v_top = npzde.update_v(v_top, E, dt_days)
    v_bot = npzde.update_v(v_bot, 0, dt_days)
    # account for benthic remineralization
    v_bot['SDet'] -= S_sink
    v_bot['LDet'] -= L_sink
    v_bot['NH4'] += S_sink + L_sink

df_top = pd.DataFrame(index=XB,columns=vn_list,data=v_top)
df_bot = pd.DataFrame(index=XB,columns=vn_list,data=v_bot)

plt.close('all')
pfun.start_plot(figsize=(12,8))
lw = 3

# spatial structure at the end

fig = plt.figure()

ax = fig.add_subplot(211)
df_top.plot(ax=ax,linewidth=lw)
ax.set_title(source_str)
ax.text(.5,.9,'Top Layer',ha='center',transform=ax.transAxes)

ax = fig.add_subplot(212)
df_bot.plot(ax=ax,linewidth=lw, legend=False)
ax.set_xlabel('Along Channel Distance [km]')
ax.text(.5,.9,'Bottom Layer',ha='center',transform=ax.transAxes)

# time evolution of mean values

fig = plt.figure()

ax = fig.add_subplot(211)
df_mean_top.plot(ax=ax)
ax.set_title(source_str)
ax.text(.5,.9,'Top Layer',ha='center',transform=ax.transAxes)

ax = fig.add_subplot(212)
df_mean_bot.plot(ax=ax,legend=False)
ax.set_xlabel('Time [days]')
ax.text(.5,.9,'Bottom Layer',ha='center',transform=ax.transAxes)
