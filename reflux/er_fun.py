"""
Efflux-Reflux utility functions
"""

import numpy as np

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
    
    Q_efflux = alpha_efflux * q1
    Q_reflux = alpha_reflux * q0
    
    return alpha_efflux, alpha_reflux, Q_efflux, Q_reflux