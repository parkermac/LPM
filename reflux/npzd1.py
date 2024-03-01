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

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# ======================================================================

# Choices
sink_fac_list = [0,1,4]
choice_dict = dict()

for sink_fac in sink_fac_list:

    out_dict = dict()

    source = 'river' # river or ocean
    etype = 'chatwin' # chatwin or hr

    # ----------------------------------------------------------------------

    # create the physical solution
    phys_tup, sol_tup, er1_tup, er2_tup, er3_tup, t_tup = er_fun.get_params(etype=etype)
    # unpacking
    Qr, B, H_top, H_bot, Sbar_0, DS_0, N_boxes, L, etype = phys_tup
    Sin, Sout, Qin, Qout, x, DS, dx, DA, X, xb, XB, V_top, V_bot, V = sol_tup
    alpha_efflux, alpha_reflux = er1_tup
    Q_efflux, Q_reflux, W_efflux, W_reflux, Net_efflux, Net_reflux = er2_tup
    Q_efflux_alt, Q_reflux_alt, W_efflux_alt, W_reflux_alt, Net_efflux_alt, Net_reflux_alt = er3_tup
    dt, T_flush = t_tup

    # Run for a specified number of flushing times
    nt = 40 * int(T_flush / dt)
    dt_days = dt/86400 # used by npzde.update_v() 

    # Form an average for scaling of sinking
    W_er = (W_efflux_alt.mean() + W_reflux_alt.mean())/2 # [m s-1]
    Q_sink = W_er * DA

    if True:
        print('')
        sink_dist = dt * sink_fac * W_er
        # sinking distance in one time step (must be less than layer thickness) [m]
        print('dt_days = %0.2f, nt = %d, total time in days = %0.1f' % (dt_days, nt, nt * dt / 86400))
        print('W_er = %0.2f, sink_fac*W_er %0.2f [m d-1]' % (W_er*86400, sink_fac*W_er*86400))
        print('H_top = %0.1f, H_bot = %0.1f, sink_dist = %0.1f [m]' % (H_top,H_bot,sink_dist))

    # NPZD model
    # Note that the time is always in units of days for the NPZD model, whereas
    # time is seconds for the physical circulation.
    #
    # intial conditions, all [mmol N m-3] which is the same as [uM]
    v_top = dict()
    v_top['Phy'] = 0.01 * np.ones(N_boxes)
    v_top['Zoo'] = 0.1 * v_top['Phy'].copy()
    v_top['SDet'] = 0 * np.ones(N_boxes)
    v_top['LDet'] = 0 * np.ones(N_boxes)
    v_top['NO3'] = 0 * np.ones(N_boxes)
    v_top['NH4'] = 0 * np.ones(N_boxes)
    v_top['oxy'] = 300 * np.ones(N_boxes) # [mmol O2 m-3]
    vn_list = list(v_top.keys())
    v_bot = v_top.copy()
    #
    E = 100 # PAR for upper layer [W m-2]

    # initialize a dict to hold budget time series for each NPZD variable
    budget_dict = dict()
    for vn in vn_list:
        # initialize a DataFrame to hold budget time series
        df = pd.DataFrame(columns=['Cnet','Cmean','Fr','Fin','Fout','dCnet_dt','Error'])
        budget_dict[vn] = df

    # initialize DataFrames to accumulate time series of layer-mean tracer values
    df_mean_top = pd.DataFrame(columns = vn_list)
    df_mean_bot = pd.DataFrame(columns = vn_list)

    for ii in range(nt):

        if np.mod(ii,10) == 0:
            for vn in vn_list:
                df_mean_top.loc[ii*dt_days,vn] = np.mean(v_top[vn])
                df_mean_bot.loc[ii*dt_days,vn] = np.nanmean(v_bot[vn])

        # advection step
        for vn in vn_list:
            C_top = v_top[vn].copy()
            C_bot = v_bot[vn].copy()

            if vn == 'NO3':
                if source == 'river': 
                    source_str = 'River N Source'
                    C_river = np.array([10])
                    C_ocean = np.array([0])
                elif source == 'ocean':
                    source_str = 'Ocean N Source'
                    C_river = np.array([0])
                    C_ocean = np.array([10])
                else:
                    print('Error: Check source definition.')
                    sys.exit()
            elif vn == 'oxy':
                C_river = np.array([300])
                C_ocean = np.array([100])
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
            elif vn == 'oxy':
                Oxy_air_flux_sum = npzde.airsea_oxygen(C_top, dt_days, DA)
                DO_change = Oxy_air_flux_sum / V_top
            else:
                QQ_sink = 0 * Q_sink

            if np.mod(ii,10) == 0:
                tt = ii*dt/86400 # use time in days for the index
                df = budget_dict[vn]
                df.loc[tt,'Cnet'] = np.nansum(C_top*V_top) + np.nansum(C_bot*V_bot)
                df.loc[tt,'Fr'] = C_river[0] * Qr
                df.loc[tt,'Fin'] = C_ocean[0] * Qin[-1]
                df.loc[tt,'Fout'] = -(C_top[-1] * Qout[-1])

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
        v_bot['oxy'] -= (106/16) * (S_sink + L_sink)
        # account for air-sea oxygen transport
        v_top['oxy'] += DO_change

    df_top = pd.DataFrame(index=XB,columns=vn_list,data=v_top)
    df_bot = pd.DataFrame(index=XB,columns=vn_list,data=v_bot)

    for vn in vn_list:
        df = budget_dict[vn]
        Cnet = df.Cnet.to_numpy()
        tt_sec = df.index.to_numpy()*86400
        dCnet_dt = (Cnet[2:]-Cnet[:-2])/(tt_sec[2:]-tt_sec[:-2])
        df['dCnet_dt'].iloc[1:-1] = dCnet_dt
        df.loc[:,'Error'] = df.dCnet_dt - (df.Fr + df.Fin + df.Fout)
        df.Cmean = df.Cnet/V

    # make a DataFrame for the budget time series for Total N
    vn_list_short = [item for item in vn_list if item != 'oxy']
    for vn in vn_list_short:
        if vn == vn_list[0]:
            df_net = budget_dict[vn].copy()
        else:
            df_net = df_net + budget_dict[vn]
    # ======================================================================

    out_dict['df_top'] = df_top
    out_dict['df_bot'] = df_bot

    choice_dict[sink_fac] = out_dict

# plotting
plt.close('all')
pfun.start_plot(fs=20, figsize=(14,8))
fig = plt.figure()
lw=3
ymax = 12

ii = 1
for sink_fac in sink_fac_list:
    df_top = (choice_dict[sink_fac])['df_top']
    df_bot = (choice_dict[sink_fac])['df_bot']

    # simplifications for plotting
    df_top['Det'] = df_top['LDet'] + df_top['SDet']
    df_bot['Det'] = df_bot['LDet'] + df_bot['SDet']
    vn_list_shorter = ['Phy','NO3','NH4','Det']

    ax = fig.add_subplot(2,3,ii)
    if ii == 1:
        df_top.plot(y=vn_list_shorter,ax=ax,linewidth=lw, legend=True)
        ax.set_ylabel('[mmol N m-3]')
    else:
        df_top.plot(y=vn_list_shorter,ax=ax,linewidth=lw, legend=False)
    ax.set_title('$W_{sink}/W_{mix}$ = %0.2f' % (sink_fac))
    ax.text(.05,.9,'Top Layer',ha='left',transform=ax.transAxes,bbox=pfun.bbox)
    ax.set_xlim(0,X[-1])
    ax.set_ylim(0,ymax)
    ax.grid(True)

    ax = fig.add_subplot(2,3,ii+3)
    df_bot.plot(y=vn_list_shorter,ax=ax,linewidth=lw, legend=False)
    ax.set_xlabel('Along Channel Distance [km]')
    if ii == 1:
        ax.set_ylabel('[mmol N m-3]')
    ax.text(.05,.9,'Bottom Layer',ha='left',transform=ax.transAxes,bbox=pfun.bbox)
    ax.set_xlim(0,X[-1])
    ax.set_ylim(0,ymax)
    ax.grid(True)

    ii += 1

fig.tight_layout()
plt.show()
pfun.end_plot()

out_fn = Ldir['parent'] / 'LPM_output' / 'reflux'/ 'npzd1.png'
Lfun.make_dir(out_fn.parent)
fig.savefig(out_fn)
