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
    Qout = Qr * Sout / DS = Qr at the head, as desired.

    """
    N_edges = N_boxes + 1
    a = Sbar_0/(L**1.5)
    alpha = DS_0/L
    x = np.linspace((alpha/(2*a))**2,L,N_edges)
    Sin = a*x**1.5 + alpha*x/2
    Sout = a*x**1.5 - alpha*x/2
    return Sin, Sout, x, L

def a_calc(Qin, Qout, Sin, Sout):
    
    Q1 = Qout[1:]
    q1 = Qin[1:]
    q2 = Qout[:-1]
    Q2 = Qin[:-1]
    
    S1 = Sout[1:]
    s1 = Sin[1:]
    s2 = Sout[:-1]
    S2 = Sin[:-1]
    
    Q_efflux = Q1 * (S1 - s2) / (s1 - s2)
    Q_reflux = Q2 * (s1 - S2) / (s1 - s2)
    
    return Q_efflux, Q_reflux

# Estuary scalar parameters
Qr = 300    # River Transport [m3 s-1]
B = 3e3     # width [m]
H_top = 20     # thickness of top layer [m]
H_bot = 20     # thickness of bottom layer [m]

# Get the solution at box edges
Sbar_0 = 30
DS_0 = 5
N_boxes = 1000
L = 50e3
Sin, Sout, x, L = get_Sio_chatwin(Sbar_0, DS_0, N_boxes, L)
DS = Sin - Sout

# Calculate transports using steady Knudsen blance (sign convention
# used here is that all transports are positive)
Qout = Qr*Sin/DS
Qin = Qr*Sout/DS

# Efflux-Reflux parameters
Q_efflux, Q_reflux = a_calc(Qin, Qout, Sin, Sout)

# calculate vertical velocities in each box
dx = np.diff(x)
DA = B * dx
W_efflux = Q_efflux / DA
W_reflux = Q_reflux / DA


# Make x-axes for plotting
X = x/1e3   # box edges [km]
xb = x[:-1] + dx/2
XB = xb/1e3 # box centers[km]

# plotting
plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize=(14,12))

ax = fig.add_subplot(311)
ax.plot(X, Sin, '-r', label='Sin')
ax.plot(X, Sout, '-b', label='Sout')
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
ax.plot(XB, W_efflux * sec_per_day, '-r', label='W_efflux [m/day]')
ax.plot(XB, W_reflux * sec_per_day, '-b', label='W_reflux [m/day]')
ax.set_xlim(0, X[-1])
ax.set_ylim(bottom=0)
ax.grid(True)
ax.legend(loc='lower right')
ax.set_xlabel('X [km]')

ax.text(.2, .5, 'Number of boxes = %d' % (N_boxes), transform=ax.transAxes)
ax.text(.2, .4, 'Net Efflux / Qin[mouth] = %0.1f' % (Q_efflux.sum() / Qin[-1]), transform=ax.transAxes)
ax.text(.2, .3, 'Net Reflux / Qout[mouth] = %0.1f' % (Q_reflux.sum() / Qout[-1]), transform=ax.transAxes)


pfun.end_plot()
plt.show()

