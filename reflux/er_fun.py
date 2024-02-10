"""
Efflux-Reflux utility functions
"""

import numpy as np
import sys

def get_params(Qr=1e3, B=3e3, H_top=20, H_bot=20, Sbar_0=30, DS_0=5,
    N_boxes=100, L=50e3, etype='chatwin'):
    """
    This is the primary function for getting all the variables used for a box
    model time integration.
    """

    # Estuary physical parameters
    # Qr =  river transport [m3 s-1]
    # B = width [m]
    # H_top = thickness of top layer [m]
    # H_bot = thickness of bottom layer [m]

    # Sbar_0 = mean salinity at mouth [g kg-1] 
    # DS_0 = Sin - Sout at mouth [g kg-1]
    # N_boxes = number of along-channel grid boxes
    # L = length of channel [m]

    # Create the solution at box edges
    if etype == 'chatwin':
        Sin, Sout, x, L = get_Sio_chatwin(Sbar_0, DS_0, N_boxes, L)
    elif etype == 'hr':
        Sin, Sout, x, L = get_Sio_hr(Sbar_0, DS_0, N_boxes, L)

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
    V = np.sum(V_top) + np.sum(V_bot[1:]) # total active channel volume [m3]

    # Calculate transports using steady Knudsen balance
    # (sign convention used here is that all transports are positive)
    Qout = Qr*Sin/DS
    Qin = Qr*Sout/DS

    # Efflux-Reflux parameters
    alpha_efflux, alpha_reflux, Q_efflux, Q_reflux = alpha_calc(Qin, Qout, Sin, Sout)

    # Calculate vertical velocities in each box
    W_efflux = Q_efflux / DA
    W_reflux = Q_reflux / DA
    # and full integrals
    Net_efflux = Q_efflux.sum()
    Net_reflux = Q_reflux.sum()

    # Try out the "continuous function" version of the vertical transports.
    Q_efflux_alt = np.diff(Sout) * Qout[1:] / DS[1:]
    Q_reflux_alt = np.diff(Sin) * Qin[:-1] / DS[:-1]
    # Note: if we retain the full denominator this pretty closely matches the non-alt
    # versions, as it should. But these are sensitive to N_boxes.
    Net_efflux_alt = Q_efflux_alt.sum()
    Net_reflux_alt = Q_reflux_alt.sum()
    W_efflux_alt = Q_efflux_alt / DA
    W_reflux_alt = Q_reflux_alt / DA

    # Estimate max dt for stability
    dt = 0.9 * np.min((np.min(V_top/Qout[1:]), np.min(V_bot/Qin[1:])))

    # Estimate flushing time
    T_flush = V / Qout[-1]

    phys_tup = (Qr, B, H_top, H_bot, Sbar_0, DS_0, N_boxes, L, etype)
    sol_tup = (Sin, Sout, Qin, Qout, x, DS, dx, DA, X, xb, XB, V_top, V_bot, V)
    er1_tup = (alpha_efflux, alpha_reflux)
    er2_tup = (Q_efflux, Q_reflux, W_efflux, W_reflux, Net_efflux, Net_reflux)
    er3_tup = (Q_efflux_alt, Q_reflux_alt, W_efflux_alt, W_reflux_alt, Net_efflux_alt, Net_reflux_alt)
    t_tup = (dt, T_flush)

    return phys_tup, sol_tup, er1_tup, er2_tup, er3_tup, t_tup

def get_Sio_chatwin(Sbar_0, DS_0, N_boxes, L):
    """
    Function to create Sin and Sout for the Chatwin solution.
    All fields defined at the box edges.
    
    S increases toward positive x.
    
    Sbar_0 is (Sin + Sout)/2 at the mouth
    DS_0 is (Sin - Sout) at the mouth
    N_boxes is the number of boxes
    L is the nominal estuary length [m]
    
    Note that the actual length is a bit less than L because of
    how we formulate the solution to force Sout = 0 at the head.
    This ensures that Sin = DS at the head, and so Knudsen gives
    Qout = Qr * Sin / DS = Qr at the head, as desired.
    """
    N_edges = N_boxes + 1
    a = Sbar_0/(L**1.5)
    b = DS_0/L
    x = np.linspace((b/(2*a))**2,L,N_edges)
    Sin = a*x**1.5 + b*x/2
    Sout = a*x**1.5 - b*x/2
    return Sin, Sout, x, L

def get_Sio_hr(Sbar_0, DS_0, N_boxes, L):
    """
    Like the HR65 Central Regime solution
    """
    N_edges = N_boxes + 1
    a = Sbar_0/L
    b = DS_0/L
    x = np.linspace(0,L,N_edges)
    Sin = a*x + DS_0
    Sout = a*x
    return Sin, Sout, x, L

def alpha_calc(Qin, Qout, Sin, Sout):
    """
    Calculate alphas for all boxes.
    """
    Q1 = Qout[1:]
    q1 = Qin[1:]
    q0 = Qout[:-1]
    Q0 = Qin[:-1]
    
    S1 = Sout[1:]
    s1 = Sin[1:]
    s0 = Sout[:-1]
    S0 = Sin[:-1]
    
    alpha_efflux = (Q1 / q1) * (S1 - s0) / (s1 - s0)
    alpha_reflux = (Q0 / q0) * (s1 - S0) / (s1 - s0)

    # check that alpha values at the head are correct
    if np.abs(alpha_efflux[0]-1) > 1e-6:
        print('Error: alpha_efflux[0] must be very close to 1')
        sys.exit()
    if np.abs(alpha_reflux[0]) > 1e-6:
        print('Error: alpha_reflux[0] must be very close to 0')
        sys.exit()
    
    Q_efflux = alpha_efflux * q1
    Q_reflux = alpha_reflux * q0
    
    return alpha_efflux, alpha_reflux, Q_efflux, Q_reflux
    
def box_model(C_bot, C_top, C_river, C_ocean, alpha_efflux, alpha_reflux, V_top, V_bot, dt, Qin, Qout, Q_sink=0, T_decay_inv=0):
    """
    Box model integrator, for a single time 
    """
    # check that the sinking is not too fast
    if dt*np.max(Q_sink) >= np.min(V_top):
        print('Error: sinking will lose more than upper layer volume!')
        sys.exit()
    top_upstream = np.concatenate((C_river, C_top[:-1]))
    bot_upstream = np.concatenate((C_bot[1:], C_ocean))
    sink = C_top*Q_sink
    # force sink = 0 in the first box because the bottom cell there is
    # not active
    sink[0] = 0
    C_top = C_top + (dt/V_top)*((1 - alpha_reflux)*top_upstream*Qout[:-1]
        + alpha_efflux*bot_upstream*Qin[1:]
        - C_top*Qout[1:]
        - sink) - dt*C_top*T_decay_inv
    C_bot = C_bot + (dt/V_bot)*((1 - alpha_efflux)*bot_upstream*Qin[1:]
        + alpha_reflux*top_upstream*Qout[:-1]
        - C_bot*Qin[:-1]
        + sink) - dt*C_bot*T_decay_inv
    C_bot[0] = np.nan # first bottom cell not active, so mask
    
    return C_bot, C_top