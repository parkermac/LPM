"""
Code to run the efflux-reflux model with NPZD variables.

This is based on npzd0 but starts comparing different runs.
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

# Estuary physical parameters
Qr = 300    # River Transport [m3 s-1]
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
W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2 # [m s-1]
Q_sink = W_er * DA # [m3 s-1]

# Estimate max dt for stability
dt = 0.9 * np.min((np.min(V_top/Qout[1:]), np.min(V_bot/Qin[1:])))
dt_days = dt/86400
# Run for a specified number of flushing times
T_flush = V / Qout[-1]
nt = 10 * int(T_flush / dt)

# initialize arrays
# intial conditions, all [mmol N m-3], except Chl which is [mg Chl m-3]
v_top = dict()
v_top['Phy'] = 0.01 * np.ones(N_boxes)
v_top['Zoo'] = 0.1 * v_top['Phy'].copy()
v_top['SDet'] = 0 * np.ones(N_boxes)
v_top['LDet'] = 0 * np.ones(N_boxes)
v_top['NO3'] = 20 * np.ones(N_boxes)
v_top['NH4'] = 0 * np.ones(N_boxes)
#
v_bot = v_top.copy()

E = 100 # [W m-2]

vn_list = list(v_top.keys())

print('dt_days = %0.2f' % (dt_days))
print('nt = %d' % (nt))
print('total time i days = %0.1f' % (nt * dt /86400))
print('W_er [m d-1] = %0.2f' % (W_er*86400))

plt.close('all')
pfun.start_plot(figsize=(12,8))
lw = 3
fig = plt.figure()
ymax = 40
sink_fac = 1

sink_dist = dt * sink_fac * W_er # [m]
print('H_top = %0.1f, H_bot = %0.1f, sink_dist = %0.1f [m]' % (H_top,H_bot,sink_dist))

for source in ['river','ocean']:

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
                if source == 'river': 
                    source_str = 'River N Source'
                    C_river = np.array([10])
                    C_ocean = np.array([0])
                    col = 1
                elif source == 'ocean':
                    source_str = 'Ocean N Source'
                    C_river = np.array([0])
                    C_ocean = np.array([10])
                    col = 2
            else:
                C_river = np.array([0])
                C_ocean = np.array([0])
            if vn == 'SDet':
                QQ_sink = sink_fac * Q_sink/10
            elif vn == 'LDet':
                QQ_sink = sink_fac * Q_sink
            else:
                QQ_sink = 0 * Q_sink

            C_bot, C_top = er_fun.box_model(C_bot, C_top, C_river, C_ocean,
            alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=QQ_sink)

            v_top[vn] = C_top
            v_bot[vn] = C_bot   
                    
        # npzd step
        v_top = npzde.update_v(v_top, E, dt_days)
        v_bot = npzde.update_v(v_bot, 0, dt_days)

        # benthic remineralization
        this_sink = v_top['LDet'] * QQ_sink * dt

    df_top = pd.DataFrame(index=XB,columns=vn_list,data=v_top)
    df_bot = pd.DataFrame(index=XB,columns=vn_list,data=v_bot)

    # spatial structure at the end
    ax = fig.add_subplot(2,2,col)
    df_top.plot(ax=ax,linewidth=lw)
    ax.set_title(source_str)
    ax.set_ylim(0,ymax)
    ax.grid(True)
    ax.text(.05,.9,'Top Layer', transform=ax.transAxes, bbox=pfun.bbox)

    ax = fig.add_subplot(2,2,col+2)
    df_bot.plot(ax=ax,linewidth=lw)
    ax.set_xlabel('Along Channel Distance [km]')
    ax.set_ylim(0,ymax)
    ax.grid(True)
    ax.text(.05,.9,'Bottom Layer', transform=ax.transAxes, bbox=pfun.bbox)

