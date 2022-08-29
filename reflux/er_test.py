"""
Code to explore Efflux-Reflux theory.
"""

import numpy as np
import matplotlib.pyplot as plt

from lo_tools import plotting_functions as pfun

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

def alpha_calc(Qin, Qout, Sin, Sout):
    # calculate alphas for all boxes
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
    
    Q_efflux = alpha_efflux * q1
    Q_reflux = alpha_reflux * q0
    
    return alpha_efflux, alpha_reflux, Q_efflux, Q_reflux

# Estuary physical parameters
Qr = 300    # River Transport [m3 s-1]
B = 3e3     # width [m]
H_top = 20  # thickness of top layer [m]
H_bot = 20  # thickness of bottom layer [m]

# Create the solution at box edges
Sbar_0 = 30
DS_0 = 5
N_boxes = 1000
L = 50e3
Sin, Sout, x, L = get_Sio_chatwin(Sbar_0, DS_0, N_boxes, L)
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

# Calculate transports using steady Knudsen blance (sign convention
# used here is that all transports are positive)
Qout = Qr*Sin/DS
Qin = Qr*Sout/DS

# Efflux-Reflux parameters
alpha_efflux, alpha_reflux, Q_efflux, Q_reflux = alpha_calc(Qin, Qout, Sin, Sout)

# Calculate vertical velocities in each box
W_efflux = Q_efflux / DA
W_reflux = Q_reflux / DA

# Try out the "continuous function" version of the vertical transports.
Q_efflux_alt = np.diff(Sout) * Qout[1:] / DS[1:]
Q_reflux_alt = np.diff(Sin) * Qin[:-1] / DS[:-1]
# Note: if we retain the full denominator this pretty closely matches the non-alt
# versions, as it should. But these are sensitive to N_boxes.
Net_Efflux = Q_efflux_alt.sum()
Net_Reflux = Q_reflux_alt.sum()
W_efflux_alt = Q_efflux_alt / DA
W_reflux_alt = Q_reflux_alt / DA
# Result: These match Q_efflux.sum() and Q_reflux.sum() quite well for N_boxes = 10000.
# Curiously, they seem to be extremely insensitive to N_boxes, varying by about 1% over
# the range N_boxes = 10 to 10000!
# In contrast the estimates from Q_efflux.sum() and Q_reflux.sum() require
# N_boxes >= 1000 to be any good. Interesting.

# Box model integrator
#
# Initial condition
C_top = np.zeros(N_boxes)
C_bot = np.zeros(N_boxes)

# Boundary conditions
# This mimics salinity
C_river = np.zeros(1)
C_ocean = Sin[-1]*np.ones(1)
# This is a river tracer
# C_river = 10 * np.ones(1)
# C_ocean = np.zeros(1)

# Estimate max dt for stability
dt = 0.9 * np.min((np.min(V_top/Qout[1:]), np.min(V_bot/Qin[1:])))
# Run for a specified number of flushing times
T_flush = V / Qout[-1]
nt = 10 * int(T_flush / dt)

# Integrate over time
for ii in range (nt):
    top_upstream = np.concatenate((C_river, C_top[:-1]))
    bot_upstream = np.concatenate((C_bot[1:], C_ocean))
    C_top = C_top + (dt/V_top)*((1 - alpha_reflux)*top_upstream*Qout[:-1]
        + alpha_efflux*bot_upstream*Qin[1:]
        - C_top*Qout[1:])
    C_bot = C_bot + (dt/V_bot)*((1 - alpha_efflux)*bot_upstream*Qin[1:]
        + alpha_reflux*top_upstream*Qout[:-1]
        - C_bot*Qin[:-1])
    C_bot[0] = C_bot[1] # a little nudge for the bottom box at the head

# Plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(14,12))

ax = fig.add_subplot(311)
ax.plot(X, Sin, '-r', label='Sin')
ax.plot(X, Sout, '-b', label='Sout')
ax.plot(X, DS, '-', color='orange', label=r'$\Delta S$')
ax.plot(XB, C_bot, '--r', label='C_bot')
ax.plot(XB, C_top, '--b', label='C_top')
ax.plot(XB, C_bot - C_top, '--', color='orange', label=r'$\Delta C$')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='upper left')
ax.set_title('Efflux-Reflux in the Chatwin Solution')

ax = fig.add_subplot(312)
ax.plot(X, Qin/Qr, '-r', label='Qin/Qr')
ax.plot(X, Qout/Qr, '-b', label='Qout/Qr')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='upper left')

ax = fig.add_subplot(313)
sec_per_day = 86400
ax.plot(XB, W_efflux * sec_per_day, '--r', label='W_efflux [m/day]')
ax.plot(XB, W_reflux * sec_per_day, '--b', label='W_reflux [m/day]')
ax.plot(XB, W_efflux_alt * sec_per_day, ':r', label='W_efflux_alt [m/day]')
ax.plot(XB, W_reflux_alt * sec_per_day, ':b', label='W_reflux_alt [m/day]')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='lower right')
ax.set_xlabel('X [km]')

ax.text(.2, .5, 'Number of boxes = %d' % (N_boxes), transform=ax.transAxes)
ax.text(.2, .4, 'Net Efflux / Qin_mouth = %0.1f (alt %0.1f)' %
    (Q_efflux.sum() / Qin[-1], Net_Efflux / Qin[-1]), transform=ax.transAxes)
ax.text(.2, .3, 'Net Reflux / Qout_mouth = %0.1f (alt %0.1f)' %
    (Q_reflux.sum() / Qout[-1], Net_Reflux / Qout[-1]), transform=ax.transAxes)

pfun.end_plot()
plt.show()

